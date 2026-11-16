"""Job listings and opportunity discovery REST API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import JobRepository
from app.schemas.jobs import JobListingResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    _auth: AuthDep,
    status_filter: Annotated[str | None, Query(alias="status", description="Filter by job status")] = None,
    company: Annotated[str | None, Query(description="Filter by company name substring")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max jobs to return")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> JobListResponse:
    """Lists persistent job listings from SQLite with optional filtering and pagination."""
    async with get_db_session() as session:
        repo = JobRepository(session)
        items = await repo.list_listings(status=status_filter, company=company, limit=limit, offset=offset)
        total = await repo.count_listings(status=status_filter, company=company)

    return JobListResponse(
        items=[
            JobListingResponse(
                id=j.id,
                source_id=j.source_id,
                external_id=j.external_id,
                company=j.company,
                title=j.title,
                location=j.location,
                employment_type=j.employment_type,
                work_arrangement=j.work_arrangement,
                salary_range=j.salary_range,
                description=j.description,
                requirements=j.requirements,
                application_url=j.application_url,
                discovered_at=j.discovered_at,
                last_verified_at=j.last_verified_at,
                status=j.status,
            )
            for j in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{job_id}", response_model=JobListingResponse)
async def get_job(
    job_id: str,
    _auth: AuthDep,
) -> JobListingResponse:
    """Retrieves full details of a specific job listing."""
    async with get_db_session() as session:
        repo = JobRepository(session)
        job = await repo.get_listing_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job listing '{job_id}' not found",
            )

    return JobListingResponse(
        id=job.id,
        source_id=job.source_id,
        external_id=job.external_id,
        company=job.company,
        title=job.title,
        location=job.location,
        employment_type=job.employment_type,
        work_arrangement=job.work_arrangement,
        salary_range=job.salary_range,
        description=job.description,
        requirements=job.requirements,
        application_url=job.application_url,
        discovered_at=job.discovered_at,
        last_verified_at=job.last_verified_at,
        status=job.status,
    )
