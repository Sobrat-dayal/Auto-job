"""Transactional Canonical Job Split Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalJobModel,
    CanonicalJobSourceLinkModel,
    JobSplitOperationModel,
)
from app.recruitment.aggregation.canonical.history import job_version_history_manager
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.contracts import SplitExecuteResponse
from app.recruitment.aggregation.errors import CanonicalJobNotFoundError, SplitValidationError


class SplitExecutionEngine:
    """Executes atomic, transactional separation of erroneously merged sources."""

    async def execute_split(
        self,
        session: AsyncSession,
        source_job_id: str,
        source_link_ids_to_detach: list[str],
        actor: str = "user_manual",
        reason: str = "Reversing incorrect merge / separating distinct requisition",
    ) -> SplitExecuteResponse:
        orig_job = await canonical_job_registry.get_by_id(session, source_job_id)
        if not orig_job:
            raise CanonicalJobNotFoundError(f"Canonical job {source_job_id} not found")

        stmt_links = select(CanonicalJobSourceLinkModel).where(
            CanonicalJobSourceLinkModel.canonical_job_id == source_job_id,
            CanonicalJobSourceLinkModel.association_status == "active",
        )
        res_links = await session.execute(stmt_links)
        active_links = list(res_links.scalars().all())

        if len(active_links) <= len(source_link_ids_to_detach):
            raise SplitValidationError("Cannot split all sources away from a canonical job (at least one must remain)")

        # Find matching link models
        links_to_move = [l for l in active_links if l.id in source_link_ids_to_detach]
        if not links_to_move:
            raise SplitValidationError("None of the specified source link IDs were found on this job")

        # Create new canonical job for detached sources
        first_moved = links_to_move[0]
        new_job = await canonical_job_registry.create_canonical_job(
            session=session,
            title=orig_job.display_title,
            employer_id=orig_job.employer_id,
            requisition_id=None,  # will re-extract from moved sources
            employment_type=orig_job.employment_type,
            location_summary=orig_job.location_summary,
            work_arrangement=orig_job.work_arrangement,
            description_reference=orig_job.description_reference,
            compensation_summary=orig_job.compensation_summary,
            primary_source_id=first_moved.source_id,
            primary_url=first_moved.original_url,
        )

        # Move links to new job
        for link in links_to_move:
            link.canonical_job_id = new_job.id
            link.association_status = "active"

        # Update source counts & versions
        orig_job.source_count = max(1, orig_job.source_count - len(links_to_move))
        orig_job.version += 1
        orig_job.updated_at = datetime.now(UTC)

        new_job.source_count = len(links_to_move)

        # Record split operation
        split_op = JobSplitOperationModel(
            source_job_id=orig_job.id,
            resulting_job_ids_json=[orig_job.id, new_job.id],
            actor=actor,
            reason=reason,
            affected_sources_json=[l.source_observation_id for l in links_to_move],
            status="completed",
            created_at=datetime.now(UTC),
        )
        session.add(split_op)
        await session.flush()

        # Record history for both
        await job_version_history_manager.record_version(
            session=session,
            job=orig_job,
            change_summary=f"Split operation: {len(links_to_move)} sources detached into new job {new_job.id}",
        )
        await job_version_history_manager.record_version(
            session=session,
            job=new_job,
            change_summary=f"Created via split from original job {orig_job.id}",
        )

        return SplitExecuteResponse(
            operation_id=split_op.id,
            original_job_id=orig_job.id,
            new_canonical_job_ids=[new_job.id],
            status="completed",
        )


split_execution_engine = SplitExecutionEngine()
