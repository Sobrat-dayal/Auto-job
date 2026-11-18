"""Emergency Stop and safety guardrails for Visual Automation (Stage 18)."""

from __future__ import annotations

import logging
from app.computer.windows.sessions import session_manager
from app.security.authorization.emergency import get_emergency_stop_controller

logger = logging.getLogger("autonom.visual.security.guard")


class VisualSecurityGuard:
    """Enforces fail-closed Emergency Stop, session lock detection, and integrity boundaries for visual operations."""

    @staticmethod
    def assert_visual_operation_allowed(operation_name: str = "visual operation") -> None:
        """Asserts that Emergency Stop is NOT active and the Windows desktop is interactive."""
        e_stop = get_emergency_stop_controller()
        if e_stop.is_emergency_stop_active:
            state = e_stop.get_state()
            reason = getattr(state, "emergency_stop_reason", None) or getattr(state, "reason", None) or "Emergency Stop is active"
            logger.warning(f"Visual operation '{operation_name}' blocked: {reason}")
            raise PermissionError(f"Emergency Stop active: {reason}")

        if e_stop.is_automation_paused:
            state = e_stop.get_state()
            reason = getattr(state, "automation_pause_reason", None) or "Automation is paused"
            logger.warning(f"Visual operation '{operation_name}' blocked: {reason}")
            raise PermissionError(f"Automation paused: {reason}")

        session_info = session_manager.get_session_info()
        if session_info.is_locked:
            logger.warning(f"Visual operation '{operation_name}' blocked: Windows session is locked")
            raise PermissionError("Visual automation unavailable: Windows interactive session is locked")

        if not session_info.is_interactive:
            logger.warning(f"Visual operation '{operation_name}' blocked: session is non-interactive")
            raise PermissionError("Visual automation unavailable: no interactive desktop attached")


visual_security_guard = VisualSecurityGuard()
