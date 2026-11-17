"""Tests for Emergency Stop and Automation Pause (Stage 14)."""

import pytest

from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    AuthorizationRequest,
    ReasonCode,
)
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.engine import (
    AuthorizationDeniedError,
    get_authorization_engine,
)
from app.security.enforcement.gateway import get_tool_execution_gateway


@pytest.mark.asyncio
async def test_emergency_stop_activation_and_blocking():
    """Verify emergency stop blocks all operations at engine and gateway boundaries."""
    controller = get_emergency_stop_controller()
    engine = get_authorization_engine()
    gateway = get_tool_execution_gateway()

    # Ensure clean starting state
    await controller.clear_emergency_stop()
    assert controller.is_emergency_stop_active is False

    req = AuthorizationRequest(
        actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_emg_test"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
        parameters={"skills": ["python"]},
    )

    # 1. Normal state: action allowed
    dec1 = await engine.evaluate(req)
    assert dec1.outcome == ActionEffect.ALLOW

    # 2. Activate emergency stop
    state = await controller.activate_emergency_stop(activated_by="admin", reason="Test panic trigger")
    assert state.is_emergency_stop_active is True
    assert controller.is_emergency_stop_active is True

    # 3. Engine evaluation returns DENY with EMERGENCY_STOP_ACTIVE
    dec2 = await engine.evaluate(req)
    assert dec2.outcome == ActionEffect.DENY
    assert dec2.reason_code == ReasonCode.EMERGENCY_STOP_ACTIVE

    # 4. Gateway execution raises AuthorizationDeniedError
    with pytest.raises(AuthorizationDeniedError) as exc_info:
        await gateway.execute_capability(
            capability_id="recruitment_match_skills",
            parameters={"skills": ["python"]},
            actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_emg_test"),
        )
    assert exc_info.value.decision.reason_code == ReasonCode.EMERGENCY_STOP_ACTIVE

    # 5. Clear emergency stop
    cleared_state = await controller.clear_emergency_stop(cleared_by="admin")
    assert cleared_state.is_emergency_stop_active is False
    assert controller.is_emergency_stop_active is False

    # 6. Operation permitted again
    dec3 = await engine.evaluate(req)
    assert dec3.outcome == ActionEffect.ALLOW


@pytest.mark.asyncio
async def test_automation_pause_and_resume():
    """Verify pause blocks autonomous background execution while permitting user-directed requests."""
    controller = get_emergency_stop_controller()
    engine = get_authorization_engine()

    await controller.clear_emergency_stop()
    await controller.resume_automation()

    # Autonomous agent request
    agent_req = AuthorizationRequest(
        actor=ActorContext(actor_type="agent", agent_id="job_matching_agent", workflow_id="wf_pause_test"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
    )

    # Direct user request
    user_req = AuthorizationRequest(
        actor=ActorContext(actor_type="user", actor_id="operator", workflow_id="wf_pause_test"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
    )

    # 1. Pause automation
    await controller.pause_automation(paused_by="operator", reason="Scheduled maintenance")
    assert controller.is_automation_paused is True

    # 2. Agent request is blocked with AUTOMATION_PAUSED
    dec_agent = await engine.evaluate(agent_req)
    assert dec_agent.outcome == ActionEffect.DENY
    assert dec_agent.reason_code == ReasonCode.AUTOMATION_PAUSED

    # 3. Direct user request is permitted
    dec_user = await engine.evaluate(user_req)
    assert dec_user.outcome == ActionEffect.ALLOW

    # 4. Resume automation
    await controller.resume_automation(resumed_by="operator")
    assert controller.is_automation_paused is False

    # 5. Agent request is permitted again
    dec_resumed = await engine.evaluate(agent_req)
    assert dec_resumed.outcome == ActionEffect.ALLOW
