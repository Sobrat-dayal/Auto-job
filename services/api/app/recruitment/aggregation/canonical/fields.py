"""Field Candidate Management & Provenance Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobFieldCandidateModel


class FieldCandidateManager:
    """Stores and tracks candidate values for canonical job fields across sources."""

    async def add_candidate(
        self,
        session: AsyncSession,
        canonical_job_id: str,
        source_link_id: str,
        field_name: str,
        candidate_value: Optional[str] = None,
        candidate_value_json: Optional[dict[str, Any]] = None,
        is_selected: bool = False,
    ) -> CanonicalJobFieldCandidateModel:
        cand = CanonicalJobFieldCandidateModel(
            canonical_job_id=canonical_job_id,
            source_link_id=source_link_id,
            field_name=field_name,
            candidate_value=candidate_value,
            candidate_value_json=candidate_value_json or {},
            retrieved_at=datetime.now(UTC),
            is_selected=is_selected,
        )
        session.add(cand)
        await session.flush()
        return cand

    async def list_candidates(
        self,
        session: AsyncSession,
        canonical_job_id: str,
        field_name: Optional[str] = None,
    ) -> list[CanonicalJobFieldCandidateModel]:
        stmt = select(CanonicalJobFieldCandidateModel).where(
            CanonicalJobFieldCandidateModel.canonical_job_id == canonical_job_id
        )
        if field_name:
            stmt = stmt.where(CanonicalJobFieldCandidateModel.field_name == field_name)
        res = await session.execute(stmt)
        return list(res.scalars().all())


field_candidate_manager = FieldCandidateManager()
