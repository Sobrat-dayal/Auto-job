"""Unit tests for Section 115: Recruitment Agent Policy Integration and Snapshot Generation."""

import pytest
from app.recruitment.policy.contracts import (
    JobOpportunityContext,
    PolicyDecisionOutcome,
    WorkArrangement,
)
from app.recruitment.policy.service import recruitment_policy_service


@pytest.mark.asyncio
async def test_agent_policy_snapshot_and_evaluation():
    adapter = recruitment_policy_service.agent_adapter

    # 1. Inspect agent policy snapshot
    snapshot = adapter.get_agent_policy_snapshot()
    assert "active_strategy" in snapshot
    assert snapshot["active_strategy"]["title"] == "Backend & Distributed Systems Focus"
    assert snapshot["remaining_daily_budget"] > 0
    assert "target_roles" in snapshot["active_strategy"]

    # 2. Check action permissions for agent
    ok, _ = adapter.check_action_permission(agent_role="application_agent", action="prepare_resume_draft")
    assert ok is True

    # 3. Direct autonomous submission prohibited without specific Mode 4 grant
    ok_submit, msg_submit = adapter.check_action_permission(agent_role="application_agent", action="submit_application")
    assert ok_submit is False
    assert "prohibited" in msg_submit

    # 4. Evaluate job opportunity via agent adapter
    job = JobOpportunityContext(
        id="job_agent_01",
        title="Backend Software Engineer",
        employer_name="Stripe",
        work_arrangement=WorkArrangement.REMOTE,
    )
    decision = await adapter.evaluate_job_for_agents(job)
    assert decision.job_title == "Backend Software Engineer"
    assert decision.decision in (PolicyDecisionOutcome.PROCEED, PolicyDecisionOutcome.NEEDS_REVIEW)
