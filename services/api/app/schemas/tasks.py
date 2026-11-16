"""Pydantic schemas for task models, requests, responses, and state machine."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.system import ErrorDetail


class TaskState(str, Enum):
    """The 11 durable task states defined in the AUTONOM architecture."""

    CREATED = "Created"
    QUEUED = "Queued"
    PLANNING = "Planning"
    WAITING_FOR_DEPENDENCIES = "WaitingForDependencies"
    RUNNING = "Running"
    WAITING_FOR_AUTHORIZATION = "WaitingForAuthorization"
    PAUSED = "Paused"
    RETRYING = "Retrying"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED)

    @property
    def is_active(self) -> bool:
        return self in (
            TaskState.QUEUED,
            TaskState.PLANNING,
            TaskState.WAITING_FOR_DEPENDENCIES,
            TaskState.RUNNING,
            TaskState.WAITING_FOR_AUTHORIZATION,
            TaskState.RETRYING,
        )


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreateRequest(BaseModel):
    task_type: str = Field(
        ..., description="Registered task handler identifier (e.g. compute.echo, test.sleep_progress)"
    )
    payload: dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to the task handler")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Execution priority")
    timeout_seconds: float | None = Field(default=None, description="Optional custom timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional caller-defined task metadata")


class TaskProgressPayload(BaseModel):
    progress: float = Field(..., ge=0.0, le=100.0, description="Percentage of completion (0.0 to 100.0)")
    message: str = Field(..., description="Progress description or status message")
    stage: str | None = Field(default=None, description="Optional current execution stage name")


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of registered task handler")
    state: TaskState = Field(..., description="Current task state")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task execution priority")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: datetime | None = Field(default=None, description="Execution start timestamp")
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Current progress percent")
    progress_message: str | None = Field(default=None, description="Latest progress message")
    result: Any | None = Field(default=None, description="Task output payload when completed")
    error: ErrorDetail | None = Field(default=None, description="Error details when failed or timed out")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata associated with task")
    correlation_id: str = Field(..., description="Correlation ID for distributed tracing")


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse] = Field(..., description="List of task records")
    total: int = Field(..., description="Total tasks matching filter")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Offset used")


class TaskResultResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    state: TaskState = Field(..., description="Final or current task state")
    result: Any | None = Field(default=None, description="Execution result when completed")
    error: ErrorDetail | None = Field(default=None, description="Error detail if failed")
    execution_time_seconds: float | None = Field(default=None, description="Elapsed execution duration")


class TaskCancelResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    cancelled: bool = Field(..., description="Whether cancellation request was accepted or processed")
    message: str = Field(..., description="Cancellation status message")
    state: TaskState = Field(..., description="State of task after cancellation request")
