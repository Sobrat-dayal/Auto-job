"""Unit tests for the deterministic Authorization Engine, Scopes, and Policies (Stage 14)."""

from datetime import UTC, datetime, timedelta
import pytest

from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    AuthorizationRequest,
    GrantDefinition,
    GrantType,
    PolicyDefinition,
    ReasonCode,
    RiskLevel,
)
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.engine import get_authorization_engine
from app.security.authorization.evaluator import (
    classify_action_risk,
    evaluate_grant_match,
    evaluate_policy_rule,
)
from app.security.authorization.scopes import (
    is_safe_filesystem_path,
    is_safe_network_url,
    matches_resource_scope,
)


def test_classify_action_risk():
    """Verify deterministic risk classification across capabilities."""
    assert classify_action_risk("recruitment_match_skills") == RiskLevel.LOW
    assert classify_action_risk("recruitment_draft_resume_bullets") == RiskLevel.MODERATE
    assert classify_action_risk("recruitment_submit_application") == RiskLevel.HIGH
    assert classify_action_risk("fs_delete_file") == RiskLevel.CRITICAL
    assert classify_action_risk("unknown_custom_read") == RiskLevel.LOW
    assert classify_action_risk("unknown_wipe_database") == RiskLevel.CRITICAL


def test_filesystem_path_traversal_defense(tmp_path):
    """Verify canonical path resolution rejects directory traversal escapes."""
    root_dir = tmp_path / "sandbox"
    root_dir.mkdir()
    safe_file = root_dir / "resume.txt"
    safe_file.write_text("safe content")

    # Safe file within root
    assert is_safe_filesystem_path(str(safe_file), str(root_dir)) is True

    # Traversal escape
    traversal_path = str(root_dir / ".." / "outside.txt")
    assert is_safe_filesystem_path(traversal_path, str(root_dir)) is False


def test_network_url_boundary_defense():
    """Verify URL origin matching prevents substring and cross-origin spoofing."""
    allowed_origins = ["https://jobs.indeed.com", "https://*.greenhouse.io"]

    # Valid exact origin
    assert is_safe_network_url("https://jobs.indeed.com/viewjob?id=123", allowed_origins) is True

    # Subdomain wildcard
    assert is_safe_network_url("https://boards.greenhouse.io/corp/jobs/456", allowed_origins) is True

    # Substring attack (attacker-indeed.com)
    assert is_safe_network_url("https://attacker-indeed.com/login", allowed_origins) is False

    # Scheme downgrade (http instead of https)
    assert is_safe_network_url("http://jobs.indeed.com/viewjob", allowed_origins) is False


def test_matches_resource_scope():
    """Verify resource scope criteria matching."""
    policy_scope = {
        "allowed_sources": ["linkedin", "indeed"],
        "excluded_companies": ["Acme Bad Corp", "SpamCo"],
        "min_match_score": 75.0,
    }

    # Compliant request
    valid_req = {"source": "linkedin", "company": "Tech Innovators", "match_score": 85.0}
    assert matches_resource_scope(valid_req, policy_scope) is True

    # Excluded company
    excluded_req = {"source": "linkedin", "company": "Acme Bad Corp International", "match_score": 90.0}
    assert matches_resource_scope(excluded_req, policy_scope) is False

    # Low match score
    low_score_req = {"source": "indeed", "company": "Good Corp", "match_score": 60.0}
    assert matches_resource_scope(low_score_req, policy_scope) is False

    # Unauthorized source
    bad_source_req = {"source": "unknown_board", "company": "Good Corp", "match_score": 95.0}
    assert matches_resource_scope(bad_source_req, policy_scope) is False


def test_evaluate_grant_match():
    """Verify advance authorization grant matching rules."""
    grant = GrantDefinition(
        name="Test Workflow Grant",
        grant_type=GrantType.WORKFLOW_SCOPED,
        subject_type="agent",
        subject_id="job_matching_agent",
        workflow_id="wf_123",
        allowed_capabilities=["recruitment_match_skills"],
        resource_scope={"unrestricted": True},
        valid_from=datetime.now(UTC) - timedelta(minutes=5),
        valid_until=datetime.now(UTC) + timedelta(minutes=30),
    )

    # Valid matching request
    valid_req = AuthorizationRequest(
        actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_123"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
    )
    assert evaluate_grant_match(grant, valid_req) is True

    # Wrong workflow
    wrong_wf_req = AuthorizationRequest(
        actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_999"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
    )
    assert evaluate_grant_match(grant, wrong_wf_req) is False

    # Wrong agent
    wrong_agent_req = AuthorizationRequest(
        actor=ActorContext(agent_id="resume_agent", workflow_id="wf_123"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
    )
    assert evaluate_grant_match(grant, wrong_agent_req) is False


@pytest.mark.asyncio
async def test_authorization_engine_evaluations():
    """Verify end-to-end evaluation with the AuthorizationEngine singleton."""
    engine = get_authorization_engine()

    # 1. Low-risk read capability -> ALLOW under baseline
    req_read = AuthorizationRequest(
        actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_test"),
        capability_id="recruitment_match_skills",
        action="recruitment_match_skills",
        parameters={"candidate_skills": ["python"], "job_requirements": ["python"]},
    )
    dec_read = await engine.evaluate(req_read)
    assert dec_read.outcome == ActionEffect.ALLOW
    assert dec_read.reason_code in (ReasonCode.EXPLICIT_ALLOW_POLICY, ReasonCode.READ_ONLY_BASELINE)

    # 2. High-risk live submission -> REQUIRE_APPROVAL by policy
    req_submit = AuthorizationRequest(
        actor=ActorContext(agent_id="application_agent", workflow_id="wf_test"),
        capability_id="recruitment_submit_application",
        action="recruitment_submit_application",
        parameters={"job_id": "job_123"},
    )
    dec_submit = await engine.evaluate(req_submit)
    assert dec_submit.outcome == ActionEffect.REQUIRE_APPROVAL
    assert dec_submit.reason_code == ReasonCode.APPROVAL_REQUIRED_BY_POLICY

    # 3. Credential extraction by specialist agent -> DENY
    req_cred = AuthorizationRequest(
        actor=ActorContext(agent_id="job_matching_agent", workflow_id="wf_test"),
        capability_id="credential_read_secret",
        action="credential_read_secret",
        parameters={"vault_key": "api_key"},
    )
    dec_cred = await engine.evaluate(req_cred)
    assert dec_cred.outcome == ActionEffect.DENY
    assert dec_cred.reason_code in (ReasonCode.CREDENTIAL_ACCESS_RESTRICTED, ReasonCode.EXPLICIT_DENY_POLICY)
