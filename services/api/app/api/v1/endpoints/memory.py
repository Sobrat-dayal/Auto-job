"""FastAPI REST endpoints for the Stage 15 Memory Engine."""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db_session
from app.memory.contracts import (
    ContextBuildRequest,
    ContextBuildResponse,
    MemoryConflictResolveRequest,
    MemoryConflictResponse,
    MemoryCreateRequest,
    MemoryRecordResponse,
    MemoryScope,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryStatsResponse,
    MemoryType,
    MemoryUpdateRequest,
    ProceduralMemoryCreateRequest,
    ProceduralMemoryResponse,
    SearchMode,
)
from app.memory.lifecycle.conflicts import conflict_resolver
from app.memory.service import memory_service
from app.memory.storage.repository import MemoryRepository

logger = logging.getLogger("autonom.api.memory")
router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory_hybrid(request: MemorySearchRequest) -> MemorySearchResponse:
    """Performs hybrid semantic and keyword retrieval over authorized memories."""
    request.search_mode = SearchMode.HYBRID
    return await memory_service.search_memory(request)


@router.post("/search/semantic", response_model=MemorySearchResponse)
async def search_memory_semantic(request: MemorySearchRequest) -> MemorySearchResponse:
    """Performs dense vector similarity retrieval over authorized memories."""
    request.search_mode = SearchMode.SEMANTIC
    return await memory_service.search_memory(request)


@router.post("/search/keyword", response_model=MemorySearchResponse)
async def search_memory_keyword(request: MemorySearchRequest) -> MemorySearchResponse:
    """Performs SQLite FTS5 full-text keyword search over authorized memories."""
    request.search_mode = SearchMode.KEYWORD
    return await memory_service.search_memory(request)


@router.get("", response_model=list[MemoryRecordResponse])
async def list_memories(
    owner_scope: Optional[MemoryScope] = None,
    scope_id: Optional[str] = None,
    memory_type: Optional[MemoryType] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[MemoryRecordResponse]:
    """Lists active memory records with optional scope and type filters."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        records = await repo.list_memories(
            owner_scope=owner_scope.value if owner_scope else None,
            scope_id=scope_id,
            memory_type=memory_type.value if memory_type else None,
            limit=limit,
            offset=offset,
        )
        return [memory_service._to_response(r) for r in records]


@router.post("", response_model=MemoryRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(request: MemoryCreateRequest) -> MemoryRecordResponse:
    """Creates, embeds, and indexes a new persistent memory record."""
    return await memory_service.write_memory(request)


@router.get("/status", response_model=MemoryStatsResponse)
async def get_memory_status() -> MemoryStatsResponse:
    """Retrieves system-wide telemetry, record counts, and index health."""
    stats = await memory_service.get_stats()
    return MemoryStatsResponse(
        total_records=stats["total_records"],
        by_type=stats["by_type"],
        by_verification_status=stats["by_verification_status"],
        by_scope=stats["by_scope"],
        indexed_records=stats["indexed_records"],
        pending_embeddings=stats["pending_embeddings"],
        conflicts_unresolved=stats["conflicts_unresolved"],
        active_procedures=stats["active_procedures"],
        vector_dimension=stats["vector_dimension"],
        fts_enabled=stats["fts_enabled"],
    )


@router.post("/context", response_model=ContextBuildResponse)
async def build_agent_context(request: ContextBuildRequest) -> ContextBuildResponse:
    """Assembles structured prompt context for an agent execution within token budget."""
    return await memory_service.build_context(request)


@router.post("/export")
async def export_memory(
    owner_scope: Optional[MemoryScope] = None,
    scope_id: Optional[str] = None,
    include_sensitive: bool = False,
) -> list[dict[str, Any]]:
    """Exports authorized memories in structured JSON format."""
    async with get_db_session() as session:
        return await memory_service.export_service.export_memories(
            session=session,
            owner_scope=owner_scope,
            scope_id=scope_id,
            include_sensitive=include_sensitive,
        )


@router.post("/consolidate")
async def consolidate_memories(
    scope_id: str = Query(..., description="Target scope ID to consolidate"),
) -> dict[str, Any]:
    """Runs bounded consolidation job over memories within a scope."""
    async with get_db_session() as session:
        return await memory_service.consolidator.consolidate_scope(session, scope_id=scope_id)


@router.post("/index/rebuild")
async def rebuild_memory_indexes() -> dict[str, Any]:
    """Rebuilds and reloads active vector and FTS5 search indexes."""
    await memory_service.initialize()
    return {"status": "completed", "vector_store_size": memory_service.vector_store.size()}


@router.get("/conflicts", response_model=list[MemoryConflictResponse])
async def list_conflicts(
    status: Optional[str] = Query(default="unresolved"),
) -> list[MemoryConflictResponse]:
    """Lists contradictory memory records requiring review or resolution."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        conflicts = await repo.list_conflicts(status=status)
        return [
            MemoryConflictResponse(
                id=c.id,
                memory_id_a=c.memory_id_a,
                memory_id_b=c.memory_id_b,
                conflict_type=c.conflict_type,
                description=c.description,
                status=c.status,
                resolution_action=c.resolution_action,
                resolved_by=c.resolved_by,
                created_at=c.created_at,
                resolved_at=c.resolved_at,
            )
            for c in conflicts
        ]


@router.post("/conflicts/{conflict_id}/resolve", response_model=MemoryConflictResponse)
async def resolve_conflict(
    conflict_id: str,
    request: MemoryConflictResolveRequest,
) -> MemoryConflictResponse:
    """Resolves a detected memory conflict, optionally superseding an older record."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        resolved = await repo.resolve_conflict(
            conflict_id=conflict_id,
            resolution_action=request.resolution_action,
        )
        if not resolved:
            raise HTTPException(status_code=404, detail="Conflict not found")

        if request.resolution_action == "supersede" and request.superseding_memory_id:
            # Mark superseded
            await conflict_resolver.supersede_memory(
                session=session,
                old_memory_id=resolved.memory_id_a,
                new_memory_id=request.superseding_memory_id,
            )

        return MemoryConflictResponse(
            id=resolved.id,
            memory_id_a=resolved.memory_id_a,
            memory_id_b=resolved.memory_id_b,
            conflict_type=resolved.conflict_type,
            description=resolved.description,
            status=resolved.status,
            resolution_action=resolved.resolution_action,
            resolved_by=resolved.resolved_by,
            created_at=resolved.created_at,
            resolved_at=resolved.resolved_at,
        )


@router.get("/procedures", response_model=list[ProceduralMemoryResponse])
async def list_procedures(
    capability_id: Optional[str] = None,
) -> list[ProceduralMemoryResponse]:
    """Lists registered procedural memory templates."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        procs = await repo.list_procedures(capability_id=capability_id)
        return [
            ProceduralMemoryResponse(
                id=p.id,
                procedure_id=p.procedure_id,
                name=p.name,
                description=p.description,
                capability_id=p.capability_id,
                required_inputs=p.required_inputs_json or {},
                steps=p.steps_json or [],
                preconditions=p.preconditions_json or {},
                expected_outputs=p.expected_outputs_json or {},
                verification_requirements=p.verification_requirements_json or {},
                required_permissions=p.required_permissions_json or [],
                provenance=p.provenance_json or {},
                version=p.version,
                validation_status=p.validation_status,
                success_count=p.success_count,
                failure_count=p.failure_count,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in procs
        ]


@router.post("/procedures", response_model=ProceduralMemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_procedure(request: ProceduralMemoryCreateRequest) -> ProceduralMemoryResponse:
    """Creates a validated procedural memory."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        p = await repo.create_procedure(
            procedure_id=request.procedure_id,
            name=request.name,
            description=request.description,
            capability_id=request.capability_id,
            required_inputs=request.required_inputs,
            steps=request.steps,
            preconditions=request.preconditions,
            expected_outputs=request.expected_outputs,
            verification_requirements=request.verification_requirements,
            required_permissions=request.required_permissions,
            provenance=request.provenance,
        )
        return ProceduralMemoryResponse(
            id=p.id,
            procedure_id=p.procedure_id,
            name=p.name,
            description=p.description,
            capability_id=p.capability_id,
            required_inputs=p.required_inputs_json or {},
            steps=p.steps_json or [],
            preconditions=p.preconditions_json or {},
            expected_outputs=p.expected_outputs_json or {},
            verification_requirements=p.verification_requirements_json or {},
            required_permissions=p.required_permissions_json or [],
            provenance=p.provenance_json or {},
            version=p.version,
            validation_status=p.validation_status,
            success_count=p.success_count,
            failure_count=p.failure_count,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


@router.get("/{memory_id}", response_model=MemoryRecordResponse)
async def get_memory(memory_id: str) -> MemoryRecordResponse:
    """Retrieves an authorized memory record by ID."""
    rec = await memory_service.get_memory(memory_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Memory record not found")
    return rec


@router.patch("/{memory_id}", response_model=MemoryRecordResponse)
async def update_memory(memory_id: str, request: MemoryUpdateRequest) -> MemoryRecordResponse:
    """Updates fields of an existing memory record."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        updates = request.model_dump(exclude_unset=True)
        # Convert enums to string values
        for k in ("verification_status", "confidence_category", "sensitivity_category", "visibility_policy", "retention_policy"):
            if k in updates and updates[k] is not None:
                updates[k] = updates[k].value

        updated = await repo.update_memory(memory_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Memory record not found")

        # If content changed, re-index and re-embed
        if "content" in updates or "title" in updates:
            provider = memory_service.embedding_registry.get_active_provider()
            new_embedding = await provider.embed_text(f"{updated.title} {updated.content}")
            await repo.save_embedding(
                memory_id=updated.id,
                embedding=new_embedding,
                model_id=provider.model_id,
                checksum=memory_service.dedup_service.compute_checksum(updated.content),
            )
            memory_service.vector_store.upsert(
                memory_id=updated.id,
                embedding=new_embedding,
                model_id=provider.model_id,
                owner_scope=updated.owner_scope,
                scope_id=updated.scope_id,
            )
            await memory_service.fts_index.index_memory(
                session=session,
                memory_id=updated.id,
                title=updated.title,
                content=updated.content,
                summary=updated.summary,
                owner_scope=updated.owner_scope,
                scope_id=updated.scope_id,
                memory_type=updated.memory_type,
            )

        return memory_service._to_response(updated)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: str) -> None:
    """Securely deletes a memory record, removing it from all search indices."""
    ok = await memory_service.delete_memory(memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Memory record not found")


@router.get("/{memory_id}/history")
async def get_memory_history(memory_id: str) -> dict[str, Any]:
    """Retrieves access and modification history for a memory record."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        rec = await repo.get_memory_by_id(memory_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Memory record not found")
        return {
            "id": rec.id,
            "version": rec.version,
            "created_at": rec.created_at.isoformat(),
            "updated_at": rec.updated_at.isoformat(),
            "last_accessed_at": rec.last_accessed_at.isoformat(),
            "superseded_by": rec.superseded_by,
        }


@router.get("/{memory_id}/sources")
async def get_memory_sources(memory_id: str) -> dict[str, Any]:
    """Retrieves provenance and evidence references for a memory record."""
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        rec = await repo.get_memory_by_id(memory_id)
        if not rec:
            raise HTTPException(status_code=404, detail="Memory record not found")
        return {
            "id": rec.id,
            "source_type": rec.source_type,
            "source_ref": rec.source_ref,
            "provenance": rec.provenance_json or {},
        }
