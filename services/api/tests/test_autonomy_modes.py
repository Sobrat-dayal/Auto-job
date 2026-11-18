"""Unit tests for Section 110 & 112: Autonomy Modes, Standing Grants, and Revocation."""

import pytest
from app.recruitment.policy.autonomy.controller import AutonomyController
from app.recruitment.policy.contracts import AutonomyMode


@pytest.fixture
def autonomy_ctrl() -> AutonomyController:
    return AutonomyController()


def test_autonomy_modes_permissions(autonomy_ctrl: AutonomyController):
    # Mode 1: Research Only
    ok, _ = autonomy_ctrl.validate_action_authorization(AutonomyMode.RESEARCH_ONLY, "discover")
    assert ok is True
    ok, reason = autonomy_ctrl.validate_action_authorization(AutonomyMode.RESEARCH_ONLY, "prepare_resume_draft")
    assert ok is False
    assert "prohibited under Research Only" in reason

    # Mode 2: Prepare and Review
    ok, _ = autonomy_ctrl.validate_action_authorization(AutonomyMode.PREPARE_AND_REVIEW, "prepare_resume_draft")
    assert ok is True
    ok, reason = autonomy_ctrl.validate_action_authorization(AutonomyMode.PREPARE_AND_REVIEW, "submit_application")
    assert ok is False
    assert "Direct autonomous submission prohibited" in reason

    # Mode 3: Preauthorized Preparation
    ok, _ = autonomy_ctrl.validate_action_authorization(AutonomyMode.PREAUTHORIZED_PREPARATION, "prepare_answer_draft")
    assert ok is True
    ok, _ = autonomy_ctrl.validate_action_authorization(AutonomyMode.PREAUTHORIZED_PREPARATION, "submit_application")
    assert ok is False


def test_standing_grant_revocation(autonomy_ctrl: AutonomyController):
    # 1. Create standing grant
    grant = autonomy_ctrl.create_grant(
        grantee_agent="application_agent",
        action_type="recruitment.application.prepare",
        target_employers=["Stripe", "GitHub"],
        max_operations=10,
    )
    assert grant.is_revoked is False

    # 2. Validate action with valid grant under Mode 4
    ok, msg = autonomy_ctrl.validate_action_authorization(
        mode=AutonomyMode.BOUNDED_AUTONOMOUS_APPLICATIONS,
        action="prepare_application",
        grant_id=grant.id,
        employer="Stripe",
    )
    assert ok is True
    assert "Action authorized under standing grant" in msg

    # 3. Revoke grant
    revoked = autonomy_ctrl.revoke_grant(grant.id)
    assert revoked is True

    # 4. Action must now be strictly denied
    ok_after, msg_after = autonomy_ctrl.validate_action_authorization(
        mode=AutonomyMode.BOUNDED_AUTONOMOUS_APPLICATIONS,
        action="prepare_application",
        grant_id=grant.id,
        employer="Stripe",
    )
    assert ok_after is False
    assert "has been revoked" in msg_after
