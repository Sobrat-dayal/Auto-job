"""Task management REST API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import AuthDep, TaskManagerDep
from app.schemas.tasks import (
    TaskCancelResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskResultResponse,
    TaskState,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreateRequest,
    manager: TaskManagerDep,
    _auth: AuthDep,
) -> TaskResponse:
    """Submits a new task for asynchronous background worker execution."""
    return await manager.create_task(req)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    manager: TaskManagerDep,
    _auth: AuthDep,
    state: Annotated[TaskState | None, Query(description="Filter tasks by state")] = None,
    task_type: Annotated[str | None, Query(description="Filter tasks by registered handler type")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum tasks to return")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> TaskListResponse:
    """Lists tasks with optional state/type filtering and bounded pagination."""
    return manager.list_tasks(state=state, task_type=task_type, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    manager: TaskManagerDep,
    _auth: AuthDep,
) -> TaskResponse:
    """Retrieves full task metadata and current state."""
    return manager.get_task(task_id)


@router.post("/{task_id}/cancel", response_model=TaskCancelResponse)
async def cancel_task(
    task_id: str,
    manager: TaskManagerDep,
    _auth: AuthDep,
    reason: Annotated[str, Query(description="Reason for cancellation")] = "User requested cancellation",
) -> TaskCancelResponse:
    """Requests cooperative cancellation of a queued or actively running task."""
    return await manager.cancel_task(task_id, reason=reason)


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    manager: TaskManagerDep,
    _auth: AuthDep,
) -> TaskResultResponse:
    """Retrieves the execution result or current non-completed state of a task."""
    return manager.get_task_result(task_id)
