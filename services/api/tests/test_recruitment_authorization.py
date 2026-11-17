"""Tests for Bounded Autonomous Recruitment Application Policies (Stage 14)."""

import pytest

from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    AuthorizationRequest,
    GrantDefinition,
    GrantType,
    ReasonCode,
    RiskLevel,
)
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.engine import get_authorization_engine
from app.security.authorization.evaluator import evaluate_grant_match
from app.security.authorization.scopes import matches_resource_scope


def test_recruitment_policy_scope_constraints():
    """Verify recruitment policy constraints: match threshold, sources, company exclusions."""
    recruitment_scope = {
        "allowed_sources": ["linkedin", "greenhouse"],
        "excluded_companies": ["Blacklisted Corp", "SpamRecruiter"],
        "min_match_score": 80.0,
    }

    # 1. Eligible job: match score >= 80, approved source, clean company
    eligible = {
        "source": "greenhouse",
        "company": "Top Tier Tech",
        "match_score": 85.0,
    }
    assert matches_resource_scope(eligible, recruitment_scope) is True

    # 2. Ineligible: score below 80
    low_match = {
        "source": "greenhouse",
        "company": "Top Tier Tech",
        "match_score": 72.0,
    }
    assert matches_resource_scope(low_match, recruitment_scope) is False

    # 3. Excluded company
    blacklisted = {
        "source": "greenhouse",
        "company": "Blacklisted Corp LLC",
        "match_score": 95.0,
    }
    assert matches_resource_scope(blacklisted, recruitment_scope) is False

    # 4. Unauthorized job source
    unauth_source = {
        "source": "random_scraped_site",
        "company": "Top Tier Tech",
        "match_score": 90.0,
    }
    assert matches_resource_scope(unauth_source, recruitment_scope) is False


def test_recruitment_grant_usage_limits():
    """Verify daily submission limits enforced through grant max_uses."""
    daily_grant = GrantDefinition(
        name="Daily Job Application Grant",
        grant_type=GrantType.STANDING,
        subject_id="application_agent",
        allowed_capabilities=["recruitment_submit_application"],
        resource_scope={"unrestricted": True},
        max_uses=5,
        use_count=4,
    )

    req = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent"),
        capability_id="recruitment_submit_application",
        action="recruitment_submit_application",
    )

    # 4/5 used: still active
    assert evaluate_grant_match(daily_grant, req) is True

    # Reach 5/5
    daily_grant.use_count = 5
    assert daily_grant.is_active is False
    assert evaluate_grant_match(daily_grant, req) is False


@pytest.mark.asyncio
async def test_sensitive_screening_question_escalation():
    """Verify that sensitive legal/attestation questions escalate to require human approval."""
    engine = get_authorization_engine()

    # Normal application field classification -> low risk, allowed
    req_normal = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent", workflow_id="wf_rec_test"),
        capability_id="recruitment_classify_application_fields",
        action="recruitment_classify_application_fields",
        parameters={"fields": ["first_name", "email", "phone", "linkedin_url"]},
    )
    dec_normal = await engine.evaluate(req_normal)
    assert dec_normal.outcome == ActionEffect.ALLOW

    # Actual submission -> high risk, requires human approval
    req_submit = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent", workflow_id="wf_rec_test"),
        capability_id="recruitment_submit_application",
        action="recruitment_submit_application",
        parameters={
            "job_id": "job_123",
            "attestations": {
                "work_authorization": "requires_sponsorship",
                "criminal_history": "none",
            },
        },
    )
    dec_submit = await engine.evaluate(req_submit)
    assert dec_submit.outcome == ActionEffect.REQUIRE_APPROVAL
    assert dec_submit.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
