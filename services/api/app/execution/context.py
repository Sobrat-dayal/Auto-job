"""Execution context passed to task handlers for progress reporting and cancellation checks."""

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.events.bus import EventBus
    from app.execution.manager import TaskExecutionManager


class TaskExecutionContext:
    """Execution context provided to TaskHandler instances.

    Allows handlers to report real-time progress and cooperatively check for cancellation.
    """

    def __init__(
        self,
        task_id: str,
        task_type: str,
        correlation_id: str,
        event_bus: "EventBus",
        manager: "TaskExecutionManager",
    ) -> None:
        self.task_id = task_id
        self.task_type = task_type
        self.correlation_id = correlation_id
        self.event_bus = event_bus
        self.manager = manager
        self._cancellation_requested = False
        self._cancellation_event = asyncio.Event()

    def request_cancellation(self) -> None:
        """Flags that cancellation has been requested for this task."""
        self._cancellation_requested = True
        self._cancellation_event.set()

    def is_cancellation_requested(self) -> bool:
        """Returns True if the task has received a cancellation request."""
        return self._cancellation_requested

    async def report_progress(
        self,
        progress: float,
        message: str,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Reports execution progress, updating task record and publishing a task.progress event."""
        await self.manager.record_task_progress(
            task_id=self.task_id,
            progress=progress,
            message=message,
            stage=stage,
            details=details,
        )
