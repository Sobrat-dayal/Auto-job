"""Pydantic schemas for Command Center Dashboard metrics, operational trends, and recruitment pipeline."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DashboardTasksSummary(BaseModel):
    running: int = Field(ge=0, description="Tasks currently executing on workers")
    queued: int = Field(ge=0, description="Tasks waiting in worker queue")
    completed: int = Field(ge=0, description="Tasks successfully finished")
    failed: int = Field(ge=0, description="Tasks terminated with error or crash")
    cancelled: int = Field(ge=0, description="Tasks cooperatively cancelled")
    total: int = Field(ge=0, description="Total durable task count in database")


class AgentOperationStatus(BaseModel):
    id: str = Field(description="Unique agent identifier")
    name: str = Field(description="Display name of the agent")
    role: str = Field(description="Functional specialty and domain")
    status: Literal[
        "unavailable",
        "offline",
        "idle",
        "starting",
        "planning",
        "running",
        "paused",
        "waiting_approval",
        "recovering",
        "completed",
        "failed",
        "degraded",
    ] = Field(default="unavailable", description="Operational lifecycle status")
    target_stage: str = Field(description="Roadmap stage when this agent capability goes live")
    is_available: bool = Field(default=False, description="Whether the agent runtime is currently implemented")
    current_task: str | None = None
    progress: float | None = None
    last_activity: str | None = None
    successful_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)
    message: str = Field(default="Agent capability scheduled for upcoming roadmap stage")


class RecruitmentSummary(BaseModel):
    jobs_discovered: int = Field(default=0, ge=0, description="Total jobs discovered and recorded in database")
    jobs_discovered_today: int = Field(default=0, ge=0, description="Jobs recorded in database today")
    active_listings: int = Field(default=0, ge=0, description="Active job listings in database")
    applications_total: int = Field(default=0, ge=0, description="Total applications recorded in database")
    applications_submitted: int = Field(default=0, ge=0, description="Applications with confirmed submitted status")
    pipeline_stages: dict[str, int] = Field(default_factory=dict, description="Counts by pipeline stage")
    automated_scouting_enabled: bool = Field(
        default=False,
        description="Whether automated crawler/scouter is active (Stage 26)",
    )
    automated_scouting_message: str = Field(
        default="Automated job scouting engine scheduled for Stage 26",
    )


class DashboardOverviewResponse(BaseModel):
    system_status: Literal["operational", "degraded", "disconnected"] = "operational"
    uptime_seconds: float = Field(ge=0.0)
    backend_connected: bool = True
    task_dispatch_status: Literal["active", "paused"] = "active"
    ai_swarm_status: Literal["scheduled_stage_12", "active", "degraded"] = "scheduled_stage_12"
    tasks_summary: DashboardTasksSummary
    agents: list[AgentOperationStatus]
    recruitment: RecruitmentSummary
    workers: dict[str, Any] = Field(default_factory=dict)
    pending_actions_count: int = Field(ge=0, default=0)
    timestamp: datetime


class TaskTrendDataPoint(BaseModel):
    date: str = Field(description="ISO date string YYYY-MM-DD or hour string")
    created: int = Field(default=0, ge=0)
    completed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    cancelled: int = Field(default=0, ge=0)
    avg_duration_seconds: float = Field(default=0.0, ge=0.0)


class DashboardTaskTrendsResponse(BaseModel):
    window: Literal["today", "7d", "30d"] = "7d"
    data_points: list[TaskTrendDataPoint]
    total_volume: int = Field(ge=0, default=0)
    overall_success_rate: float = Field(ge=0.0, le=100.0, default=100.0)
