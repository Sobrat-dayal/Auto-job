"""Internal agent capabilities for Job Intelligence (Stage 28).

Registers typed callable capabilities for autonomous recruitment agents:
- JobDiscoveryAgent
- JobIntelligenceSpecialist
- VerificationAgent
- JobMatchingAgent (Read-Only)
- Supervisor
"""

from typing import Any

from app.recruitment.intelligence.contracts import (
    AnalysisStatus,
    AtomicRequirement,
    JobIntelligenceRecord,
    RequirementCategory,
)
from app.recruitment.intelligence.service import job_intelligence_service


async def capability_analyze_job(canonical_job_id: str, force: bool = False, use_ai: bool = True) -> dict[str, Any]:
    """Execute job intelligence analysis for a single canonical job."""
    record = await job_intelligence_service.analyze_job(canonical_job_id, force=force, use_ai=use_ai)
    return record.model_dump(mode="json")


async def capability_analyze_batch(job_ids: list[str], use_ai: bool = False) -> list[dict[str, Any]]:
    """Execute batch job intelligence analysis."""
    records = await job_intelligence_service.analyze_batch(job_ids, use_ai=use_ai)
    return [r.model_dump(mode="json") for r in records]


async def capability_get_record(canonical_job_id: str) -> dict[str, Any] | None:
    """Fetch structured intelligence record for a job."""
    record = await job_intelligence_service.get_record(canonical_job_id)
    return record.model_dump(mode="json") if record else None


async def capability_get_requirements(canonical_job_id: str, category: str | None = None) -> list[dict[str, Any]]:
    """Fetch atomic requirements for a job, optionally filtered by category."""
    cat_enum = RequirementCategory(category) if category else None
    reqs = await job_intelligence_service.get_requirements(canonical_job_id, category=cat_enum)
    return [r.model_dump(mode="json") for r in reqs]


async def capability_get_skills(canonical_job_id: str) -> list[dict[str, Any]]:
    """Fetch structured skills for a job."""
    skills = await job_intelligence_service.get_skills(canonical_job_id)
    return [s.model_dump(mode="json") for s in skills]


async def capability_get_education(canonical_job_id: str) -> list[dict[str, Any]]:
    """Fetch education requirements for a job."""
    edu = await job_intelligence_service.get_education(canonical_job_id)
    return [e.model_dump(mode="json") for e in edu]


async def capability_get_experience(canonical_job_id: str) -> list[dict[str, Any]]:
    """Fetch experience requirements for a job."""
    exp = await job_intelligence_service.get_experience(canonical_job_id)
    return [e.model_dump(mode="json") for e in exp]


async def capability_get_compensation(canonical_job_id: str) -> dict[str, Any]:
    """Fetch compensation intelligence for a job."""
    comp = await job_intelligence_service.get_compensation(canonical_job_id)
    return comp.model_dump(mode="json")


async def capability_get_conditions(canonical_job_id: str) -> dict[str, Any]:
    """Fetch employment and workplace conditions for a job."""
    cond = await job_intelligence_service.get_employment(canonical_job_id)
    return cond.model_dump(mode="json")


async def capability_get_deadlines(canonical_job_id: str) -> dict[str, Any]:
    """Fetch application deadlines and instructions for a job."""
    deadlines = await job_intelligence_service.get_deadlines(canonical_job_id)
    return deadlines.model_dump(mode="json")


async def capability_get_evidence(canonical_job_id: str) -> list[dict[str, Any]]:
    """Fetch provenance evidence for a job."""
    ev = await job_intelligence_service.get_evidence(canonical_job_id)
    return [e.model_dump(mode="json") for e in ev]


async def capability_get_conflicts(canonical_job_id: str) -> list[dict[str, Any]]:
    """Fetch multi-source requirement conflicts for a job."""
    conflicts = await job_intelligence_service.get_conflicts(canonical_job_id)
    return [c.model_dump(mode="json") for c in conflicts]


async def capability_get_status() -> dict[str, Any]:
    """Fetch overall diagnostic and operational status."""
    return await job_intelligence_service.get_diagnostics()


# Registry mapping
JOB_INTELLIGENCE_CAPABILITIES = {
    "job.intelligence.analyze": capability_analyze_job,
    "job.intelligence.analyze_batch": capability_analyze_batch,
    "job.intelligence.get_record": capability_get_record,
    "job.intelligence.get_requirements": capability_get_requirements,
    "job.intelligence.get_skills": capability_get_skills,
    "job.intelligence.get_education": capability_get_education,
    "job.intelligence.get_experience": capability_get_experience,
    "job.intelligence.get_compensation": capability_get_compensation,
    "job.intelligence.get_conditions": capability_get_conditions,
    "job.intelligence.get_deadlines": capability_get_deadlines,
    "job.intelligence.get_evidence": capability_get_evidence,
    "job.intelligence.get_conflicts": capability_get_conflicts,
    "job.intelligence.get_status": capability_get_status,
}
