"""Unit tests for Hybrid Security Guards and Authorization Integration."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.hybrid.contracts import (
    HybridActionType,
    InteractionAction,
    InteractionMethod,
    InteractionTarget,
    SurfaceType,
    TargetType,
)
from app.hybrid.errors import EmergencyStopActiveError, FallbackBlockedError
from app.hybrid.security.authorization import HybridAuthorizationBridge
from app.hybrid.security.execution_guard import HybridExecutionGuard
from app.security.authorization.contracts import (
    ActionEffect,
    AuthorizationDecision,
    ReasonCode,
    RiskLevel,
)
from datetime import datetime, timezone


class MockEmergencyController:
    def __init__(self, is_active: bool = False) -> None:
        self.is_emergency_stop_active = is_active

    async def activate_emergency_stop(self, activated_by: str = "", reason: str = "") -> None:
        self.is_emergency_stop_active = True

    async def clear_emergency_stop(self, cleared_by: str = "") -> None:
        self.is_emergency_stop_active = False


@pytest.mark.asyncio
async def test_execution_guard_emergency_stop_blocks_execution() -> None:
    """Verifies that active emergency stop immediately raises EmergencyStopActiveError."""
    ctrl = MockEmergencyController(is_active=True)
    guard = HybridExecutionGuard(emergency_controller=ctrl)

    assert guard.is_emergency_stop_active() is True
    with pytest.raises(EmergencyStopActiveError):
        guard.ensure_execution_allowed()


@pytest.mark.asyncio
async def test_execution_guard_killswitch_activation_and_reset() -> None:
    """Verifies local killswitch activation, state reflection, and deactivation."""
    ctrl = MockEmergencyController(is_active=False)
    guard = HybridExecutionGuard(emergency_controller=ctrl)

    assert guard.is_emergency_stop_active() is False

    await guard.activate_killswitch(reason="Test operator emergency stop")
    assert guard.is_emergency_stop_active() is True
    assert ctrl.is_emergency_stop_active is True

    await guard.deactivate_killswitch()
    assert guard.is_emergency_stop_active() is False
    assert ctrl.is_emergency_stop_active is False


@pytest.mark.asyncio
async def test_authorization_bridge_action_mapping() -> None:
    """Verifies mapping of hybrid actions to Stage 14 permission categories and actions."""
    bridge = HybridAuthorizationBridge(auth_engine=MagicMock())

    cat_dom, act_dom = bridge.get_action_identifier(HybridActionType.CLICK, InteractionMethod.BROWSER_DOM)
    assert cat_dom == "browser"
    assert act_dom == "browser_click"

    cat_uia, act_uia = bridge.get_action_identifier(HybridActionType.CLICK, InteractionMethod.WINDOWS_UIA)
    assert cat_uia == "desktop"
    assert act_uia == "desktop_invoke"

    cat_vis, act_vis = bridge.get_action_identifier(HybridActionType.CLICK, InteractionMethod.VISUAL_GROUNDING)
    assert cat_vis == "desktop"
    assert act_vis == "visual_click"


@pytest.mark.asyncio
async def test_authorization_fallback_blocked_when_policy_denies() -> None:
    """Verifies that fallback candidate requiring unauthorized permission is blocked with FallbackBlockedError."""
    mock_auth_engine = MagicMock()
    # Mock evaluate_authorization returning DENY
    mock_auth_engine.evaluate_authorization = AsyncMock(return_value=AuthorizationDecision(
        decision_id="dec_deny_1",
        outcome=ActionEffect.DENY,
        reason_code=ReasonCode.EXPLICIT_DENY_POLICY,
        explanation="Desktop visual input capture forbidden by organization policy",
        risk_level=RiskLevel.HIGH,
        correlation_id="corr_1",
        timestamp=datetime.now(timezone.utc),
    ))

    bridge = HybridAuthorizationBridge(auth_engine=mock_auth_engine)
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.CLICK,
    )

    with pytest.raises(FallbackBlockedError) as exc_info:
        await bridge.validate_fallback_authorization(
            subject_id="agent_1",
            action=action,
            fallback_method=InteractionMethod.VISUAL_GROUNDING,
        )
    assert "blocked by authorization policy" in str(exc_info.value)
