"""Canonical job resolver for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import JobListing
from app.recruitment.matching.errors import CanonicalJobNotFoundError

logger = logging.getLogger("autonom.recruitment.matching.inputs.canonical_jobs")


async def resolve_canonical_job(canonical_job_id: str, db_session: AsyncSession) -> dict[str, Any]:
    """Retrieves canonical job listing record from database."""
    stmt = select(JobListing).where(JobListing.id == canonical_job_id)
    res = await db_session.execute(stmt)
    job = res.scalar_one_or_none()

    if not job:
        raise CanonicalJobNotFoundError(f"Canonical job '{canonical_job_id}' not found in database.")

    return {
        "id": job.id,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "employment_type": job.employment_type,
        "work_arrangement": job.work_arrangement,
        "salary_range": job.salary_range,
        "description": job.description or "",
        "status": job.status,
        "discovered_at": job.discovered_at.isoformat() if job.discovered_at else None,
        "last_verified_at": job.last_verified_at.isoformat() if job.last_verified_at else None,
        "application_url": job.application_url,
    }
