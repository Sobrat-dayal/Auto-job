"""Job Discovery API Endpoints (Stage 26).

FastAPI routes for Multi-Source Job Discovery Engine, connectors, source management,
employer career portals, URL and manual import, tasks, and telemetry.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import AuthContext, require_auth
from app.recruitment.discovery.contracts import (
    ConnectorId,
    ConnectorManifest,
    DiscoveryOverviewStats,
    DiscoverySettingsConfig,
    DiscoveryTaskCreateRequest,
    DiscoveryTaskRecord,
    EmployerCareerPageCreateRequest,
    EmployerCareerSource,
    JobSourceConfig,
    JobSourceCreateRequest,
    JobSourceHealth,
    JobSourceObservation,
    JobSourceSnapshot,
    JobSourceUpdateRequest,
    ManualImportRequest,
    PostingAvailability,
    PrefilterOutcome,
    SourceValidationResult,
    UrlImportRequest,
)
from app.recruitment.discovery.errors import (
    ConnectorNotFoundError,
    JobDiscoveryError,
    SourceAccessRestrictedError,
    SourceNotFoundError,
)
from app.recruitment.discovery.service import job_discovery_service

router = APIRouter(prefix="/recruitment/discovery", tags=["job-discovery"])


# -----------------------------------------------------------------------------
# Overview & Diagnostics
# -----------------------------------------------------------------------------
@router.get("/status", response_model=DiscoveryOverviewStats)
@router.get("/overview", response_model=DiscoveryOverviewStats)
async def get_discovery_overview(
    auth: AuthContext = Depends(require_auth),
) -> DiscoveryOverviewStats:
    """Get high-level summary metrics across sources, postings, and tasks."""
    return job_discovery_service.get_overview_stats()


@router.get("/diagnostics")
async def get_discovery_diagnostics(
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Retrieve detailed diagnostic information including health, cache, and limits."""
    stats = job_discovery_service.get_overview_stats()
    health_list = job_discovery_service.list_all_health()
    settings = job_discovery_service.get_settings()
    manifests = job_discovery_service.list_connectors()

    return {
        "status": "operational",
        "overview": stats.model_dump(),
        "settings": settings.model_dump(),
        "connectors_available": len(manifests),
        "sources_tracked": len(health_list),
        "source_health": [h.model_dump() for h in health_list],
    }


# -----------------------------------------------------------------------------
# Connectors
# -----------------------------------------------------------------------------
@router.get("/connectors", response_model=list[ConnectorManifest])
async def list_connectors(
    auth: AuthContext = Depends(require_auth),
) -> list[ConnectorManifest]:
    """List all registered job source connectors and capability manifests."""
    return job_discovery_service.list_connectors()


@router.get("/connectors/{connector_id}", response_model=ConnectorManifest)
async def get_connector(
    connector_id: str,
    auth: AuthContext = Depends(require_auth),
) -> ConnectorManifest:
    """Get manifest for a specific connector."""
    manifest = job_discovery_service.get_connector_manifest(connector_id)
    if not manifest:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
    return manifest


# -----------------------------------------------------------------------------
# Sources Management
# -----------------------------------------------------------------------------
@router.get("/sources", response_model=list[JobSourceConfig])
async def list_sources(
    enabled_only: bool = Query(False, description="Filter for enabled sources only"),
    auth: AuthContext = Depends(require_auth),
) -> list[JobSourceConfig]:
    """List configured job sources."""
    return job_discovery_service.list_sources(enabled_only=enabled_only)


@router.post("/sources", response_model=JobSourceConfig, status_code=status.HTTP_201_CREATED)
async def create_source(
    req: JobSourceCreateRequest,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceConfig:
    """Create a new job source configuration."""
    return job_discovery_service.create_source(req)


@router.get("/sources/{source_id}", response_model=JobSourceConfig)
async def get_source(
    source_id: str,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceConfig:
    """Get configuration details for a specific job source."""
    try:
        return job_discovery_service.get_source(source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/sources/{source_id}", response_model=JobSourceConfig)
async def update_source(
    source_id: str,
    req: JobSourceUpdateRequest,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceConfig:
    """Update job source configuration."""
    try:
        return job_discovery_service.update_source(source_id, req)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Delete a configured job source."""
    success = job_discovery_service.delete_source(source_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    return {"source_id": source_id, "deleted": True}


@router.post("/sources/{source_id}/validate", response_model=SourceValidationResult)
async def validate_source(
    source_id: str,
    auth: AuthContext = Depends(require_auth),
) -> SourceValidationResult:
    """Validate endpoint reachability, credentials, and structure for a source."""
    try:
        return await job_discovery_service.validate_source(source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/sources/{source_id}/refresh", response_model=JobSourceSnapshot)
async def refresh_source(
    source_id: str,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceSnapshot:
    """Manually trigger incremental fetch and snapshot sync for a source."""
    try:
        return await job_discovery_service.refresh_source(source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except SourceAccessRestrictedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/sources/{source_id}/health", response_model=JobSourceHealth)
async def get_source_health(
    source_id: str,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceHealth:
    """Retrieve operational telemetry and health state for a source."""
    return job_discovery_service.get_source_health(source_id)


# -----------------------------------------------------------------------------
# Employer Career Sources
# -----------------------------------------------------------------------------
@router.get("/employers", response_model=list[EmployerCareerSource])
async def list_employer_sources(
    enabled_only: bool = Query(False),
    auth: AuthContext = Depends(require_auth),
) -> list[EmployerCareerSource]:
    """List approved employer career portals."""
    return job_discovery_service.list_employer_sources(enabled_only=enabled_only)


@router.post("/employers", response_model=EmployerCareerSource, status_code=status.HTTP_201_CREATED)
async def add_employer_source(
    req: EmployerCareerPageCreateRequest,
    auth: AuthContext = Depends(require_auth),
) -> EmployerCareerSource:
    """Register a new employer career page and detect ATS metadata."""
    return job_discovery_service.add_employer_source(req)


@router.delete("/employers/{employer_id}")
async def delete_employer_source(
    employer_id: str,
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Delete an employer career source."""
    success = job_discovery_service.delete_employer_source(employer_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Employer source '{employer_id}' not found")
    return {"employer_id": employer_id, "deleted": True}


# -----------------------------------------------------------------------------
# Import Handlers
# -----------------------------------------------------------------------------
@router.post("/import/url", response_model=JobSourceObservation)
async def import_job_url(
    req: UrlImportRequest,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceObservation:
    """Import and parse a single job URL provided by the user."""
    try:
        return await job_discovery_service.import_url(req)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to import URL: {str(exc)}")


@router.post("/import/manual", response_model=JobSourceObservation)
async def import_job_manual(
    req: ManualImportRequest,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceObservation:
    """Create a job posting observation directly from user-supplied details."""
    return job_discovery_service.import_manual(req)


# -----------------------------------------------------------------------------
# Postings / Observations
# -----------------------------------------------------------------------------
@router.get("/postings", response_model=list[JobSourceObservation])
async def list_postings(
    source_id: Optional[str] = Query(None),
    availability: Optional[PostingAvailability] = Query(None),
    prefilter: Optional[PrefilterOutcome] = Query(None),
    query: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    auth: AuthContext = Depends(require_auth),
) -> list[JobSourceObservation]:
    """List observed job postings with filtering."""
    return job_discovery_service.list_observations(
        source_id=source_id,
        availability=availability,
        prefilter=prefilter,
        query=query,
        limit=limit,
    )


@router.get("/postings/{observation_id}", response_model=JobSourceObservation)
async def get_posting(
    observation_id: str,
    auth: AuthContext = Depends(require_auth),
) -> JobSourceObservation:
    """Retrieve detailed observation record for a single job posting."""
    obs = job_discovery_service.get_observation(observation_id)
    if not obs:
        raise HTTPException(status_code=404, detail=f"Posting observation '{observation_id}' not found")
    return obs


# -----------------------------------------------------------------------------
# Tasks
# -----------------------------------------------------------------------------
@router.get("/tasks", response_model=list[DiscoveryTaskRecord])
async def list_tasks(
    limit: int = Query(50, ge=1, le=100),
    auth: AuthContext = Depends(require_auth),
) -> list[DiscoveryTaskRecord]:
    """List recent discovery tasks."""
    return job_discovery_service.list_tasks(limit=limit)


@router.post("/tasks", response_model=DiscoveryTaskRecord, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    req: DiscoveryTaskCreateRequest,
    auth: AuthContext = Depends(require_auth),
) -> DiscoveryTaskRecord:
    """Queue a new multi-source discovery background task."""
    return job_discovery_service.create_task(req)


@router.get("/tasks/{task_id}", response_model=DiscoveryTaskRecord)
async def get_task(
    task_id: str,
    auth: AuthContext = Depends(require_auth),
) -> DiscoveryTaskRecord:
    """Get status and metrics for a specific discovery task."""
    task = job_discovery_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    auth: AuthContext = Depends(require_auth),
) -> dict[str, Any]:
    """Cancel a running or queued discovery task."""
    success = job_discovery_service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found or cannot be cancelled")
    return {"task_id": task_id, "cancelled": True}


# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------
@router.get("/settings", response_model=DiscoverySettingsConfig)
async def get_settings(
    auth: AuthContext = Depends(require_auth),
) -> DiscoverySettingsConfig:
    """Get discovery concurrency, rate limits, and network settings."""
    return job_discovery_service.get_settings()


@router.put("/settings", response_model=DiscoverySettingsConfig)
async def update_settings(
    settings: DiscoverySettingsConfig,
    auth: AuthContext = Depends(require_auth),
) -> DiscoverySettingsConfig:
    """Update discovery concurrency, rate limits, and network settings."""
    return job_discovery_service.update_settings(settings)
