"""Tests for Approval Request Management, Deduplication, Replay Protection, and Consumption (Stage 14)."""

import uuid
import pytest

from app.security.authorization.approvals import get_approval_manager
from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    ApprovalMode,
    ApprovalStatus,
    AuthorizationRequest,
    ReasonCode,
    RiskLevel,
)
from app.security.authorization.engine import get_authorization_engine


@pytest.mark.asyncio
async def test_approval_lifecycle_and_replay_protection():
    """Verify approval creation, deduplication, resolution, and single-use consumption."""
    manager = get_approval_manager()
    engine = get_authorization_engine()
    wf_id = f"wf_appr_{uuid.uuid4().hex[:8]}"

    auth_req = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent", workflow_id=wf_id, step_id="step_sub"),
        capability_id="recruitment_submit_application",
        action="recruitment_submit_application",
        parameters={"job_id": f"job_{uuid.uuid4().hex[:6]}", "candidate_name": "Test Candidate"},
    )

    # 1. Create approval request
    appr1 = await manager.create_or_get_request(
        auth_request=auth_req,
        risk_level=RiskLevel.HIGH,
        reason="Requires user confirmation before sending application",
        approval_mode=ApprovalMode.ONE_TIME,
    )
    assert appr1.id.startswith("appr_")
    assert appr1.status == ApprovalStatus.PENDING

    # 2. Deduplication check: submitting identical request returns the exact same approval ID
    appr2 = await manager.create_or_get_request(
        auth_request=auth_req,
        risk_level=RiskLevel.HIGH,
        reason="Duplicate check",
    )
    assert appr2.id == appr1.id

    # 3. List pending approvals
    pending = await manager.list_requests(status="pending")
    assert any(p.id == appr1.id for p in pending)

    # 4. Before approval: engine evaluation returns REQUIRE_APPROVAL
    decision_before = await engine.evaluate(auth_req)
    assert decision_before.outcome == ActionEffect.REQUIRE_APPROVAL

    # 5. Approve the request
    resolved = await manager.resolve_request(
        approval_id=appr1.id,
        decision="approve",
        decided_by="test_user",
        reason="Approved by user in test",
        approval_mode=ApprovalMode.ONE_TIME,
    )
    assert resolved.status == ApprovalStatus.APPROVED

    # 6. Now engine evaluation returns ALLOW due to approved status
    decision_after = await engine.evaluate(auth_req)
    assert decision_after.outcome == ActionEffect.ALLOW
    assert decision_after.reason_code == ReasonCode.APPROVAL_GRANTED

    # 7. Consume approval (simulating execution completion)
    await manager.consume_request(appr1.id)
    consumed_req = await manager.get_request(appr1.id)
    assert consumed_req.status == ApprovalStatus.CONSUMED

    # 8. Replay attack check: once consumed, engine evaluation requires approval again
    decision_replayed = await engine.evaluate(auth_req)
    assert decision_replayed.outcome == ActionEffect.REQUIRE_APPROVAL


@pytest.mark.asyncio
async def test_approval_denial_flow():
    """Verify explicit denial of an approval request."""
    manager = get_approval_manager()

    auth_req = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent", workflow_id="wf_deny_test"),
        capability_id="recruitment_submit_application",
        action="recruitment_submit_application",
        parameters={"job_id": "job_rejected"},
    )

    req = await manager.create_or_get_request(
        auth_request=auth_req,
        risk_level=RiskLevel.HIGH,
        reason="Test rejection",
    )
    assert req.status == ApprovalStatus.PENDING

    denied = await manager.resolve_request(
        approval_id=req.id,
        decision="deny",
        decided_by="test_user",
        reason="Job is unsuitable",
    )
    assert denied.status == ApprovalStatus.DENIED
