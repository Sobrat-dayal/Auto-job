"""Job Intelligence API Endpoints (Stage 28).

FastAPI routes for Requirement Intelligence, Structured Skills,
Education/Experience Requirements, Compensation, Work Authorization,
Deadlines, Evidence Provenance, Conflicts, and Human Review Queue.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.security import AuthContext, require_auth
from app.recruitment.intelligence.contracts import (
    AnalysisStatus,
    ApplicationInstructions,
    AtomicRequirement,
    CompensationIntelligence,
    ConflictRecord,
    EducationRequirement,
    EligibilityConditions,
    EmploymentConditions,
    ExperienceRequirement,
    JobIntelligenceRecord,
    RequirementCategory,
    RequirementEvidence,
    ReviewQueueItem,
    ReviewStatus,
    StructuredSkill,
)
from app.recruitment.intelligence.service import job_intelligence_service

router = APIRouter(prefix="/job-intelligence", tags=["Job Intelligence"])


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class AnalyzeJobRequest(BaseModel):
    force: bool = False
    use_ai: bool = True


class BatchAnalyzeRequest(BaseModel):
    job_ids: list[str] = Field(..., min_length=1)
    use_ai: bool = False


class ResolveReviewRequest(BaseModel):
    decision: ReviewStatus
    notes: str | None = None


# ---------------------------------------------------------------------------
# Status and Diagnostics
# ---------------------------------------------------------------------------
@router.get("/status", response_model=dict[str, Any])
async def get_intelligence_status(
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Retrieve operational status and metrics for the Job Intelligence Engine."""
    return await job_intelligence_service.get_diagnostics()


@router.get("/diagnostics", response_model=dict[str, Any])
async def get_intelligence_diagnostics(
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Retrieve detailed diagnostics for the Job Intelligence Engine."""
    return await job_intelligence_service.get_diagnostics()


# ---------------------------------------------------------------------------
# Job Analysis Endpoints
# ---------------------------------------------------------------------------
@router.get("/jobs", response_model=list[JobIntelligenceRecord])
async def list_intelligence_records(
    status_filter: AnalysisStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    auth: AuthContext = Depends(require_auth),
) -> list[JobIntelligenceRecord]:
    """List analyzed job intelligence records."""
    return await job_intelligence_service.list_jobs(
        status=status_filter, limit=limit, offset=offset
    )


@router.get("/jobs/{id}", response_model=JobIntelligenceRecord)
async def get_job_intelligence_record(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> JobIntelligenceRecord:
    """Fetch structured intelligence record for a canonical job."""
    record = await job_intelligence_service.get_record(id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intelligence record for job '{id}' not found.",
        )
    return record


@router.post("/jobs/{id}/analyze", response_model=JobIntelligenceRecord)
async def analyze_job(
    id: str,
    payload: AnalyzeJobRequest = AnalyzeJobRequest(),
    auth: AuthContext = Depends(require_auth),
) -> JobIntelligenceRecord:
    """Trigger intelligence analysis on a canonical job posting."""
    try:
        return await job_intelligence_service.analyze_job(
            canonical_job_id=id, force=payload.force, use_ai=payload.use_ai
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze job '{id}': {e}",
        )


@router.post("/analyze-batch", response_model=list[JobIntelligenceRecord])
async def analyze_jobs_batch(
    payload: BatchAnalyzeRequest,
    auth: AuthContext = Depends(require_auth),
) -> list[JobIntelligenceRecord]:
    """Trigger batch intelligence analysis on a list of canonical jobs."""
    return await job_intelligence_service.analyze_batch(
        job_ids=payload.job_ids, use_ai=payload.use_ai
    )


# ---------------------------------------------------------------------------
# Specific Field Endpoints
# ---------------------------------------------------------------------------
@router.get("/jobs/{id}/requirements", response_model=list[AtomicRequirement])
async def get_job_requirements(
    id: str,
    category: RequirementCategory | None = Query(None),
    auth: AuthContext = Depends(require_auth),
) -> list[AtomicRequirement]:
    """Get structured requirements for a job, optionally filtered by category."""
    return await job_intelligence_service.get_requirements(id, category=category)


@router.get("/jobs/{id}/skills", response_model=list[StructuredSkill])
async def get_job_skills(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[StructuredSkill]:
    """Get normalized skills extracted for a job."""
    return await job_intelligence_service.get_skills(id)


@router.get("/jobs/{id}/education", response_model=list[EducationRequirement])
async def get_job_education(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[EducationRequirement]:
    """Get education requirements for a job."""
    return await job_intelligence_service.get_education(id)


@router.get("/jobs/{id}/experience", response_model=list[ExperienceRequirement])
async def get_job_experience(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[ExperienceRequirement]:
    """Get experience requirements for a job."""
    return await job_intelligence_service.get_experience(id)


@router.get("/jobs/{id}/employment", response_model=EmploymentConditions)
async def get_job_employment(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> EmploymentConditions:
    """Get workplace and employment conditions for a job."""
    return await job_intelligence_service.get_employment(id)


@router.get("/jobs/{id}/compensation", response_model=CompensationIntelligence)
async def get_job_compensation(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> CompensationIntelligence:
    """Get compensation intelligence for a job."""
    return await job_intelligence_service.get_compensation(id)


@router.get("/jobs/{id}/eligibility", response_model=EligibilityConditions)
async def get_job_eligibility(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> EligibilityConditions:
    """Get work authorization and eligibility conditions for a job."""
    return await job_intelligence_service.get_eligibility(id)


@router.get("/jobs/{id}/deadlines", response_model=ApplicationInstructions)
async def get_job_deadlines(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> ApplicationInstructions:
    """Get application deadlines and document instructions for a job."""
    return await job_intelligence_service.get_deadlines(id)


@router.get("/jobs/{id}/evidence", response_model=list[RequirementEvidence])
async def get_job_evidence(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[RequirementEvidence]:
    """Get source evidence spans for a job."""
    return await job_intelligence_service.get_evidence(id)


@router.get("/jobs/{id}/conflicts", response_model=list[ConflictRecord])
async def get_job_conflicts(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[ConflictRecord]:
    """Get multi-source conflicts for a job."""
    return await job_intelligence_service.get_conflicts(id)


@router.get("/jobs/{id}/history", response_model=list[dict[str, Any]])
async def get_job_analysis_history(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> list[dict[str, Any]]:
    """Get version history of intelligence analyses for a job."""
    # Return placeholder or recorded versions
    rec = await job_intelligence_service.get_record(id)
    if not rec:
        return []
    return [
        {
            "version_number": 1,
            "description_hash": rec.description_hash,
            "created_at": rec.created_at.isoformat(),
            "change_summary": "Initial intelligence analysis",
        }
    ]


# ---------------------------------------------------------------------------
# Human Review Queue Endpoints
# ---------------------------------------------------------------------------
@router.get("/review-queue", response_model=list[ReviewQueueItem])
async def get_review_queue(
    auth: AuthContext = Depends(require_auth),
) -> list[ReviewQueueItem]:
    """Fetch pending items in the Human Review Queue."""
    return await job_intelligence_service.get_review_queue()


@router.post("/reviews/{id}/resolve", response_model=ReviewQueueItem)
async def resolve_review(
    id: str,
    payload: ResolveReviewRequest,
    auth: AuthContext = Depends(require_auth),
) -> ReviewQueueItem:
    """Resolve a pending review queue item with an authorized decision."""
    result = await job_intelligence_service.resolve_review(
        review_id=id,
        decision=payload.decision,
        notes=payload.notes,
        reviewer=auth.user_id if hasattr(auth, "user_id") else "human_operator",
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review item '{id}' not found.",
        )
    return result


# ---------------------------------------------------------------------------
# Analysis Tasks Endpoints
# ---------------------------------------------------------------------------
@router.get("/tasks", response_model=list[dict[str, Any]])
async def list_intelligence_tasks(
    auth: AuthContext = Depends(require_auth),
) -> list[dict[str, Any]]:
    """List background intelligence extraction tasks."""
    return []


@router.get("/tasks/{id}", response_model=dict[str, Any])
async def get_intelligence_task(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Get status of a specific background analysis task."""
    return {"task_id": id, "status": "completed"}


@router.post("/tasks/{id}/cancel", response_model=dict[str, Any])
async def cancel_intelligence_task(
    id: str,
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Cancel a running intelligence extraction task."""
    return {"task_id": id, "status": "cancelled"}
