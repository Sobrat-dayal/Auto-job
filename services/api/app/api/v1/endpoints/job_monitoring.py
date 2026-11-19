"""FastAPI REST endpoints for Stage 30 Continuous Recruitment Monitoring."""

from __future__ import annotations

from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.api.dependencies import AuthDep
from app.recruitment.monitoring.contracts import (
    AlertEventData,
    AlertRuleCreateRequest,
    AlertRuleData,
    AlertRuleUpdateRequest,
    ComponentHealthData,
    DiagnosticsReport,
    JobChangeEventData,
    JobWatchCreateRequest,
    JobWatchData,
    JobWatchUpdateRequest,
    MonitoringMetricsData,
    MonitoringOverviewKPIs,
    MonitoringProfileCreateRequest,
    MonitoringProfileData,
    MonitoringProfileUpdateRequest,
    MonitoringRunData,
    MonitoringSettingsData,
    MonitoringSettingsUpdateRequest,
    NotificationOutboxData,
    OpportunityQueueEntryData,
    OpportunityQueueUpdateRequest,
    SchedulePreviewResponse,
)
from app.recruitment.monitoring.errors import (
    AlertEventNotFoundError,
    AlertRuleNotFoundError,
    ProfileNotFoundError,
    QueueEntryNotFoundError,
    RunNotFoundError,
    WatchNotFoundError,
)
from app.recruitment.monitoring.service import recruitment_monitoring_service

router = APIRouter(prefix="/recruitment-monitoring", tags=["recruitment-monitoring"])


# ---------------------------------------------------------------------------
# Overview & Status
# ---------------------------------------------------------------------------

@router.get("/status", response_model=MonitoringOverviewKPIs)
async def get_monitoring_status(auth: AuthDep) -> MonitoringOverviewKPIs:
    """Returns overview KPIs, active watches count, and operational status."""
    return await recruitment_monitoring_service.get_overview_kpis(owner_id=auth.user_id)


# ---------------------------------------------------------------------------
# Monitoring Profiles
# ---------------------------------------------------------------------------

@router.get("/profiles", response_model=list[MonitoringProfileData])
async def list_monitoring_profiles(auth: AuthDep) -> list[MonitoringProfileData]:
    """Lists all monitoring profiles owned by the authenticated user."""
    return await recruitment_monitoring_service.list_profiles(owner_id=auth.user_id)


@router.post("/profiles", response_model=MonitoringProfileData, status_code=status.HTTP_201_CREATED)
async def create_monitoring_profile(
    auth: AuthDep,
    req: MonitoringProfileCreateRequest,
) -> MonitoringProfileData:
    """Creates a new recruitment monitoring profile."""
    return await recruitment_monitoring_service.create_profile(owner_id=auth.user_id, req=req)


@router.get("/profiles/{profile_id}", response_model=MonitoringProfileData)
async def get_monitoring_profile(profile_id: str, _auth: AuthDep) -> MonitoringProfileData:
    """Retrieves a single monitoring profile by ID."""
    try:
        return await recruitment_monitoring_service.get_profile(profile_id)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/profiles/{profile_id}", response_model=MonitoringProfileData)
async def update_monitoring_profile(
    profile_id: str,
    req: MonitoringProfileUpdateRequest,
    _auth: AuthDep,
) -> MonitoringProfileData:
    """Updates configuration for a monitoring profile."""
    try:
        return await recruitment_monitoring_service.update_profile(profile_id, req)
    except ProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------------------------------------------------------------------
# Job Watches
# ---------------------------------------------------------------------------

@router.get("/watches", response_model=list[JobWatchData])
async def list_job_watches(
    auth: AuthDep,
    profile_id: Annotated[Optional[str], Query(description="Filter by profile ID")] = None,
    status_filter: Annotated[Optional[str], Query(alias="status", description="Filter by status")] = None,
) -> list[JobWatchData]:
    """Lists all active and configured job watches."""
    return await recruitment_monitoring_service.list_watches(
        owner_id=auth.user_id,
        profile_id=profile_id,
        status=status_filter,
    )


@router.post("/watches", response_model=JobWatchData, status_code=status.HTTP_201_CREATED)
async def create_job_watch(
    auth: AuthDep,
    req: JobWatchCreateRequest,
) -> JobWatchData:
    """Creates and activates a new job watch with recurring schedule."""
    return await recruitment_monitoring_service.create_watch(owner_id=auth.user_id, req=req)


@router.get("/watches/{watch_id}", response_model=JobWatchData)
async def get_job_watch(watch_id: str, _auth: AuthDep) -> JobWatchData:
    """Retrieves full configuration and status for a job watch."""
    try:
        return await recruitment_monitoring_service.get_watch(watch_id)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/watches/{watch_id}", response_model=JobWatchData)
async def update_job_watch(
    watch_id: str,
    req: JobWatchUpdateRequest,
    _auth: AuthDep,
) -> JobWatchData:
    """Updates watch parameters, schedule, or filters."""
    try:
        return await recruitment_monitoring_service.update_watch(watch_id, req)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/watches/{watch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_watch(watch_id: str, _auth: AuthDep) -> None:
    """Deletes a job watch and its associated schedules."""
    deleted = await recruitment_monitoring_service.delete_watch(watch_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Watch '{watch_id}' not found.")


@router.post("/watches/{watch_id}/validate")
async def validate_job_watch(watch_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Performs sanity validation on a watch and schedule without executing it."""
    try:
        return await recruitment_monitoring_service.validate_watch(watch_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/watches/{watch_id}/activate", response_model=JobWatchData)
async def activate_job_watch(watch_id: str, _auth: AuthDep) -> JobWatchData:
    """Activates a draft, paused, or suspended watch."""
    try:
        return await recruitment_monitoring_service.activate_watch(watch_id)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/watches/{watch_id}/pause", response_model=JobWatchData)
async def pause_job_watch(watch_id: str, _auth: AuthDep) -> JobWatchData:
    """Pauses recurring executions for a watch."""
    try:
        return await recruitment_monitoring_service.pause_watch(watch_id)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/watches/{watch_id}/resume", response_model=JobWatchData)
async def resume_job_watch(watch_id: str, _auth: AuthDep) -> JobWatchData:
    """Resumes recurring executions for a paused watch."""
    try:
        return await recruitment_monitoring_service.resume_watch(watch_id)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/watches/{watch_id}/run-now", response_model=MonitoringRunData)
async def run_watch_now(
    watch_id: str,
    auth: AuthDep,
) -> MonitoringRunData:
    """Triggers an immediate manual discovery run for the specified watch."""
    try:
        return await recruitment_monitoring_service.run_now(
            watch_id=watch_id,
            worker_id=f"user-{auth.user_id[:8]}",
            applicant_profile_id=auth.user_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/watches/{watch_id}/schedule-preview", response_model=SchedulePreviewResponse)
async def get_schedule_preview(watch_id: str, _auth: AuthDep) -> SchedulePreviewResponse:
    """Calculates upcoming occurrences and estimated request budgets without executing network requests."""
    try:
        return await recruitment_monitoring_service.preview_schedule(watch_id)
    except WatchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------------------------------------------------------------------
# Monitoring Runs
# ---------------------------------------------------------------------------

@router.get("/runs", response_model=list[MonitoringRunData])
async def list_monitoring_runs(
    _auth: AuthDep,
    watch_id: Annotated[Optional[str], Query(description="Filter by watch ID")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[MonitoringRunData]:
    """Lists monitoring execution run history."""
    return await recruitment_monitoring_service.list_runs(watch_id=watch_id, limit=limit, offset=offset)


@router.get("/runs/{run_id}", response_model=MonitoringRunData)
async def get_monitoring_run(run_id: str, _auth: AuthDep) -> MonitoringRunData:
    """Retrieves full details and progress metrics for a monitoring run."""
    try:
        return await recruitment_monitoring_service.get_run(run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/runs/{run_id}/cancel")
async def cancel_monitoring_run(run_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Cancels an active or queued monitoring run."""
    cancelled = await recruitment_monitoring_service.cancel_run(run_id)
    if not cancelled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel run '{run_id}'.")
    return {"cancelled": True, "run_id": run_id}


# ---------------------------------------------------------------------------
# Opportunity Queue
# ---------------------------------------------------------------------------

@router.get("/opportunities", response_model=list[OpportunityQueueEntryData])
async def list_opportunities(
    auth: AuthDep,
    priority: Annotated[Optional[str], Query(description="Filter by priority level")] = None,
    queue_status: Annotated[Optional[str], Query(description="Filter by queue status")] = None,
    ready_for_preparation: Annotated[Optional[bool], Query(description="Filter by readiness")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[OpportunityQueueEntryData]:
    """Lists prioritized vacancies in the opportunity queue."""
    return await recruitment_monitoring_service.list_opportunities(
        applicant_profile_id=auth.user_id,
        priority=priority,
        queue_status=queue_status,
        ready_for_preparation=ready_for_preparation,
        limit=limit,
        offset=offset,
    )


@router.get("/opportunities/{entry_id}", response_model=OpportunityQueueEntryData)
async def get_opportunity(entry_id: str, _auth: AuthDep) -> OpportunityQueueEntryData:
    """Retrieves details of a single opportunity queue entry."""
    try:
        return await recruitment_monitoring_service.get_opportunity(entry_id)
    except QueueEntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/opportunities/{entry_id}", response_model=OpportunityQueueEntryData)
async def update_opportunity(
    entry_id: str,
    req: OpportunityQueueUpdateRequest,
    _auth: AuthDep,
) -> OpportunityQueueEntryData:
    """Applies user actions (save, prioritize, defer, exclude, archive) or manual priority changes."""
    try:
        return await recruitment_monitoring_service.update_opportunity(entry_id, req)
    except QueueEntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------------------------------------------------------------------
# Job Changes
# ---------------------------------------------------------------------------

@router.get("/job-changes", response_model=list[JobChangeEventData])
async def list_job_changes(
    _auth: AuthDep,
    canonical_job_id: Annotated[Optional[str], Query(description="Filter by job ID")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[JobChangeEventData]:
    """Lists recorded material and technical job changes."""
    return await recruitment_monitoring_service.list_job_changes(canonical_job_id=canonical_job_id, limit=limit)


# ---------------------------------------------------------------------------
# Alerts & Notifications
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=list[AlertEventData])
async def list_alerts(
    auth: AuthDep,
    unread_only: Annotated[bool, Query(description="Filter unread alerts")] = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AlertEventData]:
    """Lists alerts generated by monitoring operations."""
    return await recruitment_monitoring_service.list_alerts(
        owner_id=auth.user_id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.get("/alert-rules", response_model=list[AlertRuleData])
async def list_alert_rules(auth: AuthDep) -> list[AlertRuleData]:
    """Lists configured alert rules."""
    return await recruitment_monitoring_service.list_alert_rules(owner_id=auth.user_id)


@router.post("/alert-rules", response_model=AlertRuleData, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    auth: AuthDep,
    req: AlertRuleCreateRequest,
) -> AlertRuleData:
    """Creates a new alert rule."""
    return await recruitment_monitoring_service.create_alert_rule(owner_id=auth.user_id, req=req)


@router.patch("/alert-rules/{rule_id}", response_model=AlertRuleData)
async def update_alert_rule(
    rule_id: str,
    req: AlertRuleUpdateRequest,
    _auth: AuthDep,
) -> AlertRuleData:
    """Updates an alert rule."""
    try:
        return await recruitment_monitoring_service.update_alert_rule(rule_id, req)
    except AlertRuleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Marks an alert as acknowledged / read."""
    ack = await recruitment_monitoring_service.acknowledge_alert(alert_id)
    if not ack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert '{alert_id}' not found.")
    return {"acknowledged": True, "alert_id": alert_id}


@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Dismisses an alert."""
    dismissed = await recruitment_monitoring_service.dismiss_alert(alert_id)
    if not dismissed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert '{alert_id}' not found.")
    return {"dismissed": True, "alert_id": alert_id}


@router.get("/notifications", response_model=list[NotificationOutboxData])
async def list_notifications(
    _auth: AuthDep,
    status_filter: Annotated[Optional[str], Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[NotificationOutboxData]:
    """Lists in-app and desktop notification outbox items."""
    return await recruitment_monitoring_service.list_notifications(status=status_filter, limit=limit)


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Marks a notification as read."""
    marked = await recruitment_monitoring_service.mark_notification_read(notification_id)
    if not marked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification '{notification_id}' not found.")
    return {"read": True, "notification_id": notification_id}


# ---------------------------------------------------------------------------
# Health, Metrics & Settings
# ---------------------------------------------------------------------------

@router.get("/sources/health")
async def get_source_health(_auth: AuthDep) -> list[dict[str, Any]]:
    """Returns connectivity, error status, and freshness for all job sources."""
    return [h.model_dump(mode="json") for h in recruitment_monitoring_service.list_source_health()]


@router.get("/workers/health", response_model=list[ComponentHealthData])
async def get_worker_health(_auth: AuthDep) -> list[ComponentHealthData]:
    """Returns heartbeats and status for workers and recruitment agents."""
    return await recruitment_monitoring_service.list_worker_health()


@router.get("/metrics", response_model=MonitoringMetricsData)
async def get_monitoring_metrics(_auth: AuthDep) -> MonitoringMetricsData:
    """Returns aggregated execution counts, latencies, and request totals."""
    return await recruitment_monitoring_service.get_metrics()


@router.get("/diagnostics", response_model=DiagnosticsReport)
async def get_diagnostics(_auth: AuthDep) -> DiagnosticsReport:
    """Returns unified diagnostics report for monitoring and background operations."""
    return await recruitment_monitoring_service.get_diagnostics()


@router.get("/settings", response_model=MonitoringSettingsData)
async def get_monitoring_settings(auth: AuthDep) -> MonitoringSettingsData:
    """Returns persistent background monitoring settings."""
    return await recruitment_monitoring_service.get_settings(owner_id=auth.user_id)


@router.patch("/settings", response_model=MonitoringSettingsData)
async def update_monitoring_settings(
    auth: AuthDep,
    req: MonitoringSettingsUpdateRequest,
) -> MonitoringSettingsData:
    """Updates persistent background monitoring and Windows lifecycle settings."""
    return await recruitment_monitoring_service.update_settings(owner_id=auth.user_id, req=req)
