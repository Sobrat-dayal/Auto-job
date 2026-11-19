"""Dependency graph and invalidation engine for Stage 30 Recruitment Pipeline."""

from __future__ import annotations

import logging
from typing import Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    JobListing,
    RecruitmentOpportunityQueueModel,
)
from app.recruitment.matching.lifecycle.invalidation import invalidate_for_job_update

logger = logging.getLogger("autonom.recruitment.monitoring.pipeline.dependency_graph")


class DependencyGraphManager:
    """Manages version dependencies between Canonical Jobs, Intelligence, Matching, and Queue."""

    async def invalidate_downstream_for_job(
        self,
        canonical_job_id: str,
        reason: str,
        session: AsyncSession,
    ) -> None:
        """Invalidates matching cache and flags opportunity queue entry when a job changes materially."""
        logger.info(f"Invalidating downstream dependencies for job '{canonical_job_id}': {reason}")

        # Invalidate Stage 29 match evaluations
        await invalidate_for_job_update(canonical_job_id, session)

        # Update Opportunity Queue entry status to awaiting match
        stmt = (
            update(RecruitmentOpportunityQueueModel)
            .where(RecruitmentOpportunityQueueModel.canonical_job_id == canonical_job_id)
            .values(
                queue_status="awaiting_match",
                ready_for_preparation=False,
            )
        )
        await session.execute(stmt)
        await session.flush()

    async def handle_job_closure(
        self,
        canonical_job_id: str,
        session: AsyncSession,
    ) -> None:
        """Updates canonical job and queue when confirmed closed."""
        logger.info(f"Handling closure for job '{canonical_job_id}'")

        # Update canonical job status
        stmt_job = (
            update(JobListing)
            .where(JobListing.id == canonical_job_id)
            .values(status="closed")
        )
        await session.execute(stmt_job)

        # Update opportunity queue
        stmt_q = (
            update(RecruitmentOpportunityQueueModel)
            .where(RecruitmentOpportunityQueueModel.canonical_job_id == canonical_job_id)
            .values(
                job_availability="closed",
                queue_status="closed",
                ready_for_preparation=False,
            )
        )
        await session.execute(stmt_q)
        await session.flush()


dependency_graph = DependencyGraphManager()
