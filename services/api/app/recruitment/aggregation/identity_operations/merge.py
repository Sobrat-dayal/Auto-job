"""Transactional Canonical Job Merge Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalJobLocationModel,
    CanonicalJobModel,
    CanonicalJobSourceLinkModel,
    JobMergeOperationModel,
)
from app.recruitment.aggregation.canonical.history import job_version_history_manager
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.contracts import CanonicalJobRecord, MergeExecuteResponse
from app.recruitment.aggregation.errors import CanonicalJobNotFoundError, CircularMergeError
from app.recruitment.aggregation.identity_operations.supersession import supersession_manager


class MergeExecutionEngine:
    """Executes atomic, transactional merges of canonical job identities."""

    async def execute_merge(
        self,
        session: AsyncSession,
        surviving_job_id: str,
        superseded_job_id: str,
        actor: str = "system_auto",
        reason: str = "Authorized duplicate merge",
        field_overrides: Optional[dict[str, Any]] = None,
    ) -> MergeExecuteResponse:
        if surviving_job_id == superseded_job_id:
            raise CircularMergeError("Cannot merge a canonical job into itself")

        surviving = await canonical_job_registry.get_by_id(session, surviving_job_id)
        if not surviving:
            raise CanonicalJobNotFoundError(f"Surviving job {surviving_job_id} not found")

        superseded = await canonical_job_registry.get_by_id(session, superseded_job_id)
        if not superseded:
            raise CanonicalJobNotFoundError(f"Superseded job {superseded_job_id} not found")

        # 1. Reassign all source links from superseded to surviving
        stmt_links = select(CanonicalJobSourceLinkModel).where(
            CanonicalJobSourceLinkModel.canonical_job_id == superseded_job_id,
            CanonicalJobSourceLinkModel.association_status == "active",
        )
        res_links = await session.execute(stmt_links)
        superseded_links = list(res_links.scalars().all())

        links_transferred = 0
        for link in superseded_links:
            link.canonical_job_id = surviving.id
            link.association_status = "active"
            link.is_primary = False  # preserve existing primary
            links_transferred += 1

        # 2. Reassign locations
        stmt_locs = select(CanonicalJobLocationModel).where(
            CanonicalJobLocationModel.canonical_job_id == superseded_job_id
        )
        res_locs = await session.execute(stmt_locs)
        for loc in res_locs.scalars().all():
            loc.canonical_job_id = surviving.id

        # 3. Create Supersession Alias
        alias = await supersession_manager.create_alias(
            session=session,
            superseded_id=superseded.id,
            surviving_id=surviving.id,
        )

        # 4. Mark superseded job as superseded/closed
        superseded.status = "closed"
        superseded.identity_status = "rejected"
        superseded.updated_at = datetime.now(UTC)

        # 5. Update surviving job
        surviving.source_count += links_transferred
        surviving.version += 1
        surviving.updated_at = datetime.now(UTC)

        if field_overrides:
            for k, v in field_overrides.items():
                if hasattr(surviving, k):
                    setattr(surviving, k, v)

        # 6. Record Merge Operation
        merge_op = JobMergeOperationModel(
            surviving_job_id=surviving.id,
            superseded_job_id=superseded.id,
            actor=actor,
            reason=reason,
            merge_plan_json={
                "transferred_sources": links_transferred,
                "overrides": field_overrides or {},
            },
            status="completed",
            created_at=datetime.now(UTC),
        )
        session.add(merge_op)
        await session.flush()

        # 7. Record new version snapshot
        await job_version_history_manager.record_version(
            session=session,
            job=surviving,
            change_summary=f"Merged duplicate job {superseded.id}: {reason}",
        )

        contract = canonical_job_registry.to_contract(surviving)

        return MergeExecuteResponse(
            operation_id=merge_op.id,
            surviving_job=contract,
            superseded_job_id=superseded.id,
            status="completed",
            transferred_source_count=links_transferred,
            created_alias_id=alias.id,
        )


merge_execution_engine = MergeExecutionEngine()
