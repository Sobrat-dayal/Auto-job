"""Emergency Stop and safety guardrails for Windows desktop automation (Stage 17)."""

import logging
from app.computer.windows.sessions import session_manager
from app.security.authorization.emergency import get_emergency_stop_controller

logger = logging.getLogger("autonom.computer.security.guard")


class DesktopSecurityGuard:
    """Enforces fail-closed Emergency Stop, session lock detection, and integrity boundaries."""

    @staticmethod
    def assert_automation_allowed() -> None:
        """Asserts that Emergency Stop is NOT active and the Windows desktop is accessible."""
        e_stop = get_emergency_stop_controller()
        if e_stop.is_emergency_stop_active:
            state = e_stop.get_state()
            reason = getattr(state, "emergency_stop_reason", None) or getattr(state, "reason", None) or "Emergency Stop is active"
            logger.warning(f"Desktop automation blocked: {reason}")
            raise PermissionError(f"Emergency Stop active: {reason}")

        session_info = session_manager.get_session_info()
        if session_info.is_locked:
            logger.warning("Desktop automation blocked: Windows session is locked")
            raise PermissionError("Desktop automation unavailable: Windows interactive session is locked")

        if not session_info.is_interactive:
            logger.warning("Desktop automation blocked: session is non-interactive")
            raise PermissionError("Desktop automation unavailable: no interactive desktop attached")


desktop_security_guard = DesktopSecurityGuard()
