"""Job Intelligence resolver for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.recruitment.intelligence.service import job_intelligence_service
from app.recruitment.matching.contracts import JobIntelligenceSnapshotData
from app.recruitment.matching.errors import JobIntelligenceNotFoundError

logger = logging.getLogger("autonom.recruitment.matching.inputs.job_intelligence")


async def resolve_job_intelligence(
    canonical_job_id: str,
    db_session: AsyncSession,
    auto_analyze: bool = True,
) -> JobIntelligenceSnapshotData:
    """Loads or executes Stage 28 structured requirements for a canonical job."""
    record = await job_intelligence_service.get_record(canonical_job_id)

    if not record and auto_analyze:
        try:
            logger.info(f"Auto-triggering intelligence analysis for job '{canonical_job_id}'")
            record = await job_intelligence_service.analyze_job(
                canonical_job_id=canonical_job_id,
                force=False,
                use_ai=False,  # Fallback deterministic execution
                db_session=db_session,
            )
        except Exception as exc:
            logger.error(f"Intelligence extraction failed for job '{canonical_job_id}': {exc}")
            raise JobIntelligenceNotFoundError(f"Job requirements analysis failed for '{canonical_job_id}'.") from exc

    if not record:
        raise JobIntelligenceNotFoundError(f"Structured job intelligence not found for '{canonical_job_id}'.")

    # Serialize requirements to dict format
    mandatory_reqs = [r.model_dump(mode="json") for r in record.mandatory_requirements]
    preferred_reqs = [r.model_dump(mode="json") for r in record.preferred_requirements]
    optional_reqs = [r.model_dump(mode="json") for r in record.optional_requirements]
    conditional_reqs = [r.model_dump(mode="json") for r in record.conditional_requirements]
    groups = [g.model_dump(mode="json") for g in record.requirement_groups]
    skills = [s.model_dump(mode="json") for s in record.skills]
    education = [e.model_dump(mode="json") for e in record.education]
    experience = [exp.model_dump(mode="json") for exp in record.experience]

    return JobIntelligenceSnapshotData(
        canonical_job_id=record.canonical_job_id,
        canonical_job_version=record.canonical_job_version,
        job_title=record.job_title,
        company_name="Employer",  # Will be populated with canonical job company name
        job_location=None,
        employment_type=record.employment_conditions.employment_type.value if record.employment_conditions.employment_type else None,
        work_arrangement=record.employment_conditions.workplace_type.value if record.employment_conditions.workplace_type else None,
        status="active",
        discovered_at=record.created_at.isoformat(),
        role_family=record.role_family,
        seniority=record.seniority,
        mandatory_requirements=mandatory_reqs,
        preferred_requirements=preferred_reqs,
        optional_requirements=optional_reqs,
        conditional_requirements=conditional_reqs,
        requirement_groups=groups,
        skills=skills,
        education=education,
        experience=experience,
        employment_conditions=record.employment_conditions.model_dump(mode="json"),
        compensation=record.compensation.model_dump(mode="json"),
        eligibility=record.eligibility.model_dump(mode="json"),
        deadlines=record.application_instructions.model_dump(mode="json"),
    )
