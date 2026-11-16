"""Pydantic schemas for system, health, version, and error responses."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status: healthy, degraded")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Current server timestamp in UTC",
    )
    environment: str = Field(..., description="Runtime environment")
    is_loopback: bool = Field(..., description="Whether service is bound to loopback")


class ReadinessResponse(BaseModel):
    ready: bool = Field(..., description="Whether service is ready to accept requests")
    status: str = Field(..., description="Readiness status description")
    checks: dict[str, bool] = Field(..., description="Component readiness checks")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Current server timestamp in UTC",
    )


class VersionResponse(BaseModel):
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application release version")
    api_version: str = Field(..., description="API version prefix (e.g. v1)")
    python_version: str = Field(..., description="Runtime Python version")
    platform: str = Field(..., description="Host operating system platform")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    retryable: bool = Field(default=False, description="Whether the operation may be safely retried")
    details: dict[str, Any] | None = Field(default=None, description="Optional diagnostic details")


class ErrorResponse(BaseModel):
    error: ErrorDetail
    status_code: int
    request_id: str | None = Field(default=None, description="Request identifier for tracing")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WorkerInfo(BaseModel):
    worker_id: str = Field(..., description="Unique worker process or task identifier")
    status: str = Field(..., description="Worker state: idle, busy, shutting_down")
    active_task_id: str | None = Field(default=None, description="ID of task currently executing, if any")
    tasks_completed: int = Field(default=0, description="Cumulative tasks completed by this worker")
    tasks_failed: int = Field(default=0, description="Cumulative tasks failed on this worker")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Worker start timestamp")


class WorkerListResponse(BaseModel):
    workers: list[WorkerInfo] = Field(..., description="List of active worker pool instances")
    total_workers: int = Field(..., description="Total active worker slots")
    active_workers: int = Field(..., description="Workers currently executing tasks")
    idle_workers: int = Field(..., description="Workers currently waiting for tasks")
    max_capacity: int = Field(..., description="Configured maximum worker concurrency")


class SystemStatusResponse(BaseModel):
    status: str = Field(..., description="System overall operational status")
    uptime_seconds: float = Field(..., description="Uptime of API service in seconds")
    active_tasks: int = Field(..., description="Number of tasks currently running")
    queued_tasks: int = Field(..., description="Number of tasks waiting in queue")
    workers: dict[str, int] = Field(..., description="Worker statistics breakdown")
    event_subscribers: int = Field(..., description="Current count of active event bus subscribers")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Current timestamp in UTC")


class SystemCapabilitiesResponse(BaseModel):
    capabilities: list[str] = Field(..., description="List of implemented system capabilities")
    supported_task_types: list[str] = Field(..., description="List of registered executable task types")
    max_concurrency: int = Field(..., description="Maximum allowed concurrent workers")
    max_queue_size: int = Field(..., description="Maximum capacity of task queue")
    realtime_streaming: bool = Field(default=True, description="Whether Server-Sent Events stream is enabled")
