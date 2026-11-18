"""Tests for Desktop Actions, Security Guardrails, and Verification (Stage 17)."""

import pytest
from app.computer.actions.dialogs import dialog_safety_guard
from app.computer.contracts import DesktopActionRequest, DesktopActionType
from app.computer.security.guard import desktop_security_guard
from app.computer.security.privacy import privacy_filter
from app.security.authorization.emergency import get_emergency_stop_controller


def test_file_dialog_safety_guard():
    """Verify FileDialogSafetyGuard allows safe user paths and rejects Windows system directories or path traversal."""
    # Allowed user path
    allowed, _ = dialog_safety_guard.validate_target_file_path(r"C:\Users\User\Documents\resume.pdf")
    assert allowed is True

    # Blocked system directories
    blocked_sys, reason_sys = dialog_safety_guard.validate_target_file_path(r"C:\Windows\System32\cmd.exe")
    assert blocked_sys is False
    assert "violates security policy" in reason_sys

    blocked_prog, _ = dialog_safety_guard.validate_target_file_path(r"C:\Program Files\App\binary.dll")
    assert blocked_prog is False

    # Blocked path traversal
    blocked_trav, reason_trav = dialog_safety_guard.validate_target_file_path(r"C:\Users\test\..\..\Windows\cmd.exe")
    assert blocked_trav is False
    assert "traversal" in reason_trav


def test_privacy_filter_redaction():
    """Verify PrivacyFilter redacts credit cards and social security numbers from logs."""
    text_with_cc = "Payment card is 4532 1234 5678 9012 for user"
    redacted = privacy_filter.sanitize_log_text(text_with_cc)
    assert "4532" not in redacted
    assert "[REDACTED_CARD]" in redacted

    text_with_ssn = "User SSN is 000-12-3456 in system"
    redacted_ssn = privacy_filter.sanitize_log_text(text_with_ssn)
    assert "000-12-3456" not in redacted_ssn
    assert "[REDACTED_SSN]" in redacted_ssn


@pytest.mark.asyncio
async def test_emergency_stop_guard_enforcement():
    """Verify DesktopSecurityGuard raises PermissionError when Emergency Stop is activated."""
    controller = get_emergency_stop_controller()

    # Normal state: assert_automation_allowed does not raise if emergency stop is inactive
    if not controller.is_emergency_stop_active:
        desktop_security_guard.assert_automation_allowed()

    # Activate emergency stop
    await controller.activate_emergency_stop(activated_by="test", reason="Security Unit Test Trigger")
    try:
        with pytest.raises(PermissionError, match="Emergency Stop active"):
            desktop_security_guard.assert_automation_allowed()
    finally:
        # Reset emergency stop
        await controller.clear_emergency_stop(cleared_by="test")


def test_desktop_action_request_contracts():
    """Verify DesktopActionRequest validation rules."""
    req = DesktopActionRequest(
        action_type=DesktopActionType.ACTIVATE_WINDOW,
        window_ref="win_100_200",
        timeout_ms=5000,
    )
    assert req.action_type == DesktopActionType.ACTIVATE_WINDOW
    assert req.window_ref == "win_100_200"
    assert req.timeout_ms == 5000
