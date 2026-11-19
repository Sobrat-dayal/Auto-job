"""Canonical Job Source Association Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobSourceLinkModel


class SourceLinkManager:
    """Manages associations between source observations and canonical jobs."""

    async def link_source(
        self,
        session: AsyncSession,
        canonical_job_id: str,
        source_observation_id: str,
        source_id: str,
        provider: str,
        native_posting_id: str,
        original_url: str,
        application_url: Optional[str] = None,
        listing_id: Optional[str] = None,
        decision_method: str = "exact_rule",
        evidence: Optional[dict[str, Any]] = None,
        is_primary: bool = False,
    ) -> CanonicalJobSourceLinkModel:
        # Check if already linked to this canonical job
        stmt = select(CanonicalJobSourceLinkModel).where(
            CanonicalJobSourceLinkModel.canonical_job_id == canonical_job_id,
            CanonicalJobSourceLinkModel.source_observation_id == source_observation_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.original_url = original_url
            if application_url:
                existing.application_url = application_url
            if is_primary:
                existing.is_primary = True
            return existing

        link = CanonicalJobSourceLinkModel(
            canonical_job_id=canonical_job_id,
            listing_id=listing_id,
            source_observation_id=source_observation_id,
            source_id=source_id,
            provider=provider,
            native_posting_id=native_posting_id,
            original_url=original_url,
            application_url=application_url,
            association_status="active",
            decision_method=decision_method,
            evidence_json=evidence or {},
            is_primary=is_primary,
            created_at=datetime.now(UTC),
        )
        session.add(link)
        await session.flush()
        return link

    async def list_links_for_job(
        self,
        session: AsyncSession,
        canonical_job_id: str,
    ) -> list[CanonicalJobSourceLinkModel]:
        stmt = select(CanonicalJobSourceLinkModel).where(
            CanonicalJobSourceLinkModel.canonical_job_id == canonical_job_id,
            CanonicalJobSourceLinkModel.association_status == "active",
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())


source_link_manager = SourceLinkManager()
