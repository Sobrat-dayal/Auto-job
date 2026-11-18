"""Hybrid Task State Machine managing task lifecycle transitions."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.contracts import HybridTaskStatus

logger = logging.getLogger("autonom.hybrid.execution.state_machine")

VALID_TRANSITIONS: dict[HybridTaskStatus, set[HybridTaskStatus]] = {
    HybridTaskStatus.PENDING: {
        HybridTaskStatus.ROUTING,
        HybridTaskStatus.CANCELLED,
        HybridTaskStatus.BLOCKED_POLICY,
    },
    HybridTaskStatus.ROUTING: {
        HybridTaskStatus.EXECUTING,
        HybridTaskStatus.BLOCKED_POLICY,
        HybridTaskStatus.WAITING_APPROVAL,
        HybridTaskStatus.FAILED,
        HybridTaskStatus.CANCELLED,
    },
    HybridTaskStatus.EXECUTING: {
        HybridTaskStatus.VERIFYING,
        HybridTaskStatus.FALLING_BACK,
        HybridTaskStatus.FAILED,
        HybridTaskStatus.COMPLETED,
        HybridTaskStatus.CANCELLED,
    },
    HybridTaskStatus.VERIFYING: {
        HybridTaskStatus.COMPLETED,
        HybridTaskStatus.FALLING_BACK,
        HybridTaskStatus.FAILED,
        HybridTaskStatus.CANCELLED,
    },
    HybridTaskStatus.FALLING_BACK: {
        HybridTaskStatus.ROUTING,
        HybridTaskStatus.EXECUTING,
        HybridTaskStatus.FAILED,
        HybridTaskStatus.BLOCKED_POLICY,
        HybridTaskStatus.CANCELLED,
    },
    HybridTaskStatus.COMPLETED: set(),
    HybridTaskStatus.FAILED: set(),
    HybridTaskStatus.CANCELLED: set(),
    HybridTaskStatus.BLOCKED_POLICY: set(),
    HybridTaskStatus.WAITING_APPROVAL: {
        HybridTaskStatus.ROUTING,
        HybridTaskStatus.CANCELLED,
    },
}


class HybridStateMachine:
    """Enforces deterministic lifecycle transitions for hybrid tasks."""

    def __init__(self, initial_status: HybridTaskStatus = HybridTaskStatus.PENDING) -> None:
        self._current_status = initial_status

    @property
    def current_status(self) -> HybridTaskStatus:
        return self._current_status

    def transition_to(self, new_status: HybridTaskStatus) -> HybridTaskStatus:
        """Attempt to transition to new status. Raises ValueError if illegal."""
        allowed = VALID_TRANSITIONS.get(self._current_status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Illegal state transition from {self._current_status.value} to {new_status.value}. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        logger.debug("State transition: %s -> %s", self._current_status.value, new_status.value)
        self._current_status = new_status
        return self._current_status
