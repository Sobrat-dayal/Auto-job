"""Lifecycle invalidation and dependency tracking for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import JobMatchEvaluationModel
from app.recruitment.matching.lifecycle.caching import clear_cache

logger = logging.getLogger("autonom.recruitment.matching.lifecycle.invalidation")


async def invalidate_for_profile_update(profile_id: str, db_session: AsyncSession) -> int:
    """Marks current evaluations for a profile as not current following an applicant update (Required Test 148)."""
    clear_cache()
    stmt = (
        update(JobMatchEvaluationModel)
        .where(
            JobMatchEvaluationModel.profile_id == profile_id,
            JobMatchEvaluationModel.is_current == True,  # noqa: E712
        )
        .values(is_current=False)
    )
    res = await db_session.execute(stmt)
    count = res.rowcount
    logger.info(f"Invalidated {count} match evaluations for updated profile '{profile_id}'.")
    return count


async def invalidate_for_job_update(canonical_job_id: str, db_session: AsyncSession) -> int:
    """Marks current evaluations for a job as not current following requirements change (Required Test 149)."""
    clear_cache()
    stmt = (
        update(JobMatchEvaluationModel)
        .where(
            JobMatchEvaluationModel.canonical_job_id == canonical_job_id,
            JobMatchEvaluationModel.is_current == True,  # noqa: E712
        )
        .values(is_current=False)
    )
    res = await db_session.execute(stmt)
    count = res.rowcount
    logger.info(f"Invalidated {count} match evaluations for updated job '{canonical_job_id}'.")
    return count


async def invalidate_for_policy_update(strategy_id: str, db_session: AsyncSession) -> int:
    """Marks evaluations as not current following a career policy or strategy change (Required Test 150)."""
    clear_cache()
    stmt = (
        update(JobMatchEvaluationModel)
        .where(
            JobMatchEvaluationModel.career_strategy_id == strategy_id,
            JobMatchEvaluationModel.is_current == True,  # noqa: E712
        )
        .values(is_current=False)
    )
    res = await db_session.execute(stmt)
    count = res.rowcount
    logger.info(f"Invalidated {count} match evaluations for updated career strategy '{strategy_id}'.")
    return count
