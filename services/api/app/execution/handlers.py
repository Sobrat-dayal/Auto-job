"""TaskHandler base abstraction, HandlerRegistry, and built-in safe demonstration handlers."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from app.core.exceptions import TaskCancelledError, TaskExecutionError, UnknownTaskTypeError
from app.execution.context import TaskExecutionContext


class TaskHandler(ABC):
    """Abstract base class for all task execution handlers."""

    @abstractmethod
    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> Any:
        """Executes the task logic using provided input payload and execution context."""


class ComputeEchoHandler(TaskHandler):
    """Deterministic demonstration task handler that reverses/transforms input payload."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        text = str(payload.get("text", "AUTONOM"))
        repeat = max(1, min(int(payload.get("repeat", 1)), 10))

        await context.report_progress(25.0, "Validating input parameters", stage="validation")
        await asyncio.sleep(0.05)

        await context.report_progress(50.0, "Transforming text payload", stage="processing")
        reversed_text = text[::-1]
        repeated_text = " ".join([reversed_text] * repeat)
        await asyncio.sleep(0.05)

        await context.report_progress(100.0, "Echo transformation completed", stage="finalizing")
        return {
            "original_text": text,
            "transformed_text": repeated_text,
            "length": len(repeated_text),
            "repeat_count": repeat,
            "status": "success",
        }


class SleepProgressHandler(TaskHandler):
    """Cancellable, bounded demonstration handler that reports progressive status updates."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        steps = max(1, min(int(payload.get("steps", 5)), 20))
        step_delay = max(0.05, min(float(payload.get("step_delay", 0.3)), 5.0))
        fail_at_step = payload.get("fail_at_step")

        for step in range(1, steps + 1):
            # Cooperative cancellation check
            if context.is_cancellation_requested():
                raise TaskCancelledError(
                    task_id=context.task_id,
                    reason=f"Cancellation requested at step {step}/{steps}",
                )

            # Optional simulated failure
            if fail_at_step is not None and step == int(fail_at_step):
                raise TaskExecutionError(
                    message=f"Simulated execution failure at step {step} of {steps}.",
                    task_id=context.task_id,
                    retryable=False,
                )

            percent = round((step / steps) * 100.0, 1)
            msg = f"Executing step {step} of {steps} ({percent}%)"
            await context.report_progress(percent, msg, stage=f"step_{step}")
            await asyncio.sleep(step_delay)

        return {
            "steps_completed": steps,
            "step_delay": step_delay,
            "message": f"Successfully completed all {steps} progress steps.",
            "status": "success",
        }


class HandlerRegistry:
    """Registry maintaining approved executable task handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, TaskHandler] = {}
        # Register safe built-in demonstration handlers
        self.register("compute.echo", ComputeEchoHandler())
        self.register("test.sleep_progress", SleepProgressHandler())

    def register(self, task_type: str, handler: TaskHandler) -> None:
        """Registers a task handler under a distinct task type key."""
        self._handlers[task_type] = handler

    def get(self, task_type: str) -> TaskHandler:
        """Retrieves handler for task type or raises UnknownTaskTypeError."""
        handler = self._handlers.get(task_type)
        if not handler:
            raise UnknownTaskTypeError(task_type, list(self._handlers.keys()))
        return handler

    def list_types(self) -> list[str]:
        """Returns list of all currently registered task type identifiers."""
        return sorted(self._handlers.keys())
