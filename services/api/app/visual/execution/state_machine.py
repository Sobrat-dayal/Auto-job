"""Visual task state machine.

Manages transitions between visual task execution states with validation,
timing, and state change event tracking.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

from ..contracts import VisualTaskStatus

logger = logging.getLogger(__name__)

# Valid transitions
ALLOWED_TRANSITIONS: dict[VisualTaskStatus, set[VisualTaskStatus]] = {
    VisualTaskStatus.PENDING: {VisualTaskStatus.OBSERVING, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.OBSERVING: {VisualTaskStatus.GROUNDING, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.GROUNDING: {VisualTaskStatus.ACTING, VisualTaskStatus.RECOVERING, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.ACTING: {VisualTaskStatus.VERIFYING, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.VERIFYING: {VisualTaskStatus.COMPLETED, VisualTaskStatus.RECOVERING, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.RECOVERING: {VisualTaskStatus.OBSERVING, VisualTaskStatus.GROUNDING, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED},
    VisualTaskStatus.COMPLETED: set(),
    VisualTaskStatus.FAILED: set(),
    VisualTaskStatus.CANCELLED: set(),
}


class VisualStateMachine:
    """Tracks state and validates transitions for visual tasks."""

    def __init__(self, task_id: str, initial_status: VisualTaskStatus = VisualTaskStatus.PENDING) -> None:
        self.task_id = task_id
        self.current_status = initial_status
        self.history: list[dict[str, str]] = [
            {
                "status": initial_status.value,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "reason": "Task initialized",
            }
        ]

    def transition_to(self, new_status: VisualTaskStatus, reason: str = "") -> bool:
        """Transitions to a new status if valid. Returns True if transitioned."""
        allowed = ALLOWED_TRANSITIONS.get(self.current_status, set())
        if new_status not in allowed:
            logger.warning(
                f"Invalid visual task state transition for {self.task_id}: {self.current_status.value} -> {new_status.value}"
            )
            return False

        logger.info(f"Visual task {self.task_id} transitioned: {self.current_status.value} -> {new_status.value} ({reason})")
        self.current_status = new_status
        self.history.append(
            {
                "status": new_status.value,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "reason": reason,
            }
        )
        return True

    @property
    def is_terminal(self) -> bool:
        return self.current_status in (VisualTaskStatus.COMPLETED, VisualTaskStatus.FAILED, VisualTaskStatus.CANCELLED)
