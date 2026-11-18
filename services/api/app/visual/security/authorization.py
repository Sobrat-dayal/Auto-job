"""Stage 14 authorization and policy integration for Visual Automation (Stage 18)."""

from __future__ import annotations

import logging
from typing import Optional

from app.computer.security.authorization import desktop_auth_policy
from .privacy import visual_privacy_filter

logger = logging.getLogger("autonom.visual.security.authorization")


class VisualAuthorizationEngine:
    """Validates authorization for screen capture and coordinate-based visual actions."""

    @staticmethod
    def validate_capture_target(
        target_title: Optional[str] = None,
        target_process_name: Optional[str] = None,
        target_pid: Optional[int] = None,
    ) -> tuple[bool, str]:
        """Validates that a capture target window is allowed and not a blocked sensitive window."""
        if target_title and visual_privacy_filter.is_window_sensitive(target_title):
            return False, f"Capture blocked: Window '{target_title}' is a protected credential or security window"

        if target_process_name:
            # Check process allowlist
            if not desktop_auth_policy.is_application_allowed(target_process_name):
                return False, f"Capture blocked: Application '{target_process_name}' is not in the approved desktop automation allowlist"

        return True, "Authorized"

    @staticmethod
    def validate_action_target(
        action_name: str,
        target_title: Optional[str] = None,
        target_process_name: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Validates that an input action is permitted on the specified application."""
        if target_title and visual_privacy_filter.is_window_sensitive(target_title):
            return False, f"Visual action '{action_name}' blocked: Window '{target_title}' is a protected credential or security window"

        if target_process_name:
            if not desktop_auth_policy.is_application_allowed(target_process_name):
                return False, f"Visual action '{action_name}' blocked: Application '{target_process_name}' is not in the approved desktop automation allowlist"

        return True, "Authorized"


visual_auth_engine = VisualAuthorizationEngine()
