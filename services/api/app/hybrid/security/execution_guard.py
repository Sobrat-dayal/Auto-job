"""Fail-closed Execution Guard and Emergency Stop integration for the Hybrid Engine."""

from __future__ import annotations

import ctypes
import logging
from typing import Optional

from app.hybrid.errors import EmergencyStopActiveError, SessionLockedError
from app.security.authorization.emergency import (
    EmergencyStopController,
    get_emergency_stop_controller,
)

logger = logging.getLogger("autonom.hybrid.security.execution_guard")


class HybridExecutionGuard:
    """Guards execution by asserting emergency stop status and Windows session interactivity."""

    def __init__(self, emergency_controller: Optional[EmergencyStopController] = None) -> None:
        self._emergency_controller = emergency_controller or get_emergency_stop_controller()
        self._local_killswitch: bool = False

    def is_emergency_stop_active(self) -> bool:
        """Check if global emergency stop or local hybrid killswitch is active."""
        if self._local_killswitch:
            return True
        return self._emergency_controller.is_emergency_stop_active

    def is_session_locked(self) -> bool:
        """Detect whether Windows workstation is currently locked."""
        try:
            # 0x0100 is DESKTOP_SWITCHDESKTOP
            hdesk = ctypes.windll.user32.OpenInputDesktop(0, False, 0x0100)
            if not hdesk:
                return True
            ctypes.windll.user32.CloseDesktop(hdesk)
            return False
        except Exception as exc:
            logger.debug("Workstation lock check error (ignoring): %s", exc)
            return False

    def ensure_execution_allowed(self) -> None:
        """Raise fail-closed exception if execution cannot safely proceed."""
        if self.is_emergency_stop_active():
            raise EmergencyStopActiveError(
                "Execution rejected: Global Emergency Stop or Hybrid Killswitch is active.",
                details={"emergency_stop": True},
            )

        if self.is_session_locked():
            raise SessionLockedError(
                "Execution rejected: Windows interactive desktop session is locked.",
                details={"session_locked": True},
            )

    async def activate_killswitch(self, reason: str = "Operator triggered hybrid killswitch") -> None:
        """Activate hybrid killswitch and propagate to global emergency stop."""
        self._local_killswitch = True
        await self._emergency_controller.activate_emergency_stop(
            activated_by="operator_hybrid_killswitch",
            reason=reason,
        )
        logger.warning("Hybrid killswitch activated: %s", reason)

    async def deactivate_killswitch(self) -> None:
        """Reset hybrid killswitch and global emergency stop."""
        self._local_killswitch = False
        await self._emergency_controller.clear_emergency_stop(cleared_by="operator_hybrid_reset")
        logger.info("Hybrid killswitch deactivated.")


# Global singleton instance
_execution_guard: Optional[HybridExecutionGuard] = None


def get_execution_guard() -> HybridExecutionGuard:
    """Return shared HybridExecutionGuard singleton."""
    global _execution_guard
    if _execution_guard is None:
        _execution_guard = HybridExecutionGuard()
    return _execution_guard
