"""Target Identity Validator and Freshness Verifier for the Hybrid Engine."""

from __future__ import annotations

import ctypes
import logging
from typing import Optional

from app.hybrid.contracts import InteractionTarget, SurfaceType, TargetType
from app.hybrid.errors import StaleTargetError

logger = logging.getLogger("autonom.hybrid.targets.identity")


class TargetIdentityValidator:
    """Verifies that target handles, selectors, and coordinates remain valid and fresh."""

    @staticmethod
    def validate_window_handle(hwnd: int, expected_pid: Optional[int] = None) -> bool:
        """Verify that a Win32 HWND is still valid and has not been recycled by another process."""
        if not hwnd or hwnd <= 0:
            return False

        try:
            # Check if window is still valid in user32
            is_window = bool(ctypes.windll.user32.IsWindow(hwnd))
            if not is_window:
                return False

            if expected_pid is not None and expected_pid > 0:
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value != expected_pid:
                    logger.warning(
                        "HWND %d recycled: expected PID %d but found %d",
                        hwnd,
                        expected_pid,
                        pid.value,
                    )
                    return False

            return True
        except Exception as exc:
            logger.warning("Error validating window handle %d: %s", hwnd, exc)
            return False

    @staticmethod
    def validate_target(target: InteractionTarget) -> bool:
        """Validate that the target's references are intact."""
        # 1. Native window target
        if target.window_handle:
            if not TargetIdentityValidator.validate_window_handle(target.window_handle, target.process_id):
                raise StaleTargetError(
                    f"Target window handle {target.window_handle} is invalid or has closed",
                    details={"target_id": target.target_id, "hwnd": target.window_handle},
                )

        # 2. Browser DOM target
        if target.surface_type == SurfaceType.BROWSER_DOM:
            if target.dom_selector == "":
                raise StaleTargetError(
                    "DOM selector is empty",
                    details={"target_id": target.target_id},
                )

        # 3. Visual coordinate target
        if target.surface_type == SurfaceType.CUSTOM_RENDERED and target.coordinates:
            x = target.coordinates.get("x")
            y = target.coordinates.get("y")
            if x is not None and y is not None:
                if x < 0 or y < 0:
                    raise StaleTargetError(
                        f"Negative coordinates provided: ({x}, {y})",
                        details={"target_id": target.target_id, "coords": target.coordinates},
                    )

        return True
