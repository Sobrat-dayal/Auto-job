"""Task execution manager orchestrating creation, queuing, cancellation, event publication, and SQLite persistence."""

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
from app.db.engine import get_db_session
from app.events.models import EventType
from app.execution.context import TaskExecutionContext
from app.execution.handlers import HandlerRegistry
from app.execution.state_machine import validate_transition
from app.repositories import TaskEventRepository, TaskRepository
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


def _ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


class TaskExecutionManager:
    """Manages task lifecycle, state transitions, handler dispatch, real-time events, and persistent SQLite storage."""

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

    async def load_persisted_tasks(self) -> None:
        """Loads all existing tasks from SQLite into memory and reconciles interrupted tasks."""
        try:
            async with get_db_session() as session:
                repo = TaskRepository(session)
                # First reconcile any tasks left running by previous process
                interrupted = await repo.reconcile_interrupted_tasks()
                all_tasks = await repo.list_tasks(limit=1000)

                for t in all_tasks:
                    resp = TaskResponse(
                        task_id=t.id,
                        task_type=t.task_type,
                        state=TaskState(t.status),
                        priority=t.priority,
                        progress=t.progress,
                        progress_message=t.progress_message,
                        created_at=_ensure_utc(t.created_at) or datetime.now(UTC),
                        started_at=_ensure_utc(t.started_at),
                        completed_at=_ensure_utc(t.completed_at),
                        correlation_id=t.correlation_id,
                        result=t.output_result_json,
                        error=ErrorDetail(**t.error_info_json) if t.error_info_json else None,
                    )
                    self._tasks[t.id] = resp

                if interrupted:
                    logger.warning(f"Reconciled {len(interrupted)} interrupted tasks from prior run: {[i.id for i in interrupted]}")
                logger.info(f"Loaded {len(self._tasks)} persisted tasks into manager cache.")
        except Exception as exc:
            logger.warning(f"Could not load persisted tasks from database: {exc}")

    reconcile_on_startup = load_persisted_tasks

    async def create_task(
        self,
        req: TaskCreateRequest,
        correlation_id: str | None = None,
    ) -> TaskResponse:
        """Creates a new task record, persists to SQLite, validates handler registration, and enqueues for worker processing."""
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

        # Persist created task to database
        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                event_repo = TaskEventRepository(session)
                await task_repo.create_task(
                    task_id=task_id,
                    task_type=req.task_type,
                    priority=req.priority.value,
                    title=f"Task {req.task_type}",
                    payload=req.payload,
                    correlation_id=cid,
                    timeout_seconds=float(req.timeout_seconds or settings.task_default_timeout_seconds),
                )
                await event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.TASK_CREATED,
                    state_transition="Created",
                    metadata=req.payload,
                    correlation_id=cid,
                )
        except Exception as exc:
            logger.error(f"Failed to persist task creation {task_id}: {exc}")

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

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.update_task_state(task_id, TaskState.QUEUED.value)
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_QUEUED,
                        state_transition="Created->Queued",
                        metadata={"queue_size": self.worker_manager.queue_size},
                        correlation_id=cid,
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist queued state in DB for {task_id}: {db_exc}")

        except Exception:
            # If queue is full, mark task as failed and clean up
            task.state = TaskState.FAILED
            task.error = ErrorDetail(
                code="QUEUE_SATURATED",
                message="Task queue capacity reached; task could not be enqueued.",
                retryable=True,
            )
            task.completed_at = datetime.now(UTC)

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    await task_repo.fail_task(task_id, task.error.model_dump())
            except Exception as db_exc:
                logger.error(f"Failed to record queue saturation in DB for {task_id}: {db_exc}")

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
        """Executes a task handler on the specified worker, persisting transitions and results."""
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

        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                event_repo = TaskEventRepository(session)
                await task_repo.update_task_state(task_id, TaskState.RUNNING.value)
                await event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.TASK_STARTED,
                    state_transition="Queued->Running",
                    metadata={"worker_id": worker_id},
                    correlation_id=task.correlation_id,
                )
        except Exception as exc:
            logger.error(f"Failed to persist task start {task_id}: {exc}")

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

        start_time = datetime.now(UTC)
        try:
            result = await asyncio.wait_for(handler.execute(payload, context), timeout=timeout)
            end_time = datetime.now(UTC)
            validate_transition(task.state, TaskState.COMPLETED, task_id=task_id)
            task.state = TaskState.COMPLETED
            task.progress = 100.0
            task.progress_message = "Completed successfully"
            task.result = result
            task.completed_at = end_time

            # Persist completion and worker run
            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.complete_task(task_id, result)
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_COMPLETED,
                        state_transition="Running->Completed",
                        metadata={"result": result},
                        correlation_id=task.correlation_id,
                    )
                    await task_repo.record_worker_run(
                        task_id=task_id,
                        worker_id=worker_id,
                        start_time=start_time,
                        end_time=end_time,
                        execution_result_json=result,
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist completion for {task_id}: {db_exc}")

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
            end_time = datetime.now(UTC)
            validate_transition(task.state, TaskState.FAILED, task_id=task_id)
            task.state = TaskState.FAILED
            task.completed_at = end_time
            task.error = ErrorDetail(
                code="TASK_TIMEOUT",
                message=f"Task execution exceeded {timeout} seconds timeout limit.",
                retryable=True,
            )

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.fail_task(task_id, task.error.model_dump())
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_FAILED,
                        state_transition="Running->Failed",
                        metadata={"error": task.error.model_dump()},
                        correlation_id=task.correlation_id,
                    )
                    await task_repo.record_worker_run(
                        task_id=task_id,
                        worker_id=worker_id,
                        start_time=start_time,
                        end_time=end_time,
                        failure_class="TASK_TIMEOUT",
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist timeout for {task_id}: {db_exc}")

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
            end_time = datetime.now(UTC)
            validate_transition(task.state, TaskState.CANCELLED, task_id=task_id)
            task.state = TaskState.CANCELLED
            task.completed_at = end_time
            task.progress_message = exc.message

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.cancel_task(task_id, reason=exc.message)
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_CANCELLED,
                        state_transition="Running->Cancelled",
                        metadata={"reason": exc.message},
                        correlation_id=task.correlation_id,
                    )
                    await task_repo.record_worker_run(
                        task_id=task_id,
                        worker_id=worker_id,
                        start_time=start_time,
                        end_time=end_time,
                        failure_class="TASK_CANCELLED",
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist cancellation for {task_id}: {db_exc}")

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
            end_time = datetime.now(UTC)
            validate_transition(task.state, TaskState.FAILED, task_id=task_id)
            task.state = TaskState.FAILED
            task.completed_at = end_time
            task.error = ErrorDetail(
                code="TASK_EXECUTION_ERROR",
                message=str(exc),
                retryable=getattr(exc, "retryable", False),
            )

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.fail_task(task_id, task.error.model_dump())
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_FAILED,
                        state_transition="Running->Failed",
                        metadata={"error": task.error.model_dump()},
                        correlation_id=task.correlation_id,
                    )
                    await task_repo.record_worker_run(
                        task_id=task_id,
                        worker_id=worker_id,
                        start_time=start_time,
                        end_time=end_time,
                        failure_class="TASK_EXECUTION_ERROR",
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist failure for {task_id}: {db_exc}")

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
        """Requests cancellation for an active or queued task, persisting state."""
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

            try:
                async with get_db_session() as session:
                    task_repo = TaskRepository(session)
                    event_repo = TaskEventRepository(session)
                    await task_repo.cancel_task(task_id, reason=reason)
                    await event_repo.record_event(
                        task_id=task_id,
                        event_type=EventType.TASK_CANCELLED,
                        state_transition="Queued->Cancelled",
                        metadata={"reason": reason},
                        correlation_id=task.correlation_id,
                    )
            except Exception as db_exc:
                logger.error(f"Failed to persist cancellation for {task_id}: {db_exc}")

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

        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                event_repo = TaskEventRepository(session)
                await task_repo.cancel_task(task_id, reason=reason)
                await event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.TASK_CANCELLED,
                    state_transition="Active->Cancelled",
                    metadata={"reason": reason},
                    correlation_id=task.correlation_id,
                )
        except Exception as db_exc:
            logger.error(f"Failed to persist cancel for {task_id}: {db_exc}")

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

        try:
            async with get_db_session() as session:
                task_repo = TaskRepository(session)
                await task_repo.update_task_state(task_id, task.state.value, progress=progress, progress_message=message)
        except Exception as db_exc:
            logger.error(f"Failed to update progress in DB for {task_id}: {db_exc}")

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
        """Retrieves task by ID from memory cache, raising TaskNotFoundError if missing."""
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
        """Returns paginated and filtered tasks loaded from memory cache."""
        filtered = list(self._tasks.values())
        if state is not None:
            filtered = [t for t in filtered if t.state == state]
        if task_type is not None:
            filtered = [t for t in filtered if t.task_type == task_type]

        # Sort reverse chronologically
        filtered.sort(key=lambda t: _ensure_utc(t.created_at) or datetime.min.replace(tzinfo=UTC), reverse=True)
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

    async def get_task_history(self, task_id: str) -> list[dict[str, Any]]:
        """Retrieves durable event history for a task from SQLite task_events."""
        async with get_db_session() as session:
            repo = TaskEventRepository(session)
            events = await repo.list_events_for_task(task_id)
            return [
                {
                    "event_id": e.id,
                    "event_type": e.event_type,
                    "timestamp": e.timestamp.isoformat(),
                    "state_transition": e.state_transition,
                    "sequence_num": e.sequence_num,
                    "metadata": e.metadata_json,
                    "correlation_id": e.correlation_id,
                }
                for e in events
            ]
