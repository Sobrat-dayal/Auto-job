"""Integration test for full authorization cycle during workflow execution (Stage 14)."""

from typing import Any
import uuid
import pytest

from app.db.engine import get_db_session
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.context import WorkflowContext
from app.orchestration.contracts import (
    PriorityLevel,
    StepStatus,
    VerificationPolicy,
    WorkflowPlan,
    WorkflowStatus,
    WorkflowStepDefinition,
)
from app.orchestration.scheduler import ExecutionScheduler
from app.repositories.workflow_repository import WorkflowRepository
from app.security.authorization.approvals import get_approval_manager
from app.security.authorization.contracts import ApprovalMode, ApprovalStatus


class MockSubmitApplicationCapability(BaseCapability):
    capability_id = "recruitment_submit_application"
    name = "Submit Application"
    version = "1.0.0"
    description = "Mock application submission capability"
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.DETERMINISTIC_ASSERTION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object"}

    @property
    def output_schema(self) -> dict[str, Any]:
        return {"type": "object"}

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"status": "submitted", "confirmation_number": "CONF-12345"}


@pytest.mark.asyncio
async def test_workflow_authorization_lifecycle_pause_and_resume():
    """Verify that a high-risk step transitions workflow to WAITING_FOR_AUTHORIZATION,

    creates an approval request, and once approved, resumes execution to completion.
    """
    cap_registry = get_capability_registry()
    cap_registry.register(MockSubmitApplicationCapability())

    scheduler = ExecutionScheduler()
    approval_manager = get_approval_manager()

    wf_id = f"wf_auth_cycle_{uuid.uuid4().hex[:8]}"
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"

    # Step 1: Low-risk data transform (deterministic analytical, pre-approved by baseline)
    step1 = WorkflowStepDefinition(
        step_id="step_low",
        title="Transform Candidate Data",
        description="Filter and format candidate parameters",
        capability_id="data_transform",
        dependencies=[],
        input_bindings={"data": {"candidate": "Test Candidate"}, "operation": "flatten"},
        verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
        priority=PriorityLevel.NORMAL,
    )

    # Step 2: High-risk application submission (requires approval per system policy)
    step2 = WorkflowStepDefinition(
        step_id="step_high",
        title="Submit Job Application",
        description="Submit finalized application to ATS",
        capability_id="recruitment_submit_application",
        dependencies=["step_low"],
        input_bindings={"job_id": "job_101", "candidate_name": "Test Candidate"},
        verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
        priority=PriorityLevel.HIGH,
    )

    plan = WorkflowPlan(
        workflow_id=wf_id,
        goal="Discover and submit application",
        version=1,
        steps=[step1, step2],
        success_criteria=["data transformed", "application submitted"],
    )

    raw_steps = [s.model_dump() for s in plan.steps]

    # Persist workflow and plan in DB
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        await repo.create_workflow(
            workflow_id=wf_id,
            title="Job Application Pipeline",
            goal=plan.goal,
            priority="high",
        )
        await repo.save_plan(
            plan_id=plan_id,
            workflow_id=wf_id,
            version=plan.version,
            goal=plan.goal,
            plan_json={"steps": raw_steps, "goal": plan.goal, "version": plan.version},
            success_criteria_json=plan.success_criteria,
        )
        await repo.save_steps(
            workflow_id=wf_id,
            plan_id=plan_id,
            steps=raw_steps,
        )
        await repo.save_dependencies(
            workflow_id=wf_id,
            dependencies=[("step_high", "step_low")],
        )
        await repo.update_workflow_status(
            workflow_id=wf_id,
            status=WorkflowStatus.RUNNING.value,
            active_plan_id=plan_id,
        )

    context = WorkflowContext(workflow_id=wf_id)

    # First execution pass: step1 finishes, step2 triggers authorization pause
    success_first = await scheduler.execute_plan(
        workflow_id=wf_id,
        plan_id=plan_id,
        plan=plan,
        context=context,
    )
    assert success_first is False

    # Verify workflow status transitioned to WAITING_FOR_AUTHORIZATION in DB
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        wf_rec = await repo.get_workflow(wf_id)
        assert wf_rec is not None
        assert wf_rec.status == WorkflowStatus.WAITING_FOR_AUTHORIZATION.value

        step_records = await repo.get_steps(wf_id)
        step_map = {s.step_id: s for s in step_records}
        assert step_map["step_low"].status == StepStatus.COMPLETED.value
        assert step_map["step_high"].status == StepStatus.PAUSED.value

    # Verify approval request was generated
    pending = await approval_manager.list_requests(status="pending", workflow_id=wf_id)
    assert len(pending) >= 1
    appr = pending[0]
    assert appr.workflow_id == wf_id
    assert appr.capability_id == "recruitment_submit_application"

    # User approves the request
    resolved = await approval_manager.resolve_request(
        approval_id=appr.id,
        decision="approve",
        decided_by="user_admin",
        reason="Approved for testing",
        approval_mode=ApprovalMode.ONE_TIME,
    )
    assert resolved.status == ApprovalStatus.APPROVED

    # Resume workflow execution
    success_resumed = await scheduler.execute_plan(
        workflow_id=wf_id,
        plan_id=plan_id,
        plan=plan,
        context=context,
    )
    assert success_resumed is True

    # Verify final completion in DB
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        step_records = await repo.get_steps(wf_id)
        step_map = {s.step_id: s for s in step_records}
        assert step_map["step_high"].status == StepStatus.COMPLETED.value
