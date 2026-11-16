"""Job applications and execution attempts REST API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import ApplicationRepository
from app.schemas.applications import (
    ApplicationAttemptResponse,
    ApplicationListResponse,
    ApplicationResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _map_application(app) -> ApplicationResponse:
    attempts = [
        ApplicationAttemptResponse(
            id=att.id,
            application_id=att.application_id,
            attempted_at=att.attempted_at,
            execution_status=att.execution_status,
            failure_category=att.failure_category,
            error_summary=att.error_summary,
            retry_eligible=att.retry_eligible,
            idempotency_key=att.idempotency_key,
        )
        for att in (app.attempts or [])
    ]
    return ApplicationResponse(
        id=app.id,
        job_id=app.job_id,
        profile_id=app.profile_id,
        resume_version_id=app.resume_version_id,
        status=app.status,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
        confirmation_ref=app.confirmation_ref,
        notes=app.notes,
        authorization_ref=app.authorization_ref,
        company=app.job.company if app.job else None,
        job_title=app.job.title if app.job else None,
        attempts=attempts,
    )


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    _auth: AuthDep,
    status_filter: Annotated[str | None, Query(alias="status", description="Filter by application status")] = None,
    profile_id: Annotated[str | None, Query(description="Filter by applicant profile ID")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max applications to return")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> ApplicationListResponse:
    """Lists persistent job applications from SQLite with attempts and job metadata."""
    async with get_db_session() as session:
        repo = ApplicationRepository(session)
        items = await repo.list_applications(status=status_filter, profile_id=profile_id, limit=limit, offset=offset)
        total = await repo.count_applications(status=status_filter, profile_id=profile_id)

    return ApplicationListResponse(
        items=[_map_application(app) for app in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    _auth: AuthDep,
) -> ApplicationResponse:
    """Retrieves full details of a specific job application including all attempt histories."""
    async with get_db_session() as session:
        repo = ApplicationRepository(session)
        app = await repo.get_application_by_id(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application '{application_id}' not found",
            )

    return _map_application(app)
