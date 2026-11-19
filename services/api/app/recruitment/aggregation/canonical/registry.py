"""Canonical Job Registry and Query Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import (
    CanonicalEmployerModel,
    CanonicalJobConflictModel,
    CanonicalJobIdentifierModel,
    CanonicalJobLocationModel,
    CanonicalJobModel,
    CanonicalJobSourceLinkModel,
)
from app.recruitment.aggregation.canonical.history import job_version_history_manager
from app.recruitment.aggregation.contracts import (
    CanonicalJobConflictRecord,
    CanonicalJobIdentifierRecord,
    CanonicalJobLocationRecord,
    CanonicalJobRecord,
    CanonicalJobSourceLinkRecord,
    CanonicalJobStatus,
    ConflictState,
    JobIdentityStatus,
)
from app.recruitment.aggregation.normalization.titles import normalize_title


class CanonicalJobRegistry:
    """Repository and query coordinator for canonical job records."""

    async def get_by_id(self, session: AsyncSession, job_id: str) -> Optional[CanonicalJobModel]:
        stmt = (
            select(CanonicalJobModel)
            .options(
                joinedload(CanonicalJobModel.employer),
                joinedload(CanonicalJobModel.source_links),
                joinedload(CanonicalJobModel.locations),
                joinedload(CanonicalJobModel.identifiers),
                joinedload(CanonicalJobModel.conflicts),
            )
            .where(CanonicalJobModel.id == job_id)
        )
        res = await session.execute(stmt)
        return res.unique().scalar_one_or_none()

    async def create_canonical_job(
        self,
        session: AsyncSession,
        title: str,
        employer_id: Optional[str] = None,
        requisition_id: Optional[str] = None,
        employment_type: Optional[str] = None,
        location_summary: Optional[str] = None,
        work_arrangement: Optional[str] = None,
        description_reference: Optional[str] = None,
        compensation_summary: Optional[str] = None,
        primary_source_id: Optional[str] = None,
        primary_url: Optional[str] = None,
        identity_status: JobIdentityStatus = JobIdentityStatus.PROBABLE,
    ) -> CanonicalJobModel:
        now = datetime.now(UTC)
        job = CanonicalJobModel(
            employer_id=employer_id,
            display_title=title.strip(),
            normalized_title=normalize_title(title),
            requisition_id=requisition_id,
            employment_type=employment_type,
            location_summary=location_summary,
            work_arrangement=work_arrangement,
            description_reference=description_reference,
            compensation_summary=compensation_summary,
            status=CanonicalJobStatus.ACTIVE.value,
            first_observed_at=now,
            last_observed_at=now,
            last_verified_active_at=now,
            version=1,
            source_count=1,
            identity_status=identity_status.value,
            conflict_state=ConflictState.NO_CONFLICT.value,
            primary_source_id=primary_source_id,
            primary_url=primary_url,
            created_at=now,
            updated_at=now,
        )
        session.add(job)
        await session.flush()

        # Record initial version
        await job_version_history_manager.record_version(
            session=session,
            job=job,
            change_summary="Initial canonical job created from discovery observation",
        )

        return job

    async def list_jobs(
        self,
        session: AsyncSession,
        query: Optional[str] = None,
        status: Optional[str] = None,
        employer_id: Optional[str] = None,
        work_arrangement: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CanonicalJobModel]:
        stmt = (
            select(CanonicalJobModel)
            .options(
                joinedload(CanonicalJobModel.employer),
                joinedload(CanonicalJobModel.source_links),
                joinedload(CanonicalJobModel.locations),
                joinedload(CanonicalJobModel.identifiers),
                joinedload(CanonicalJobModel.conflicts),
            )
        )
        if status:
            stmt = stmt.where(CanonicalJobModel.status == status)
        if employer_id:
            stmt = stmt.where(CanonicalJobModel.employer_id == employer_id)
        if work_arrangement:
            stmt = stmt.where(CanonicalJobModel.work_arrangement == work_arrangement)
        if query:
            stmt = stmt.where(
                or_(
                    CanonicalJobModel.display_title.ilike(f"%{query.strip()}%"),
                    CanonicalJobModel.location_summary.ilike(f"%{query.strip()}%"),
                )
            )

        stmt = stmt.order_by(CanonicalJobModel.updated_at.desc()).limit(limit).offset(offset)
        res = await session.execute(stmt)
        return list(res.unique().scalars().all())

    def to_contract(self, job: CanonicalJobModel) -> CanonicalJobRecord:
        """Convert ORM model to Pydantic contract safely without triggering lazy-load IO."""
        source_links_list = job.__dict__.get("source_links") or []
        locations_list = job.__dict__.get("locations") or []
        identifiers_list = job.__dict__.get("identifiers") or []
        conflicts_list = job.__dict__.get("conflicts") or []
        employer_obj = job.__dict__.get("employer")

        sources = [
            CanonicalJobSourceLinkRecord(
                id=link.id,
                canonical_job_id=link.canonical_job_id,
                listing_id=link.listing_id,
                source_observation_id=link.source_observation_id,
                source_id=link.source_id,
                provider=link.provider,
                native_posting_id=link.native_posting_id,
                original_url=link.original_url,
                application_url=link.application_url,
                association_status=link.association_status,
                decision_method=link.decision_method,
                evidence=link.evidence_json or {},
                is_primary=link.is_primary,
                created_at=link.created_at.isoformat() if hasattr(link.created_at, "isoformat") else str(link.created_at),
            )
            for link in source_links_list
            if link.canonical_job_id == job.id and link.association_status == "active"
        ]

        locations = [
            CanonicalJobLocationRecord(
                id=loc.id,
                country=loc.country,
                region=loc.region,
                city=loc.city,
                office=loc.office,
                is_remote=loc.is_remote,
                workplace_type=loc.workplace_type,
                raw_text=loc.raw_text,
                source_id=loc.source_id,
            )
            for loc in locations_list
        ]

        identifiers = [
            CanonicalJobIdentifierRecord(
                id=ident.id,
                id_type=ident.id_type,
                raw_id=ident.raw_id,
                normalized_id=ident.normalized_id,
                namespace=ident.namespace,
                source_id=ident.source_id,
            )
            for ident in identifiers_list
        ]

        conflicts = [
            CanonicalJobConflictRecord(
                id=conf.id,
                field_name=conf.field_name,
                conflict_type=conf.conflict_type,
                status=conf.status,
                source_values=conf.source_values_json or {},
                resolution_note=conf.resolution_note,
                resolved_by=conf.resolved_by,
                resolved_at=conf.resolved_at.isoformat() if conf.resolved_at else None,
            )
            for conf in conflicts_list
        ]

        emp_name = employer_obj.name if employer_obj else "Unknown Employer"

        return CanonicalJobRecord(
            id=job.id,
            employer_id=job.employer_id,
            employer_name=emp_name,
            display_title=job.display_title,
            normalized_title=job.normalized_title,
            requisition_id=job.requisition_id,
            employment_type=job.employment_type,
            location_summary=job.location_summary,
            work_arrangement=job.work_arrangement,
            description_reference=job.description_reference,
            compensation_summary=job.compensation_summary,
            status=job.status,
            first_observed_at=job.first_observed_at.isoformat() if hasattr(job.first_observed_at, "isoformat") else str(job.first_observed_at),
            last_observed_at=job.last_observed_at.isoformat() if hasattr(job.last_observed_at, "isoformat") else str(job.last_observed_at),
            last_verified_active_at=job.last_verified_active_at.isoformat() if job.last_verified_active_at else None,
            version=job.version,
            source_count=job.source_count,
            identity_status=job.identity_status,
            conflict_state=job.conflict_state,
            primary_source_id=job.primary_source_id,
            primary_url=job.primary_url,
            is_evergreen=job.is_evergreen,
            is_repost=job.is_repost,
            sources=sources,
            locations=locations,
            identifiers=identifiers,
            conflicts=conflicts,
            created_at=job.created_at.isoformat() if hasattr(job.created_at, "isoformat") else str(job.created_at),
            updated_at=job.updated_at.isoformat() if hasattr(job.updated_at, "isoformat") else str(job.updated_at),
        )


canonical_job_registry = CanonicalJobRegistry()
