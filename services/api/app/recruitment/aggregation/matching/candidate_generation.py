"""Duplicate Candidate Generation and Multi-Key Blocking (Stage 27)."""

from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobIdentifierModel, CanonicalJobModel
from app.recruitment.aggregation.normalization.titles import normalize_title


class CandidateGenerationEngine:
    """Generates a bounded candidate set for duplicate comparison using multi-key blocking."""

    async def find_candidates_for_job(
        self,
        session: AsyncSession,
        employer_id: Optional[str],
        title: str,
        requisition_id: Optional[str] = None,
        exclude_job_id: Optional[str] = None,
        limit: int = 25,
    ) -> list[CanonicalJobModel]:
        """Query potential duplicate candidates using employer blocking and requisition matching."""
        if not employer_id and not requisition_id and not title:
            return []

        conditions = []

        # 1. Block on same employer ID (strongest blocker)
        if employer_id:
            conditions.append(CanonicalJobModel.employer_id == employer_id)

        # 2. Block on exact requisition ID across employers
        if requisition_id:
            conditions.append(CanonicalJobModel.requisition_id == requisition_id)

        # 3. Block on normalized title match if employer is not known
        if not employer_id:
            norm_title = normalize_title(title)
            tokens = norm_title.split()[:3]
            for token in tokens:
                if len(token) >= 4:
                    conditions.append(CanonicalJobModel.normalized_title.ilike(f"%{token}%"))

        if not conditions:
            return []

        stmt = select(CanonicalJobModel).where(or_(*conditions))
        if exclude_job_id:
            stmt = stmt.where(CanonicalJobModel.id != exclude_job_id)

        stmt = stmt.limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().all())


candidate_generation_engine = CandidateGenerationEngine()
