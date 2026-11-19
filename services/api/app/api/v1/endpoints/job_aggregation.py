"""FastAPI endpoints for Job Aggregation & Canonical Database Engine (Stage 27)."""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthDep, get_session
from app.db.models import (
    AggregationTaskModel,
    CanonicalJobConflictModel,
    CanonicalJobModel,
    CanonicalJobRelationshipModel,
    CanonicalJobVersionModel,
    EmployerIdentityDecisionModel,
    JobDuplicateCandidateModel,
)
from app.recruitment.aggregation.contracts import (
    AggregationDiagnosticsReport,
    AggregationOverviewStats,
    AggregationSettingsConfig,
    AggregationTaskRecord,
    CanonicalEmployerRecord,
    CanonicalJobConflictRecord,
    CanonicalJobRecord,
    CanonicalJobSourceLinkRecord,
    ConflictResolveRequest,
    DuplicateAction,
    DuplicateCandidateRecord,
    DuplicateReviewSubmitRequest,
    EmployerCorrectionRequest,
    MergeExecuteRequest,
    MergeExecuteResponse,
    MergePreviewRequest,
    MergePreviewResponse,
    SplitExecuteRequest,
    SplitExecuteResponse,
    SplitPreviewResponse,
)
from app.recruitment.aggregation.errors import (
    CanonicalEmployerNotFoundError,
    CanonicalJobNotFoundError,
    CircularMergeError,
    MergeValidationError,
    SplitValidationError,
)
from app.recruitment.aggregation.integrations.authorization import verify_aggregation_permission
from app.recruitment.aggregation.service import job_aggregation_service

router = APIRouter(prefix="/job-aggregation", tags=["job-aggregation"])


# -----------------------------------------------------------------------------
# Overview & Diagnostics
# -----------------------------------------------------------------------------
@router.get("/status", response_model=AggregationOverviewStats)
async def get_aggregation_status(
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
) -> AggregationOverviewStats:
    verify_aggregation_permission(auth, "read_canonical")
    return await job_aggregation_service.get_overview_stats(session)


@router.get("/diagnostics", response_model=AggregationDiagnosticsReport)
async def get_aggregation_diagnostics(
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
) -> AggregationDiagnosticsReport:
    verify_aggregation_permission(auth, "read_canonical")
    return await job_aggregation_service.get_diagnostics(session)


# -----------------------------------------------------------------------------
# Canonical Jobs
# -----------------------------------------------------------------------------
@router.get("/jobs", response_model=list[CanonicalJobRecord])
async def list_canonical_jobs(
    auth: AuthDep,
    query: Optional[str] = Query(None, description="Search title or location"),
    status: Optional[str] = Query(None, description="Job posting status filter"),
    employer_id: Optional[str] = Query(None, description="Employer filter"),
    work_arrangement: Optional[str] = Query(None, description="Work arrangement (remote, hybrid, onsite)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalJobRecord]:
    verify_aggregation_permission(auth, "read_canonical")
    return await job_aggregation_service.list_jobs(
        session=session,
        query=query,
        status=status,
        employer_id=employer_id,
        work_arrangement=work_arrangement,
        limit=limit,
        offset=offset,
    )


@router.get("/jobs/{job_id}", response_model=CanonicalJobRecord)
async def get_canonical_job(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> CanonicalJobRecord:
    verify_aggregation_permission(auth, "read_canonical")
    job = await job_aggregation_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Canonical job {job_id} not found")
    return job


@router.get("/jobs/{job_id}/sources", response_model=list[CanonicalJobSourceLinkRecord])
async def get_canonical_job_sources(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalJobSourceLinkRecord]:
    verify_aggregation_permission(auth, "read_canonical")
    job = await job_aggregation_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Canonical job {job_id} not found")
    return job.sources


@router.get("/jobs/{job_id}/history", response_model=list[dict[str, Any]])
async def get_canonical_job_history(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    verify_aggregation_permission(auth, "read_canonical")
    stmt = (
        select(CanonicalJobVersionModel)
        .where(CanonicalJobVersionModel.canonical_job_id == job_id)
        .order_by(CanonicalJobVersionModel.version_number.desc())
    )
    res = await session.execute(stmt)
    versions = res.scalars().all()
    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "change_summary": v.change_summary,
            "created_at": v.created_at.isoformat(),
            "snapshot": v.snapshot_json,
        }
        for v in versions
    ]


@router.get("/jobs/{job_id}/conflicts", response_model=list[CanonicalJobConflictRecord])
async def get_canonical_job_conflicts(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalJobConflictRecord]:
    verify_aggregation_permission(auth, "read_canonical")
    job = await job_aggregation_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Canonical job {job_id} not found")
    return job.conflicts


@router.get("/jobs/{job_id}/relationships", response_model=list[dict[str, Any]])
async def get_canonical_job_relationships(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    verify_aggregation_permission(auth, "read_canonical")
    stmt = select(CanonicalJobRelationshipModel).where(
        CanonicalJobRelationshipModel.canonical_job_id == job_id
    )
    res = await session.execute(stmt)
    rels = res.scalars().all()
    return [
        {
            "id": r.id,
            "related_job_id": r.related_job_id,
            "relationship_type": r.relationship_type,
            "confidence": r.confidence,
            "notes": r.notes,
            "created_at": r.created_at.isoformat(),
        }
        for r in rels
    ]


# -----------------------------------------------------------------------------
# Ingestion & Sync
# -----------------------------------------------------------------------------
@router.post("/process", response_model=CanonicalJobRecord)
async def process_observation(
    auth: AuthDep,
    observation: dict[str, Any],
    auto_merge: bool = Query(True, description="Enable automatic merging of exact matches"),
    session: AsyncSession = Depends(get_session),
) -> CanonicalJobRecord:
    verify_aggregation_permission(auth, "create_canonical")
    return await job_aggregation_service.process_observation(session, observation, auto_merge=auto_merge)


@router.post("/process-batch", response_model=AggregationTaskRecord)
async def process_batch_observations(
    auth: AuthDep,
    observations: list[dict[str, Any]],
    auto_merge: bool = Query(True, description="Enable automatic merging of exact matches"),
    session: AsyncSession = Depends(get_session),
) -> AggregationTaskRecord:
    verify_aggregation_permission(auth, "create_canonical")
    return await job_aggregation_service.process_batch(session, observations, auto_merge=auto_merge)


@router.post("/sync-from-discovery", response_model=AggregationTaskRecord)
async def sync_from_discovery(
    auth: AuthDep,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> AggregationTaskRecord:
    verify_aggregation_permission(auth, "create_canonical")
    return await job_aggregation_service.sync_from_discovery(session, limit=limit)


# -----------------------------------------------------------------------------
# Tasks
# -----------------------------------------------------------------------------
@router.get("/tasks", response_model=list[dict[str, Any]])
async def list_aggregation_tasks(
    auth: AuthDep,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    verify_aggregation_permission(auth, "read_canonical")
    stmt = select(AggregationTaskModel).order_by(AggregationTaskModel.created_at.desc()).limit(limit)
    res = await session.execute(stmt)
    tasks = res.scalars().all()
    return [
        {
            "id": t.id,
            "task_type": t.task_type,
            "status": t.status,
            "observations_total": t.observations_total,
            "observations_processed": t.observations_processed,
            "canonical_jobs_created": t.canonical_jobs_created,
            "merges_performed": t.merges_performed,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat(),
        }
        for t in tasks
    ]


# -----------------------------------------------------------------------------
# Duplicate Detection & Review Queue
# -----------------------------------------------------------------------------
@router.get("/duplicates", response_model=list[DuplicateCandidateRecord])
async def list_duplicate_candidates(
    auth: AuthDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[DuplicateCandidateRecord]:
    verify_aggregation_permission(auth, "duplicate_review")
    return await job_aggregation_service.list_duplicate_reviews(session, limit=limit, offset=offset)


@router.get("/duplicates/{candidate_id}", response_model=DuplicateCandidateRecord)
async def get_duplicate_candidate(
    auth: AuthDep,
    candidate_id: str,
    session: AsyncSession = Depends(get_session),
) -> DuplicateCandidateRecord:
    verify_aggregation_permission(auth, "duplicate_review")
    stmt = select(JobDuplicateCandidateModel).where(JobDuplicateCandidateModel.id == candidate_id)
    res = await session.execute(stmt)
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Duplicate candidate {candidate_id} not found")
    return DuplicateCandidateRecord(
        id=c.id,
        left_job_id=c.left_job_id,
        right_job_id=c.right_job_id,
        status=c.status,
        similarity_score=c.similarity_score,
        matching_factors=c.matching_factors_json or {},
        contradictions=c.contradictions_json or {},
        recommended_action=c.recommended_action,
        created_at=c.created_at.isoformat(),
    )


@router.post("/duplicates/{candidate_id}/review", response_model=dict[str, Any])
async def submit_duplicate_review(
    auth: AuthDep,
    candidate_id: str,
    req: DuplicateReviewSubmitRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    verify_aggregation_permission(auth, "duplicate_review")
    success = await job_aggregation_service.submit_duplicate_review(
        session=session,
        candidate_id=candidate_id,
        decision=req.decision,
        reason=req.reason,
        decided_by=req.decided_by,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Candidate {candidate_id} not found")
    return {"status": "success", "decision": req.decision.value}


# -----------------------------------------------------------------------------
# Merge and Split Operations
# -----------------------------------------------------------------------------
@router.post("/jobs/merge-preview", response_model=MergePreviewResponse)
async def preview_job_merge(
    auth: AuthDep,
    req: MergePreviewRequest,
    session: AsyncSession = Depends(get_session),
) -> MergePreviewResponse:
    verify_aggregation_permission(auth, "merge_jobs")
    try:
        return await job_aggregation_service.preview_merge(
            session=session,
            surviving_id=req.surviving_job_id,
            superseded_id=req.superseded_job_id,
        )
    except CanonicalJobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CircularMergeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/jobs/merge", response_model=MergeExecuteResponse)
async def execute_job_merge(
    auth: AuthDep,
    req: MergeExecuteRequest,
    session: AsyncSession = Depends(get_session),
) -> MergeExecuteResponse:
    verify_aggregation_permission(auth, "merge_jobs")
    try:
        return await job_aggregation_service.execute_merge(
            session=session,
            surviving_id=req.surviving_job_id,
            superseded_id=req.superseded_job_id,
            actor=req.actor,
            reason=req.reason,
            field_overrides=req.field_overrides,
        )
    except CanonicalJobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CircularMergeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/jobs/{job_id}/split-preview", response_model=SplitPreviewResponse)
async def preview_job_split(
    auth: AuthDep,
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> SplitPreviewResponse:
    verify_aggregation_permission(auth, "split_jobs")
    try:
        return await job_aggregation_service.preview_split(session, job_id)
    except CanonicalJobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/jobs/{job_id}/split", response_model=SplitExecuteResponse)
async def execute_job_split(
    auth: AuthDep,
    job_id: str,
    req: SplitExecuteRequest,
    session: AsyncSession = Depends(get_session),
) -> SplitExecuteResponse:
    verify_aggregation_permission(auth, "split_jobs")
    try:
        return await job_aggregation_service.execute_split(
            session=session,
            job_id=job_id,
            link_ids=req.source_link_ids_to_detach,
            actor=req.actor,
            reason=req.reason,
        )
    except CanonicalJobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SplitValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------------------------------------------------------
# Employers
# -----------------------------------------------------------------------------
@router.get("/employers", response_model=list[CanonicalEmployerRecord])
async def list_canonical_employers(
    auth: AuthDep,
    query: Optional[str] = Query(None, description="Search employer name"),
    status: Optional[str] = Query(None, description="Identity status filter"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CanonicalEmployerRecord]:
    verify_aggregation_permission(auth, "read_employers")
    return await job_aggregation_service.list_employers(session, query, status, limit, offset)


@router.get("/employers/{employer_id}", response_model=CanonicalEmployerRecord)
async def get_canonical_employer(
    auth: AuthDep,
    employer_id: str,
    session: AsyncSession = Depends(get_session),
) -> CanonicalEmployerRecord:
    verify_aggregation_permission(auth, "read_employers")
    emp = await job_aggregation_service.get_employer(session, employer_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employer {employer_id} not found")
    return emp


@router.get("/employers/{employer_id}/evidence", response_model=list[dict[str, Any]])
async def get_employer_identity_evidence(
    auth: AuthDep,
    employer_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    verify_aggregation_permission(auth, "read_employers")
    stmt = select(EmployerIdentityDecisionModel).where(
        EmployerIdentityDecisionModel.employer_id == employer_id
    )
    res = await session.execute(stmt)
    decisions = res.scalars().all()
    return [
        {
            "id": d.id,
            "raw_name": d.raw_name,
            "decision": d.decision,
            "evidence": d.evidence_json,
            "decided_by": d.decided_by,
            "created_at": d.created_at.isoformat(),
        }
        for d in decisions
    ]


@router.post("/employers/resolve", response_model=CanonicalEmployerRecord)
async def resolve_employer_identity(
    auth: AuthDep,
    raw_name: str = Query(..., description="Raw employer name string"),
    source_url: Optional[str] = Query(None, description="Posting or careers URL"),
    provider: Optional[str] = Query(None, description="ATS or source provider"),
    session: AsyncSession = Depends(get_session),
) -> CanonicalEmployerRecord:
    verify_aggregation_permission(auth, "resolve_employers")
    return await job_aggregation_service.resolve_employer(
        session=session,
        raw_name=raw_name,
        source_url=source_url,
        provider=provider,
    )


@router.post("/employers/{employer_id}/correct", response_model=CanonicalEmployerRecord)
async def correct_canonical_employer(
    auth: AuthDep,
    employer_id: str,
    req: EmployerCorrectionRequest,
    session: AsyncSession = Depends(get_session),
) -> CanonicalEmployerRecord:
    verify_aggregation_permission(auth, "correct_employers")
    emp = await job_aggregation_service.correct_employer(session, employer_id, req)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employer {employer_id} not found")
    return emp


# -----------------------------------------------------------------------------
# Field Conflicts
# -----------------------------------------------------------------------------
@router.get("/conflicts", response_model=list[dict[str, Any]])
async def list_global_field_conflicts(
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    verify_aggregation_permission(auth, "read_canonical")
    stmt = (
        select(CanonicalJobConflictModel)
        .where(CanonicalJobConflictModel.status == "unresolved")
        .order_by(CanonicalJobConflictModel.created_at.desc())
    )
    res = await session.execute(stmt)
    conflicts = res.scalars().all()
    return [
        {
            "id": c.id,
            "canonical_job_id": c.canonical_job_id,
            "field_name": c.field_name,
            "conflict_type": c.conflict_type,
            "source_values": c.source_values_json,
            "created_at": c.created_at.isoformat(),
        }
        for c in conflicts
    ]


@router.post("/conflicts/{conflict_id}/resolve", response_model=dict[str, Any])
async def resolve_field_conflict(
    auth: AuthDep,
    conflict_id: str,
    req: ConflictResolveRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    verify_aggregation_permission(auth, "update_canonical")
    success = await job_aggregation_service.resolve_conflict(
        session=session,
        conflict_id=conflict_id,
        chosen_value=req.chosen_value,
        resolution_note=req.resolution_note,
        resolved_by=req.resolved_by,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conflict {conflict_id} not found")
    return {"status": "resolved", "conflict_id": conflict_id}


# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------
@router.get("/settings", response_model=AggregationSettingsConfig)
async def get_aggregation_settings(
    auth: AuthDep,
    session: AsyncSession = Depends(get_session),
) -> AggregationSettingsConfig:
    verify_aggregation_permission(auth, "read_canonical")
    return await job_aggregation_service.get_settings(session)


@router.put("/settings", response_model=AggregationSettingsConfig)
async def update_aggregation_settings(
    auth: AuthDep,
    settings: AggregationSettingsConfig,
    session: AsyncSession = Depends(get_session),
) -> AggregationSettingsConfig:
    verify_aggregation_permission(auth, "update_canonical")
    return await job_aggregation_service.update_settings(session, settings)
