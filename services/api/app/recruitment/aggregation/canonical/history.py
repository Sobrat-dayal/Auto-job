"""Canonical Job Version History & Audit Logging (Stage 27)."""

from datetime import UTC, datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobModel, CanonicalJobVersionModel


class JobVersionHistoryManager:
    """Records immutable version snapshots of canonical jobs for auditability."""

    async def record_version(
        self,
        session: AsyncSession,
        job: CanonicalJobModel,
        change_summary: str,
    ) -> CanonicalJobVersionModel:
        """Create an immutable historical revision record."""
        snapshot = {
            "id": job.id,
            "employer_id": job.employer_id,
            "display_title": job.display_title,
            "requisition_id": job.requisition_id,
            "employment_type": job.employment_type,
            "location_summary": job.location_summary,
            "work_arrangement": job.work_arrangement,
            "compensation_summary": job.compensation_summary,
            "status": job.status,
            "source_count": job.source_count,
            "version": job.version,
            "snapshot_timestamp": datetime.now(UTC).isoformat(),
        }

        ver = CanonicalJobVersionModel(
            canonical_job_id=job.id,
            version_number=job.version,
            snapshot_json=snapshot,
            change_summary=change_summary,
            created_at=datetime.now(UTC),
        )
        session.add(ver)
        await session.flush()
        return ver


job_version_history_manager = JobVersionHistoryManager()
