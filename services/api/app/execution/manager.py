"""Task execution manager orchestrating creation, queuing, cancellation, and event publication."""

import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import (
    TaskCancelledError,
    TaskNotFoundError,
)
from app.events.models import EventType
from app.execution.context import TaskExecutionContext
from app.execution.handlers import HandlerRegistry
from app.execution.state_machine import validate_transition
from app.schemas.events import EventEnvelope
from app.schemas.system import ErrorDetail
from app.schemas.tasks import (
    TaskCancelResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskResultResponse,
    TaskState,
)

if TYPE_CHECKING:
    from app.events.bus import EventBus
    from app.workers.manager import WorkerManager

logger = logging.getLogger("autonom.execution")


class TaskExecutionManager:
    """Manages task lifecycle, state transitions, handler dispatch, and real-time event reporting."""

    def __init__(
        self,
        event_bus: "EventBus",
        worker_manager: "WorkerManager",
        handler_registry: HandlerRegistry | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.worker_manager = worker_manager
        self.handler_registry = handler_registry or HandlerRegistry()
        self._tasks: dict[str, TaskResponse] = {}
        self._contexts: dict[str, TaskExecutionContext] = {}
        self._lock = asyncio.Lock()

    @property
    def active_tasks_count(self) -> int:
        """Returns the number of tasks currently in non-terminal, running states."""
        return sum(1 for t in self._tasks.values() if t.state.is_active)

    async def create_task(
        self,
        req: TaskCreateRequest,
        correlation_id: str | None = None,
    ) -> TaskResponse:
        """Creates a new task record, validates handler registration, and enqueues for worker processing."""
        # 1. Validate task handler registration
        self.handler_registry.get(req.task_type)

        task_id = f"tsk-{uuid4().hex[:12]}"
        cid = correlation_id or f"cor-{uuid4().hex[:8]}"
        now = datetime.now(UTC)

        task = TaskResponse(
            task_id=task_id,
            task_type=req.task_type,
            state=TaskState.CREATED,
            priority=req.priority,
            created_at=now,
            metadata=req.metadata,
            correlation_id=cid,
        )

        async with self._lock:
            self._tasks[task_id] = task

        # Publish task.created event
        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.TASK_CREATED,
                task_id=task_id,
                correlation_id=cid,
                payload={"task_type": req.task_type, "priority": req.priority.value},
            )
        )

        # Transition to QUEUED and push to WorkerManager
        validate_transition(task.state, TaskState.QUEUED, task_id=task_id)
        try:
            await self.worker_manager.enqueue_task(task_id, priority=req.priority)
            task.state = TaskState.QUEUED
        except Exception:
            # If queue is full, mark task as failed and clean up
            task.state = TaskState.FAILED
            task.error = ErrorDetail(
                code="QUEUE_SATURATED",
                message="Task queue capacity reached; task could not be enqueued.",
                retryable=True,
            )
            task.completed_at = datetime.now(UTC)
            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_FAILED,
                    task_id=task_id,
                    correlation_id=cid,
                    payload={"error": task.error.model_dump()},
                )
            )
            raise

        # Publish task.queued event
        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.TASK_QUEUED,
                task_id=task_id,
                correlation_id=cid,
                payload={"queue_size": self.worker_manager.queue_size},
            )
        )

        # Store task request payload internally for handler execution
        task.metadata["_payload"] = req.payload
        if req.timeout_seconds:
            task.metadata["_timeout_seconds"] = req.timeout_seconds

        logger.info(f"Created and queued task {task_id} (type: {req.task_type}, priority: {req.priority.value})")
        return task

    async def execute_task(self, task_id: str, worker_id: str) -> None:
        """Executes a task handler on the specified worker, enforcing timeouts and safety boundaries."""
        task = self._tasks.get(task_id)
        if not task:
            logger.warning(f"Worker {worker_id} attempted to execute missing task {task_id}")
            return

        # If already cancelled while in queue, do not execute
        if task.state == TaskState.CANCELLED:
            logger.info(f"Task {task_id} was cancelled before execution on {worker_id}")
            return

        # Transition to RUNNING
        validate_transition(task.state, TaskState.RUNNING, task_id=task_id)
        task.state = TaskState.RUNNING
        task.started_at = datetime.now(UTC)

        context = TaskExecutionContext(
            task_id=task_id,
            task_type=task.task_type,
            correlation_id=task.correlation_id,
            event_bus=self.event_bus,
            manager=self,
        )
        self._contexts[task_id] = context

        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.TASK_STARTED,
                task_id=task_id,
                correlation_id=task.correlation_id,
                payload={"worker_id": worker_id},
            )
        )

        handler = self.handler_registry.get(task.task_type)
        payload = task.metadata.get("_payload", {})
        timeout = float(task.metadata.get("_timeout_seconds") or settings.task_default_timeout_seconds)

        try:
            result = await asyncio.wait_for(handler.execute(payload, context), timeout=timeout)
            validate_transition(task.state, TaskState.COMPLETED, task_id=task_id)
            task.state = TaskState.COMPLETED
            task.progress = 100.0
            task.progress_message = "Completed successfully"
            task.result = result
            task.completed_at = datetime.now(UTC)

            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_COMPLETED,
                    task_id=task_id,
                    correlation_id=task.correlation_id,
                    payload={"result": result},
                )
            )
            logger.info(f"Task {task_id} completed successfully on {worker_id}")

        except TimeoutError:
            validate_transition(task.state, TaskState.FAILED, task_id=task_id)
            task.state = TaskState.FAILED
            task.completed_at = datetime.now(UTC)
            task.error = ErrorDetail(
                code="TASK_TIMEOUT",
                message=f"Task execution exceeded {timeout} seconds timeout limit.",
                retryable=True,
            )
            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_FAILED,
                    task_id=task_id,
                    correlation_id=task.correlation_id,
                    payload={"error": task.error.model_dump()},
                )
            )
            logger.warning(f"Task {task_id} timed out after {timeout}s on {worker_id}")

        except TaskCancelledError as exc:
            validate_transition(task.state, TaskState.CANCELLED, task_id=task_id)
            task.state = TaskState.CANCELLED
            task.completed_at = datetime.now(UTC)
            task.progress_message = exc.message
            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_CANCELLED,
                    task_id=task_id,
                    correlation_id=task.correlation_id,
                    payload={"reason": exc.message},
                )
            )
            logger.info(f"Task {task_id} cancelled during execution: {exc.message}")

        except Exception as exc:  # noqa: BLE001
            validate_transition(task.state, TaskState.FAILED, task_id=task_id)
            task.state = TaskState.FAILED
            task.completed_at = datetime.now(UTC)
            task.error = ErrorDetail(
                code="TASK_EXECUTION_ERROR",
                message=str(exc),
                retryable=getattr(exc, "retryable", False),
            )
            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_FAILED,
                    task_id=task_id,
                    correlation_id=task.correlation_id,
                    payload={"error": task.error.model_dump()},
                )
            )
            logger.error(f"Task {task_id} failed with error on {worker_id}: {exc}")
        finally:
            self._contexts.pop(task_id, None)

    async def cancel_task(self, task_id: str, reason: str = "User requested cancellation") -> TaskCancelResponse:
        """Requests cancellation for an active or queued task."""
        task = self._tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        if task.state.is_terminal:
            return TaskCancelResponse(
                task_id=task_id,
                cancelled=False,
                message=f"Task is already in terminal state '{task.state.value}'.",
                state=task.state,
            )

        if task.state in (TaskState.CREATED, TaskState.QUEUED):
            validate_transition(task.state, TaskState.CANCELLED, task_id=task_id)
            task.state = TaskState.CANCELLED
            task.completed_at = datetime.now(UTC)
            task.progress_message = reason

            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.TASK_CANCELLED,
                    task_id=task_id,
                    correlation_id=task.correlation_id,
                    payload={"reason": reason},
                )
            )
            return TaskCancelResponse(
                task_id=task_id,
                cancelled=True,
                message=f"Task cancelled while in queue: {reason}",
                state=TaskState.CANCELLED,
            )

        if task.state == TaskState.RUNNING:
            context = self._contexts.get(task_id)
            if context:
                context.request_cancellation()
            return TaskCancelResponse(
                task_id=task_id,
                cancelled=True,
                message="Cancellation request sent to active running task.",
                state=TaskState.RUNNING,
            )

        # Other intermediate active states (Planning, WaitingForDependencies, Paused)
        validate_transition(task.state, TaskState.CANCELLED, task_id=task_id)
        task.state = TaskState.CANCELLED
        task.completed_at = datetime.now(UTC)
        task.progress_message = reason
        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.TASK_CANCELLED,
                task_id=task_id,
                correlation_id=task.correlation_id,
                payload={"reason": reason},
            )
        )
        return TaskCancelResponse(
            task_id=task_id,
            cancelled=True,
            message=f"Task cancelled: {reason}",
            state=TaskState.CANCELLED,
        )

    async def record_task_progress(
        self,
        task_id: str,
        progress: float,
        message: str,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Updates stored progress and broadcasts a real-time task.progress event."""
        task = self._tasks.get(task_id)
        if not task:
            return

        task.progress = progress
        task.progress_message = message

        payload: dict[str, Any] = {
            "progress": progress,
            "message": message,
            "stage": stage,
        }
        if details:
            payload["details"] = details

        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.TASK_PROGRESS,
                task_id=task_id,
                correlation_id=task.correlation_id,
                payload=payload,
            )
        )

    def get_task(self, task_id: str) -> TaskResponse:
        """Retrieves task by ID or raises TaskNotFoundError."""
        task = self._tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(
        self,
        state: TaskState | None = None,
        task_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TaskListResponse:
        """Returns paginated and filtered tasks."""
        filtered = list(self._tasks.values())
        if state is not None:
            filtered = [t for t in filtered if t.state == state]
        if task_type is not None:
            filtered = [t for t in filtered if t.task_type == task_type]

        # Sort reverse chronologically
        filtered.sort(key=lambda t: t.created_at, reverse=True)
        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return TaskListResponse(
            tasks=paginated,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_task_result(self, task_id: str) -> TaskResultResponse:
        """Returns final execution result or current non-completed state for a task."""
        task = self.get_task(task_id)
        elapsed = None
        if task.started_at and task.completed_at:
            elapsed = round((task.completed_at - task.started_at).total_seconds(), 3)

        return TaskResultResponse(
            task_id=task.task_id,
            state=task.state,
            result=task.result,
            error=task.error,
            execution_time_seconds=elapsed,
        )
