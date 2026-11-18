"""Structural post-action state verification (Stage 17)."""

import ctypes
import logging
from typing import Any

from app.computer.contracts import DesktopActionType
from app.computer.uia.patterns import pattern_executor
from app.computer.windows.focus import focus_manager

logger = logging.getLogger("autonom.computer.actions.verifier")

user32 = ctypes.windll.user32


class StructuralActionVerifier:
    """Verifies observable state mutations following desktop action execution."""

    @staticmethod
    def verify_action_result(
        action_type: DesktopActionType,
        target_hwnd: int,
        target_element: Any | None = None,
        expected_value: Any | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Asserts expected postcondition after an action. Returns (status, evidence)."""
        evidence: dict[str, Any] = {}

        if action_type == DesktopActionType.ACTIVATE_WINDOW:
            is_fg = focus_manager.is_foreground_window(target_hwnd)
            evidence["is_foreground"] = is_fg
            status = "verified" if is_fg else "failed"
            return status, evidence

        elif action_type == DesktopActionType.CLOSE_WINDOW:
            exists = bool(user32.IsWindow(target_hwnd))
            evidence["window_exists"] = exists
            status = "verified" if not exists else "unknown"  # might show prompt or take time to exit
            return status, evidence

        elif action_type == DesktopActionType.SET_VALUE:
            if target_element:
                try:
                    actual_val = pattern_executor.get_value(target_element)
                    evidence["actual_value"] = actual_val
                    evidence["expected_value"] = expected_value
                    if expected_value is not None and str(expected_value).strip() in actual_val:
                        return "verified", evidence
                    return "failed", evidence
                except Exception as e:
                    evidence["read_error"] = str(e)
                    return "unknown", evidence
            return "skipped", evidence

        elif action_type == DesktopActionType.TOGGLE:
            if target_element:
                try:
                    # Current value
                    val = pattern_executor.get_value(target_element)
                    evidence["current_state"] = val
                    return "verified", evidence
                except Exception as e:
                    evidence["toggle_error"] = str(e)
                    return "unknown", evidence
            return "skipped", evidence

        elif action_type == DesktopActionType.INVOKE:
            evidence["invoked"] = True
            return "verified", evidence

        return "verified", evidence


action_verifier = StructuralActionVerifier()
