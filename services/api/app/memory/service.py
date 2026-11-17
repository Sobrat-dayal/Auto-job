"""Central Memory Service coordinating write pipelines, search, embeddings, lifecycle, and authorization."""

from datetime import UTC, datetime
import logging
import time
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db_session
from app.memory.contracts import (
    ContextBuildRequest,
    ContextBuildResponse,
    MemoryCreateRequest,
    MemoryRecordResponse,
    MemoryScope,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryType,
    ProvenanceMetadata,
    SearchMode,
    SensitivityCategory,
    VerificationStatus,
)
from app.memory.embeddings.registry import embedding_registry
from app.memory.lifecycle.conflicts import conflict_resolver
from app.memory.lifecycle.consolidation import memory_consolidator
from app.memory.lifecycle.deduplication import deduplication_service
from app.memory.lifecycle.deletion import deletion_coordinator
from app.memory.lifecycle.export import export_service
from app.memory.retrieval.context_builder import context_builder
from app.memory.retrieval.hybrid import hybrid_retrieval_engine
from app.memory.storage.fts_index import fts_index_manager
from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import vector_store

logger = logging.getLogger("autonom.memory.service")


class MemoryService:
    """Unified service facade for persistent agent memory, embeddings, and hybrid retrieval."""

    def __init__(self) -> None:
        self.embedding_registry = embedding_registry
        self.vector_store = vector_store
        self.fts_index = fts_index_manager
        self.retrieval_engine = hybrid_retrieval_engine
        self.context_builder = context_builder
        self.dedup_service = deduplication_service
        self.conflict_resolver = conflict_resolver
        self.consolidator = memory_consolidator
        self.deletion_coordinator = deletion_coordinator
        self.export_service = export_service
        self._is_initialized = False

    async def initialize(self) -> None:
        """Warms up in-memory vector index from persistent SQLite records."""
        if self._is_initialized:
            return

        try:
            async with get_db_session() as session:
                repo = MemoryRepository(session)
                pairs = await repo.load_all_active_embeddings()
                loaded = 0
                for mem_rec, emb_rec in pairs:
                    ok = self.vector_store.upsert(
                        memory_id=mem_rec.id,
                        embedding=emb_rec.vector_json,
                        model_id=emb_rec.embedding_model_id,
                        owner_scope=mem_rec.owner_scope,
                        scope_id=mem_rec.scope_id,
                    )
                    if ok:
                        loaded += 1
                logger.info(f"MemoryService initialized: loaded {loaded} vectors into index.")
                self._is_initialized = True
        except Exception as exc:
            logger.warning(f"MemoryService index warm-up encountered an issue: {exc}")

    async def write_memory(
        self,
        request: MemoryCreateRequest,
        actor_id: str = "user",
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> MemoryRecordResponse:
        """Executes full write pipeline: deduplication, conflict check, persistence, vector embedding, and FTS indexing."""
        async with get_db_session() as session:
            repo = MemoryRepository(session)

            # 1. Deduplication check
            checksum = self.dedup_service.compute_checksum(request.content)
            existing_id = await self.dedup_service.find_exact_duplicate(session, request.content, request.scope_id)
            if existing_id:
                logger.info(f"Exact duplicate memory detected ('{existing_id}'); updating access timestamp.")
                await repo.touch_accessed(existing_id)
                rec = await repo.get_memory_by_id(existing_id)
                return self._to_response(rec)

            # 2. Conflict detection check
            await self.conflict_resolver.detect_conflict(
                session=session,
                new_title=request.title,
                new_content=request.content,
                scope_id=request.scope_id,
            )

            # 3. Privacy & Egress validation
            active_model = self.embedding_registry.get_active_provider().model_id
            if not self.embedding_registry.validate_egress(request.sensitivity_category, active_model):
                logger.warning("Data egress policy restricted embedding generation for sensitive content.")
                request.generate_embedding = False

            # 4. Persist primary record
            prov_dict = request.provenance.model_dump() if request.provenance else {
                "source_type": request.source_type,
                "source_ref": request.source_ref,
                "author": actor_id,
                "workflow_id": workflow_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            rec = await repo.create_memory(
                memory_type=request.memory_type.value,
                title=request.title,
                content=request.content,
                summary=request.summary or request.content[:200],
                owner_scope=request.owner_scope.value,
                scope_id=request.scope_id,
                source_type=request.source_type,
                source_ref=request.source_ref,
                provenance_json=prov_dict,
                verification_status=request.verification_status.value,
                confidence_category=request.confidence_category.value,
                sensitivity_category=request.sensitivity_category.value,
                visibility_policy=request.visibility_policy.value,
                content_checksum=checksum,
                retention_policy=request.retention_policy.value,
                embedding_model_id=active_model,
                metadata_json=request.metadata,
            )

            # 5. Generate and store vector embedding
            if request.generate_embedding:
                try:
                    provider = self.embedding_registry.get_active_provider()
                    embedding_vec = await provider.embed_text(f"{request.title} {request.content}")
                    await repo.save_embedding(
                        memory_id=rec.id,
                        embedding=embedding_vec,
                        model_id=provider.model_id,
                        checksum=checksum,
                    )
                    # Register into vector store
                    self.vector_store.upsert(
                        memory_id=rec.id,
                        embedding=embedding_vec,
                        model_id=provider.model_id,
                        owner_scope=rec.owner_scope,
                        scope_id=rec.scope_id,
                    )
                except Exception as exc:
                    logger.error(f"Failed to generate embedding for memory '{rec.id}': {exc}")

            # 6. Index into SQLite FTS5 table
            await self.fts_index.index_memory(
                session=session,
                memory_id=rec.id,
                title=rec.title,
                content=rec.content,
                summary=rec.summary,
                owner_scope=rec.owner_scope,
                scope_id=rec.scope_id,
                memory_type=rec.memory_type,
            )

            # 7. Record access audit event
            await repo.log_access_event(
                action="create",
                outcome="allowed",
                actor_id=actor_id,
                agent_id=agent_id,
                workflow_id=workflow_id,
                memory_id=rec.id,
                reason="Created new memory record",
            )

            return self._to_response(rec)

    async def search_memory(
        self,
        request: MemorySearchRequest,
        actor_id: str = "user",
        allowed_memory_ids: Optional[set[str]] = None,
    ) -> MemorySearchResponse:
        """Executes search with hybrid, semantic, or keyword retrieval and records access audit."""
        start_time = time.perf_counter()
        async with get_db_session() as session:
            repo = MemoryRepository(session)
            provider = self.embedding_registry.get_active_provider()

            results = await self.retrieval_engine.search(
                session=session,
                query=request.query,
                embedding_provider=provider,
                search_mode=request.search_mode,
                memory_types=request.memory_types,
                owner_scope=request.owner_scope,
                scope_id=request.scope_id,
                allowed_memory_ids=allowed_memory_ids,
                exclude_superseded=request.exclude_superseded,
                min_score=request.min_score,
                limit=request.limit,
            )

            latency = round((time.perf_counter() - start_time) * 1000.0, 2)

            # Record search audit
            await repo.log_access_event(
                action="search",
                outcome="allowed",
                actor_id=actor_id,
                agent_id=request.agent_id,
                workflow_id=request.workflow_id,
                reason=f"Executed {request.search_mode.value} search for '{request.query[:50]}'",
            )

            return MemorySearchResponse(
                results=results,
                query=request.query,
                search_mode=request.search_mode,
                total_matched=len(results),
                latency_ms=latency,
            )

    async def get_memory(self, memory_id: str, actor_id: str = "user") -> Optional[MemoryRecordResponse]:
        """Retrieves a single memory record by ID."""
        async with get_db_session() as session:
            repo = MemoryRepository(session)
            record = await repo.get_memory_by_id(memory_id)
            if not record or record.is_deleted:
                return None
            await repo.touch_accessed(memory_id)
            await repo.log_access_event(
                action="read",
                outcome="allowed",
                actor_id=actor_id,
                memory_id=memory_id,
                reason="Direct memory retrieval",
            )
            return self._to_response(record)

    async def delete_memory(self, memory_id: str, actor_id: str = "user") -> bool:
        """Cascading deletion of a memory record and search index entries."""
        async with get_db_session() as session:
            return await self.deletion_coordinator.delete_memory(session, memory_id, actor_id=actor_id)

    async def build_context(
        self,
        request: ContextBuildRequest,
        allowed_memory_ids: Optional[set[str]] = None,
    ) -> ContextBuildResponse:
        """Assembles bounded, structured prompt context for agent execution."""
        async with get_db_session() as session:
            return await self.context_builder.build_context(session, request, allowed_memory_ids=allowed_memory_ids)

    async def get_stats(self) -> dict[str, Any]:
        """Returns storage, index, and classification statistics."""
        async with get_db_session() as session:
            repo = MemoryRepository(session)
            stats = await repo.get_stats()
            stats["vector_store_size"] = self.vector_store.size()
            stats["active_embedding_model"] = self.embedding_registry.get_active_provider().model_id
            stats["vector_dimension"] = self.vector_store.expected_dimension
            stats["fts_enabled"] = True
            return stats

    @staticmethod
    def _to_response(rec: Any) -> MemoryRecordResponse:
        return MemoryRecordResponse(
            id=rec.id,
            memory_type=MemoryType(rec.memory_type),
            title=rec.title,
            content=rec.content,
            summary=rec.summary,
            owner_scope=MemoryScope(rec.owner_scope),
            scope_id=rec.scope_id,
            source_type=rec.source_type,
            source_ref=rec.source_ref,
            provenance=rec.provenance_json or {},
            verification_status=VerificationStatus(rec.verification_status),
            confidence_category=rec.confidence_category,
            sensitivity_category=SensitivityCategory(rec.sensitivity_category),
            visibility_policy=rec.visibility_policy,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
            last_accessed_at=rec.last_accessed_at,
            expires_at=rec.expires_at,
            superseded_by=rec.superseded_by,
            version=rec.version,
            embedding_model_id=rec.embedding_model_id,
            embedding_version=rec.embedding_version,
            embedding_status=rec.embedding_status,
            content_checksum=rec.content_checksum,
            retention_policy=rec.retention_policy,
            is_deleted=rec.is_deleted,
            metadata=rec.metadata_json or {},
        )


# Global singleton memory service
memory_service = MemoryService()


def get_memory_service() -> MemoryService:
    return memory_service
