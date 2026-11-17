"""Tests for specialist agent context isolation, failure recovery, permissions, and concurrency limits (Stage 13)."""

from datetime import UTC, datetime
import uuid
import pytest

from app.db.engine import get_db_session
from app.orchestration.agents.contracts import (
    AgentCategory,
    AgentConfigurationUpdate,
    AgentManifest,
    AgentRequest,
    AvailabilityState,
)
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.agents.specialists.recruitment import ResumeAgent
from app.orchestration.contracts import FailureCategory, VerificationStatus, WorkflowStepDefinition
from app.orchestration.recovery import RecoveryAgent
from app.repositories.workflow_repository import WorkflowRepository


@pytest.mark.asyncio
async def test_context_isolation_credential_rejection():
    """Verify that specialist agents reject inputs containing credentials or raw secrets."""
    reg = get_agent_registry()
    manifest = reg.get_manifest("resume_agent")
    assert manifest is not None
    assert manifest.context_policy.allow_credentials is False

    agent = ResumeAgent(manifest)

    # Attempt to inject credential
    valid, err = agent.validate_input(
        "recruitment_draft_resume_bullets",
        {
            "matched_skills": ["Python"],
            "api_key": "secret_12345",
        },
    )
    assert valid is False
    assert "Context policy violation" in str(err)

    # Attempt execution with password
    req = AgentRequest(
        workflow_id="wf_test_sec",
        step_id="step_1",
        capability_id="recruitment_draft_resume_bullets",
        input_data={"password": "supersecretpassword", "matched_skills": ["Python"]},
    )
    result = await agent.execute(req)
    assert result.status == "failed"
    assert result.error_category == FailureCategory.INVALID_OUTPUT
    assert "Context policy violation" in (result.error_message or "")


@pytest.mark.asyncio
async def test_disabled_agent_behavior():
    """Verify that disabled agents report unavailable and reject execution."""
    reg = get_agent_registry()
    manifest = reg.get_manifest("job_matching_agent")
    assert manifest is not None

    # Temporarily disable
    reg.update_configuration("job_matching_agent", AgentConfigurationUpdate(enabled=False))
    disabled_m = reg.get_manifest("job_matching_agent")
    assert disabled_m.enabled is False
    assert disabled_m.is_available is False

    # Check routing candidates filter it out
    capable = reg.find_agents_for_capability("recruitment_match_skills")
    assert not any(a.agent_id == "job_matching_agent" for a in capable)

    # Re-enable
    reg.update_configuration("job_matching_agent", AgentConfigurationUpdate(enabled=True))
    enabled_m = reg.get_manifest("job_matching_agent")
    assert enabled_m.enabled is True
    assert enabled_m.is_available is True


@pytest.mark.asyncio
async def test_controlled_failure_recovery_and_persistence():
    """Verify controlled failure classification, recovery decision, and database logging."""
    recovery = RecoveryAgent()

    # Classify failure
    mock_step = WorkflowStepDefinition(
        step_id="step_failing",
        title="Failing Step",
        capability_id="recruitment_match_skills",
        max_retries=2,
    )
    decision = recovery.decide_recovery_action(
        step=mock_step,
        error="Verification failed: Schema validation failed on required key 'matched_skills'",
        current_retry=0,
    )
    assert decision.action == "replan"
    assert decision.failure_category == FailureCategory.FAILED_VERIFICATION

    # Log recovery attempt in database
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        wf_id = f"wf_rec_{uuid.uuid4().hex[:8]}"
        wf = await repo.create_workflow(
            workflow_id=wf_id,
            title="Recovery Test Workflow",
            goal="Test recovery mechanism",
        )
        rec = await repo.record_recovery_attempt(
            attempt_id=f"rec_{uuid.uuid4().hex[:8]}",
            workflow_id=wf.id,
            step_id="step_failing",
            failure_category=decision.failure_category.value,
            recovery_action=decision.action,
            attempt_number=1,
            success=True,
            details_json={"reason": decision.reason},
        )
        assert rec is not None

        history = await repo.list_recovery_attempts(wf.id)
        assert len(history) == 1
        assert history[0].failure_category == FailureCategory.FAILED_VERIFICATION.value


@pytest.mark.asyncio
async def test_agent_execution_history_persistence():
    """Verify recording and querying of agent execution telemetry."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        wf_id = f"wf_telemetry_{uuid.uuid4().hex[:8]}"
        # Create test workflow
        wf = await repo.create_workflow(
            workflow_id=wf_id,
            title="Telemetry Test",
            goal="Test agent execution telemetry logging",
        )
        # Record execution for coding_agent
        exec_id = f"exec_{uuid.uuid4().hex[:8]}"
        exec_rec = await repo.record_agent_execution(
            execution_id=exec_id,
            agent_id="coding_agent",
            workflow_id=wf.id,
            step_id="step_code_review",
            status="completed",
            model_used="local:llama-3-8b",
            tokens_used=420,
            cost_usd=0.0,
            duration_ms=850,
        )
        assert exec_rec.id == exec_id

        # Query for coding_agent
        agent_execs = await repo.get_executions_for_agent("coding_agent", limit=10)
        assert any(e.id == exec_id for e in agent_execs)
