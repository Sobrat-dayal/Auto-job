"""Command Center Dashboard aggregate REST API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.dependencies import AuthDep, ContainerDep
from app.db.engine import get_db_session
from app.db.models import Application, JobListing, TaskEventModel, TaskModel
from app.schemas.dashboard import (
    AgentOperationStatus,
    DashboardOverviewResponse,
    DashboardTasksSummary,
    DashboardTaskTrendsResponse,
    RecruitmentSummary,
    TaskTrendDataPoint,
)
from app.schemas.tasks import TaskState

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    container: ContainerDep,
    _auth: AuthDep,
) -> DashboardOverviewResponse:
    """Returns aggregated real-time metrics for the AUTONOM Command Center Dashboard."""
    worker_status = container.worker_manager.get_status()

    # Query persistent state from SQLite
    async with get_db_session() as session:
        # 1. Aggregate Task Counts
        task_query = select(TaskModel.status, func.count(TaskModel.id)).group_by(TaskModel.status)
        task_results = dict((await session.execute(task_query)).all())

        running_count = task_results.get(TaskState.RUNNING.value, 0)
        queued_count = task_results.get(TaskState.QUEUED.value, 0)
        completed_count = task_results.get(TaskState.COMPLETED.value, 0)
        failed_count = task_results.get(TaskState.FAILED.value, 0)
        cancelled_count = task_results.get(TaskState.CANCELLED.value, 0)
        total_tasks = sum(task_results.values())

        # Reconcile with live in-memory execution counts
        live_active = container.task_manager.active_tasks_count
        if live_active > running_count:
            running_count = live_active

        live_queued = container.worker_manager.queue_size
        if live_queued > queued_count:
            queued_count = live_queued

        tasks_summary = DashboardTasksSummary(
            running=running_count,
            queued=queued_count,
            completed=completed_count,
            failed=failed_count,
            cancelled=cancelled_count,
            total=total_tasks,
        )

        # 2. Aggregate Job Listings
        now = datetime.now(UTC)
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_jobs_res = await session.execute(select(func.count(JobListing.id)))
        total_jobs = total_jobs_res.scalar_one_or_none() or 0

        jobs_today_res = await session.execute(
            select(func.count(JobListing.id)).where(JobListing.discovered_at >= today_midnight)
        )
        jobs_today = jobs_today_res.scalar_one_or_none() or 0

        active_jobs_res = await session.execute(select(func.count(JobListing.id)).where(JobListing.status == "active"))
        active_jobs = active_jobs_res.scalar_one_or_none() or 0

        # 3. Aggregate Application Pipeline Stages
        app_counts_query = select(Application.status, func.count(Application.id)).group_by(Application.status)
        app_counts = dict((await session.execute(app_counts_query)).all())

        apps_total = sum(app_counts.values())
        apps_submitted = app_counts.get("submitted", 0)

        # Map to the 10 conceptual pipeline stages
        pipeline_stages = {
            "discovered": max(0, total_jobs - apps_total),
            "evaluated": app_counts.get("evaluated", 0),
            "matched": app_counts.get("matched", 0),
            "queued": app_counts.get("queued", 0),
            "preparing": app_counts.get("draft", 0) + app_counts.get("preparing", 0),
            "submitted": apps_submitted,
            "recruiter_response": app_counts.get("recruiter_response", 0),
            "interview": app_counts.get("interview", 0) + app_counts.get("interviewing", 0),
            "offer": app_counts.get("offer", 0) + app_counts.get("offered", 0),
            "rejected": app_counts.get("rejected", 0) + app_counts.get("closed", 0),
        }

        recruitment_summary = RecruitmentSummary(
            jobs_discovered=total_jobs,
            jobs_discovered_today=jobs_today,
            active_listings=active_jobs,
            applications_total=apps_total,
            applications_submitted=apps_submitted,
            pipeline_stages=pipeline_stages,
            automated_scouting_enabled=False,
            automated_scouting_message="Autonomous job scouting engine scheduled for Stage 26",
        )

        # 4. Pending actions count (failed tasks or issues requiring user review)
        pending_actions = failed_count

    # 5. Prominent Agent Panels (Typed status models, explicitly marked unavailable in Stage 08)
    agents = [
        AgentOperationStatus(
            id="job-discovery-agent",
            name="Job Discovery Agent",
            role="Opportunity Scout & ATS Parser",
            status="unavailable",
            target_stage="Stage 26",
            is_available=False,
            message="Autonomous job discovery scheduled for Stage 26. Connects to LinkedIn, Indeed, and ATS feeds.",
        ),
        AgentOperationStatus(
            id="application-agent",
            name="Application Tailor Agent",
            role="Resume Customizer & Submission Scribe",
            status="unavailable",
            target_stage="Stage 31",
            is_available=False,
            message="Automated application submissions scheduled for Stage 31. Form filing & resume tailoring.",
        ),
        AgentOperationStatus(
            id="supervisor-agent",
            name="Supervisor Swarm Agent",
            role="Multi-Agent Orchestrator & Safety Gate",
            status="unavailable",
            target_stage="Stage 12",
            is_available=False,
            message="Autonomous multi-agent orchestration scheduled for Stage 12. 24-agent swarm coordination.",
        ),
    ]

    return DashboardOverviewResponse(
        system_status="operational" if container.is_ready else "degraded",
        uptime_seconds=container.uptime_seconds,
        backend_connected=True,
        task_dispatch_status="active",
        ai_swarm_status="scheduled_stage_12",
        tasks_summary=tasks_summary,
        agents=agents,
        recruitment=recruitment_summary,
        workers={
            "total": worker_status.total_workers,
            "active": worker_status.active_workers,
            "idle": worker_status.idle_workers,
            "max_capacity": worker_status.max_capacity,
        },
        pending_actions_count=pending_actions,
        timestamp=now,
    )


@router.get("/task-trends", response_model=DashboardTaskTrendsResponse)
async def get_dashboard_task_trends(
    _auth: AuthDep,
    window: Annotated[Literal["today", "7d", "30d"], Query(description="Time window for trend analytics")] = "7d",
) -> DashboardTaskTrendsResponse:
    """Returns genuine time-bucketed task execution metrics derived from SQLite."""
    now = datetime.now(UTC)
    num_days = 1 if window == "today" else 7 if window == "7d" else 30
    start_date = now - timedelta(days=num_days)

    # Initialize bucket date map
    buckets: dict[str, dict[str, Any]] = {}
    for i in range(num_days):
        day = (start_date + timedelta(days=i + 1)).strftime("%Y-%m-%d")
        buckets[day] = {
            "date": day,
            "created": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "durations": [],
        }

    async with get_db_session() as session:
        query = select(TaskModel).where(TaskModel.created_at >= start_date)
        result = await session.execute(query)
        tasks = list(result.scalars().all())

    for t in tasks:
        day_str = t.created_at.strftime("%Y-%m-%d") if t.created_at else now.strftime("%Y-%m-%d")
        if day_str in buckets:
            buckets[day_str]["created"] += 1
            if t.status == TaskState.COMPLETED.value:
                buckets[day_str]["completed"] += 1
                if t.started_at and t.completed_at:
                    dur = (t.completed_at - t.started_at).total_seconds()
                    if dur >= 0:
                        buckets[day_str]["durations"].append(dur)
            elif t.status == TaskState.FAILED.value:
                buckets[day_str]["failed"] += 1
            elif t.status == TaskState.CANCELLED.value:
                buckets[day_str]["cancelled"] += 1

    data_points: list[TaskTrendDataPoint] = []
    total_volume = 0
    total_completed = 0

    for day in sorted(buckets.keys()):
        b = buckets[day]
        durs = b["durations"]
        avg_dur = round(sum(durs) / len(durs), 2) if durs else 0.0

        total_volume += b["created"]
        total_completed += b["completed"]

        data_points.append(
            TaskTrendDataPoint(
                date=b["date"],
                created=b["created"],
                completed=b["completed"],
                failed=b["failed"],
                cancelled=b["cancelled"],
                avg_duration_seconds=avg_dur,
            )
        )

    success_rate = round((total_completed / max(1, total_volume)) * 100.0, 1) if total_volume > 0 else 100.0

    return DashboardTaskTrendsResponse(
        window=window,
        data_points=data_points,
        total_volume=total_volume,
        overall_success_rate=success_rate,
    )


@router.get("/activity", response_model=list[dict[str, Any]])
async def get_dashboard_activity(
    _auth: AuthDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum activity events to return")] = 50,
) -> list[dict[str, Any]]:
    """Returns recent durable task and system activity events from SQLite."""
    async with get_db_session() as session:
        query = select(TaskEventModel).order_by(TaskEventModel.timestamp.desc()).limit(limit)
        events = list((await session.execute(query)).scalars().all())

    return [
        {
            "id": e.id,
            "task_id": e.task_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat(),
            "state_transition": e.state_transition,
            "metadata": e.metadata_json or {},
            "correlation_id": e.correlation_id,
        }
        for e in events
    ]
