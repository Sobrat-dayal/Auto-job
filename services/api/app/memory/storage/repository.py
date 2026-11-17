"""Asynchronous SQLite repository for memory records, embeddings, conflicts, and procedures."""

from datetime import UTC, datetime
import logging
from typing import Any, Optional
import uuid

from sqlalchemy import delete, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    MemoryAccessEventRecord,
    MemoryConflictRecord,
    MemoryEmbeddingRecord,
    MemoryRecord,
    ProceduralMemoryRecord,
)

logger = logging.getLogger("autonom.memory.storage.repository")


class MemoryRepository:
    """Async repository providing database persistence for the Stage 15 Memory Engine."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -----------------------------------------------------------------------
    # Memory Record CRUD
    # -----------------------------------------------------------------------

    async def create_memory(
        self,
        memory_type: str,
        title: str,
        content: str,
        summary: str,
        owner_scope: str,
        scope_id: str,
        source_type: str,
        source_ref: str,
        provenance_json: dict[str, Any],
        verification_status: str,
        confidence_category: str,
        sensitivity_category: str,
        visibility_policy: str,
        content_checksum: str,
        retention_policy: str = "permanent",
        embedding_model_id: str = "local-minilm-l6",
        expires_at: Optional[datetime] = None,
        metadata_json: Optional[dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> MemoryRecord:
        """Persists a new memory record."""
        record = MemoryRecord(
            id=memory_id or f"mem_{uuid.uuid4().hex[:12]}",
            memory_type=memory_type,
            title=title,
            content=content,
            summary=summary,
            owner_scope=owner_scope,
            scope_id=scope_id,
            source_type=source_type,
            source_ref=source_ref,
            provenance_json=provenance_json,
            verification_status=verification_status,
            confidence_category=confidence_category,
            sensitivity_category=sensitivity_category,
            visibility_policy=visibility_policy,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            last_accessed_at=datetime.now(UTC),
            expires_at=expires_at,
            superseded_by=None,
            version=1,
            embedding_model_id=embedding_model_id,
            embedding_version=1,
            embedding_status="pending",
            content_checksum=content_checksum,
            retention_policy=retention_policy,
            is_deleted=False,
            metadata_json=metadata_json or {},
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        """Retrieves a memory record by ID."""
        stmt = select(MemoryRecord).where(MemoryRecord.id == memory_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_by_checksum(self, checksum: str, scope_id: str) -> Optional[MemoryRecord]:
        """Finds an existing memory record matching a SHA-256 checksum within a scope."""
        stmt = select(MemoryRecord).where(
            MemoryRecord.content_checksum == checksum,
            MemoryRecord.scope_id == scope_id,
            MemoryRecord.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_memories(
        self,
        owner_scope: Optional[str] = None,
        scope_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryRecord]:
        """Lists memory records with optional filtering and pagination."""
        stmt = select(MemoryRecord)
        if not include_deleted:
            stmt = stmt.where(MemoryRecord.is_deleted.is_(False))
        if owner_scope:
            stmt = stmt.where(MemoryRecord.owner_scope == owner_scope)
        if scope_id:
            stmt = stmt.where(MemoryRecord.scope_id == scope_id)
        if memory_type:
            stmt = stmt.where(MemoryRecord.memory_type == memory_type)
        if verification_status:
            stmt = stmt.where(MemoryRecord.verification_status == verification_status)

        stmt = stmt.order_by(desc(MemoryRecord.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_memory(
        self,
        memory_id: str,
        updates: dict[str, Any],
    ) -> Optional[MemoryRecord]:
        """Updates specific attributes of a memory record."""
        record = await self.get_memory_by_id(memory_id)
        if not record or record.is_deleted:
            return None

        for field, value in updates.items():
            if hasattr(record, field) and value is not None:
                setattr(record, field, value)

        record.updated_at = datetime.now(UTC)
        record.version += 1
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def soft_delete_memory(self, memory_id: str) -> bool:
        """Soft-deletes a memory record, removing it from active queries."""
        record = await self.get_memory_by_id(memory_id)
        if not record:
            return False

        record.is_deleted = True
        record.updated_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def touch_accessed(self, memory_id: str) -> None:
        """Updates last_accessed_at timestamp."""
        stmt = (
            update(MemoryRecord)
            .where(MemoryRecord.id == memory_id)
            .values(last_accessed_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)
        await self.session.commit()

    # -----------------------------------------------------------------------
    # Memory Embedding Records
    # -----------------------------------------------------------------------

    async def save_embedding(
        self,
        memory_id: str,
        embedding: list[float],
        model_id: str,
        checksum: str,
    ) -> MemoryEmbeddingRecord:
        """Saves a vector embedding record for a memory."""
        # Delete prior embedding for this memory & model
        del_stmt = delete(MemoryEmbeddingRecord).where(
            MemoryEmbeddingRecord.memory_id == memory_id,
            MemoryEmbeddingRecord.embedding_model_id == model_id,
        )
        await self.session.execute(del_stmt)

        rec = MemoryEmbeddingRecord(
            id=f"emb_{uuid.uuid4().hex[:12]}",
            memory_id=memory_id,
            embedding_model_id=model_id,
            dimension=len(embedding),
            vector_json=embedding,
            checksum=checksum,
            created_at=datetime.now(UTC),
        )
        self.session.add(rec)

        # Mark memory record as completed
        upd_stmt = (
            update(MemoryRecord)
            .where(MemoryRecord.id == memory_id)
            .values(embedding_status="completed")
        )
        await self.session.execute(upd_stmt)
        await self.session.commit()
        await self.session.refresh(rec)
        return rec

    async def get_embedding(self, memory_id: str, model_id: str) -> Optional[MemoryEmbeddingRecord]:
        """Retrieves stored embedding vector for a memory."""
        stmt = select(MemoryEmbeddingRecord).where(
            MemoryEmbeddingRecord.memory_id == memory_id,
            MemoryEmbeddingRecord.embedding_model_id == model_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def load_all_active_embeddings(self) -> list[tuple[MemoryRecord, MemoryEmbeddingRecord]]:
        """Loads all active memories and their corresponding vector embeddings for index warmup."""
        stmt = (
            select(MemoryRecord, MemoryEmbeddingRecord)
            .join(MemoryEmbeddingRecord, MemoryRecord.id == MemoryEmbeddingRecord.memory_id)
            .where(MemoryRecord.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    # -----------------------------------------------------------------------
    # Procedural Memory CRUD
    # -----------------------------------------------------------------------

    async def create_procedure(
        self,
        procedure_id: str,
        name: str,
        description: str,
        capability_id: str,
        required_inputs: dict[str, Any],
        steps: list[dict[str, Any]],
        preconditions: dict[str, Any],
        expected_outputs: dict[str, Any],
        verification_requirements: dict[str, Any],
        required_permissions: list[str],
        provenance: dict[str, Any],
    ) -> ProceduralMemoryRecord:
        """Persists a new reusable procedural memory."""
        proc = ProceduralMemoryRecord(
            id=f"proc_{uuid.uuid4().hex[:12]}",
            procedure_id=procedure_id,
            name=name,
            description=description,
            capability_id=capability_id,
            required_inputs_json=required_inputs,
            steps_json=steps,
            preconditions_json=preconditions,
            expected_outputs_json=expected_outputs,
            verification_requirements_json=verification_requirements,
            required_permissions_json=required_permissions,
            provenance_json=provenance,
            version=1,
            validation_status="candidate",
            success_count=0,
            failure_count=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.session.add(proc)
        await self.session.commit()
        await self.session.refresh(proc)
        return proc

    async def get_procedure(self, procedure_id: str) -> Optional[ProceduralMemoryRecord]:
        """Gets a procedure by its unique procedure_id."""
        stmt = select(ProceduralMemoryRecord).where(
            or_(
                ProceduralMemoryRecord.procedure_id == procedure_id,
                ProceduralMemoryRecord.id == procedure_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_procedures(
        self,
        capability_id: Optional[str] = None,
        validation_status: Optional[str] = None,
    ) -> list[ProceduralMemoryRecord]:
        """Lists registered procedural memories."""
        stmt = select(ProceduralMemoryRecord)
        if capability_id:
            stmt = stmt.where(ProceduralMemoryRecord.capability_id == capability_id)
        if validation_status:
            stmt = stmt.where(ProceduralMemoryRecord.validation_status == validation_status)
        stmt = stmt.order_by(desc(ProceduralMemoryRecord.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -----------------------------------------------------------------------
    # Memory Conflict Records
    # -----------------------------------------------------------------------

    async def record_conflict(
        self,
        memory_id_a: str,
        memory_id_b: str,
        conflict_type: str,
        description: str,
    ) -> MemoryConflictRecord:
        """Records a contradiction or conflict between two memory records."""
        conflict = MemoryConflictRecord(
            id=f"cnf_{uuid.uuid4().hex[:12]}",
            memory_id_a=memory_id_a,
            memory_id_b=memory_id_b,
            conflict_type=conflict_type,
            description=description,
            status="unresolved",
            created_at=datetime.now(UTC),
        )
        self.session.add(conflict)
        await self.session.commit()
        await self.session.refresh(conflict)
        return conflict

    async def list_conflicts(self, status: Optional[str] = None) -> list[MemoryConflictRecord]:
        """Lists recorded memory conflicts."""
        stmt = select(MemoryConflictRecord)
        if status:
            stmt = stmt.where(MemoryConflictRecord.status == status)
        stmt = stmt.order_by(desc(MemoryConflictRecord.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution_action: str,
        resolved_by: str = "operator",
    ) -> Optional[MemoryConflictRecord]:
        """Marks a conflict resolved with the designated action."""
        stmt = select(MemoryConflictRecord).where(MemoryConflictRecord.id == conflict_id)
        result = await self.session.execute(stmt)
        conflict = result.scalars().first()
        if not conflict:
            return None

        conflict.status = "resolved"
        conflict.resolution_action = resolution_action
        conflict.resolved_by = resolved_by
        conflict.resolved_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(conflict)
        return conflict

    # -----------------------------------------------------------------------
    # Memory Access Audit Events
    # -----------------------------------------------------------------------

    async def log_access_event(
        self,
        action: str,
        outcome: str,
        actor_id: str = "user",
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        memory_id: Optional[str] = None,
        reason: str = "",
    ) -> MemoryAccessEventRecord:
        """Appends an immutable audit event for memory retrieval or mutation."""
        event = MemoryAccessEventRecord(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            memory_id=memory_id,
            actor_id=actor_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            action=action,
            outcome=outcome,
            reason=reason,
            timestamp=datetime.now(UTC),
        )
        self.session.add(event)
        await self.session.commit()
        return event

    async def get_stats(self) -> dict[str, Any]:
        """Aggregates memory counts by type, verification status, and scope."""
        records = await self.list_memories(limit=10000)
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_scope: dict[str, int] = {}
        indexed = 0
        pending = 0

        for r in records:
            by_type[r.memory_type] = by_type.get(r.memory_type, 0) + 1
            by_status[r.verification_status] = by_status.get(r.verification_status, 0) + 1
            by_scope[r.owner_scope] = by_scope.get(r.owner_scope, 0) + 1
            if r.embedding_status == "completed":
                indexed += 1
            elif r.embedding_status == "pending":
                pending += 1

        conflicts = await self.list_conflicts(status="unresolved")
        procs = await self.list_procedures()

        return {
            "total_records": len(records),
            "by_type": by_type,
            "by_verification_status": by_status,
            "by_scope": by_scope,
            "indexed_records": indexed,
            "pending_embeddings": pending,
            "conflicts_unresolved": len(conflicts),
            "active_procedures": len(procs),
        }
