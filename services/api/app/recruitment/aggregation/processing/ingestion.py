"""Observation Ingestion & Aggregation Pipeline Coordinator (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import (
    CanonicalEmployerModel,
    CanonicalJobIdentifierModel,
    CanonicalJobLocationModel,
    CanonicalJobModel,
    CanonicalJobSourceLinkModel,
)
from app.recruitment.aggregation.canonical.conflicts import field_conflict_manager
from app.recruitment.aggregation.canonical.fields import field_candidate_manager
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.canonical.source_links import source_link_manager
from app.recruitment.aggregation.contracts import CanonicalJobRecord, DuplicateAction
from app.recruitment.aggregation.employers.identity import employer_identity_resolver
from app.recruitment.aggregation.matching.candidate_generation import candidate_generation_engine
from app.recruitment.aggregation.matching.decisions import duplicate_decision_manager
from app.recruitment.aggregation.matching.duplicate_assessment import assess_duplicate_candidate
from app.recruitment.aggregation.normalization.employment import normalize_employment_type
from app.recruitment.aggregation.normalization.identifiers import extract_requisition_id
from app.recruitment.aggregation.normalization.locations import normalize_workplace_type
from app.recruitment.aggregation.normalization.urls import normalize_job_url


class ObservationIngestionPipeline:
    """End-to-end ingestion pipeline turning raw observations into canonical jobs."""

    async def ingest_observation(
        self,
        session: AsyncSession,
        observation_id: str,
        source_id: str,
        provider: str,
        native_posting_id: str,
        title: str,
        employer_name: str,
        source_url: str,
        application_url: Optional[str] = None,
        location_raw: Optional[str] = None,
        workplace_type: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_raw: Optional[str] = None,
        description_text: Optional[str] = None,
        posted_at: Optional[str] = None,
        listing_id: Optional[str] = None,
        auto_merge_enabled: bool = True,
    ) -> tuple[CanonicalJobModel, bool]:
        """Ingest one source observation. Returns (canonical_job, was_merged_into_existing)."""
        clean_url = normalize_job_url(source_url)
        clean_app_url = normalize_job_url(application_url) if application_url else clean_url
        req_id = extract_requisition_id(title, description_text, native_posting_id)
        norm_emp_type = normalize_employment_type(employment_type)
        norm_wp_type = normalize_workplace_type(workplace_type, location_raw)

        # 1. Check if this exact source observation is already linked to a canonical job (Idempotency!)
        stmt_link = (
            select(CanonicalJobSourceLinkModel)
            .where(
                CanonicalJobSourceLinkModel.source_observation_id == observation_id,
                CanonicalJobSourceLinkModel.association_status == "active",
            )
        )
        res_link = await session.execute(stmt_link)
        existing_link = res_link.scalar_one_or_none()
        if existing_link:
            existing_job = await canonical_job_registry.get_by_id(session, existing_link.canonical_job_id)
            if existing_job:
                return existing_job, False

        # 2. Resolve Employer Identity
        employer, _ = await employer_identity_resolver.resolve_employer(
            session=session,
            raw_name=employer_name,
            source_url=clean_url,
            provider=provider,
            description=description_text,
        )

        # 3. Find Duplicate Candidates using Blocking Keys
        candidates = await candidate_generation_engine.find_candidates_for_job(
            session=session,
            employer_id=employer.id,
            title=title,
            requisition_id=req_id,
        )

        # 4. Assess Candidates & Check Auto-Merge Eligibility
        merged_target: Optional[CanonicalJobModel] = None

        if candidates:
            # Create a temporary synthetic comparison job model
            temp_job = CanonicalJobModel(
                id=f"temp_{observation_id}",
                employer_id=employer.id,
                display_title=title,
                normalized_title=title.lower().strip(),
                requisition_id=req_id,
                employment_type=norm_emp_type,
                location_summary=location_raw,
                work_arrangement=norm_wp_type,
                description_reference=description_text,
                compensation_summary=salary_raw,
                primary_url=clean_url,
            )

            for cand in candidates:
                assessment = assess_duplicate_candidate(cand, temp_job)

                if assessment.recommended_action == DuplicateAction.MERGE and auto_merge_enabled:
                    # Deterministic match passes! Merge into this existing canonical job
                    merged_target = cand
                    break
                elif assessment.review_required:
                    # Ambiguous duplicate -> record candidate for human review
                    await duplicate_decision_manager.record_candidate(session, assessment)

        # 5. Link to Merged Target or Create New Canonical Job
        if merged_target:
            # Merge into existing
            link = await source_link_manager.link_source(
                session=session,
                canonical_job_id=merged_target.id,
                source_observation_id=observation_id,
                source_id=source_id,
                provider=provider,
                native_posting_id=native_posting_id,
                original_url=clean_url,
                application_url=clean_app_url,
                listing_id=listing_id,
                decision_method="auto_merge_deterministic",
                is_primary=False,
            )

            # Record field candidates
            if salary_raw:
                await field_candidate_manager.add_candidate(
                    session=session,
                    canonical_job_id=merged_target.id,
                    source_link_id=link.id,
                    field_name="compensation_summary",
                    candidate_value=salary_raw,
                )
            if location_raw:
                await field_candidate_manager.add_candidate(
                    session=session,
                    canonical_job_id=merged_target.id,
                    source_link_id=link.id,
                    field_name="location_summary",
                    candidate_value=location_raw,
                )

            # Check for multi-source field conflicts
            field_data = {
                merged_target.primary_source_id or "primary": {
                    "salary": merged_target.compensation_summary,
                    "work_arrangement": merged_target.work_arrangement,
                },
                source_id: {
                    "salary": salary_raw,
                    "work_arrangement": norm_wp_type,
                },
            }
            conflicts = await field_conflict_manager.detect_conflicts(
                session=session,
                canonical_job_id=merged_target.id,
                field_values_by_source=field_data,
            )
            if conflicts:
                merged_target.conflict_state = "has_conflicts"

            merged_target.source_count += 1
            merged_target.last_observed_at = datetime.now(UTC)
            merged_target.version += 1
            await session.flush()
            return merged_target, True

        else:
            # Create fresh canonical job
            new_job = await canonical_job_registry.create_canonical_job(
                session=session,
                title=title,
                employer_id=employer.id,
                requisition_id=req_id,
                employment_type=norm_emp_type,
                location_summary=location_raw,
                work_arrangement=norm_wp_type,
                description_reference=description_text,
                compensation_summary=salary_raw,
                primary_source_id=source_id,
                primary_url=clean_url,
            )

            # Link primary source
            link = await source_link_manager.link_source(
                session=session,
                canonical_job_id=new_job.id,
                source_observation_id=observation_id,
                source_id=source_id,
                provider=provider,
                native_posting_id=native_posting_id,
                original_url=clean_url,
                application_url=clean_app_url,
                listing_id=listing_id,
                decision_method="initial_discovery",
                is_primary=True,
            )

            # Add Location Record
            loc = CanonicalJobLocationModel(
                canonical_job_id=new_job.id,
                city=location_raw,
                is_remote=(norm_wp_type == "remote"),
                workplace_type=norm_wp_type,
                raw_text=location_raw,
                source_id=source_id,
            )
            session.add(loc)

            # Add Identifier Record
            if req_id:
                ident = CanonicalJobIdentifierModel(
                    canonical_job_id=new_job.id,
                    id_type="requisition_id",
                    raw_id=req_id,
                    normalized_id=req_id,
                    namespace=provider,
                    source_id=source_id,
                )
                session.add(ident)

            await session.flush()
            return new_job, False


observation_ingestion_pipeline = ObservationIngestionPipeline()
