"""Workflow Execution Scheduler executing steps according to DAG dependencies and hardware limits."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any
import uuid

from app.db.engine import get_db_session
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.context import WorkflowContext
from app.orchestration.contracts import (
    FailureCategory,
    MessageType,
    StepStatus,
    VerificationStatus,
    WorkflowPlan,
    WorkflowStepDefinition,
)
from app.orchestration.graph import DependencyGraph
from app.orchestration.recovery import RecoveryAgent
from app.orchestration.router import TaskRouterAgent
from app.orchestration.verifier import VerificationAgent
from app.repositories.workflow_repository import WorkflowRepository

logger = logging.getLogger("autonom.orchestration.scheduler")


class ExecutionScheduler:
    """Coordinates execution of workflow steps respecting DAG order and hardware concurrency limits."""

    def __init__(
        self,
        router: TaskRouterAgent | None = None,
        verifier: VerificationAgent | None = None,
        recovery: RecoveryAgent | None = None,
    ) -> None:
        self.router = router or TaskRouterAgent()
        self.verifier = verifier or VerificationAgent()
        self.recovery = recovery or RecoveryAgent()
        self.capability_registry = get_capability_registry()
        self.agent_registry = get_agent_registry()

        # RTX 4050 6GB Guardrail: At most 1 active LLM operation simultaneously
        self._llm_semaphore = asyncio.Semaphore(1)
        # Deterministic parallel tasks can run up to 4 concurrently
        self._parallel_semaphore = asyncio.Semaphore(4)

    async def execute_plan(
        self,
        workflow_id: str,
        plan_id: str,
        plan: WorkflowPlan,
        context: WorkflowContext,
        cancel_event: asyncio.Event | None = None,
        pause_event: asyncio.Event | None = None,
    ) -> bool:
        """Execute a full workflow plan to completion or terminal failure."""
        graph = DependencyGraph(plan.steps)
        step_definitions: dict[str, WorkflowStepDefinition] = {s.step_id: s for s in plan.steps}

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            step_records = await repo.get_steps(workflow_id)
            step_statuses: dict[str, StepStatus] = {
                s.step_id: StepStatus(s.status) for s in step_records
            }

        for s in plan.steps:
            if s.step_id not in step_statuses:
                step_statuses[s.step_id] = StepStatus.PENDING

        logger.info(
            "Scheduler starting execution for workflow '%s' with %d steps across stages: %s",
            workflow_id,
            len(plan.steps),
            graph.compute_parallel_stages(),
        )

        while True:
            # Check for cancellation
            if cancel_event and cancel_event.is_set():
                logger.info("Workflow '%s' received cancellation signal.", workflow_id)
                async with get_db_session() as session:
                    repo = WorkflowRepository(session)
                    for sid, stat in step_statuses.items():
                        if not stat.is_terminal:
                            step_statuses[sid] = StepStatus.CANCELLED
                            await repo.update_step_status(
                                workflow_id=workflow_id,
                                step_id=sid,
                                status=StepStatus.CANCELLED.value,
                            )
                return False

            # Check for pause
            if pause_event and pause_event.is_set():
                logger.info("Workflow '%s' is paused, waiting for resume...", workflow_id)
                while pause_event.is_set():
                    await asyncio.sleep(0.5)

            # Check if all steps terminal
            all_terminal = all(stat.is_terminal for stat in step_statuses.values())
            if all_terminal:
                all_succeeded = all(stat == StepStatus.COMPLETED for stat in step_statuses.values())
                logger.info(
                    "Workflow '%s' execution finished. All succeeded: %s",
                    workflow_id,
                    all_succeeded,
                )
                return all_succeeded

            executable_step_ids = graph.get_executable_steps(step_statuses)

            if not executable_step_ids:
                has_running = any(stat == StepStatus.RUNNING for stat in step_statuses.values())
                if has_running:
                    await asyncio.sleep(0.2)
                    continue

                logger.warning("No executable steps remain and no steps running in workflow '%s'", workflow_id)
                async with get_db_session() as session:
                    repo = WorkflowRepository(session)
                    for sid, stat in step_statuses.items():
                        if not stat.is_terminal:
                            step_statuses[sid] = StepStatus.BLOCKED
                            await repo.update_step_status(
                                workflow_id=workflow_id,
                                step_id=sid,
                                status=StepStatus.BLOCKED.value,
                                error_info_json={"reason": "Blocked by failed or incomplete dependencies"},
                            )
                return False

            tasks = [
                self._execute_single_step(
                    workflow_id=workflow_id,
                    plan_id=plan_id,
                    step=step_definitions[sid],
                    context=context,
                    step_statuses=step_statuses,
                    graph=graph,
                )
                for sid in executable_step_ids
            ]
            await asyncio.gather(*tasks)

        return True

    async def _execute_single_step(
        self,
        workflow_id: str,
        plan_id: str,
        step: WorkflowStepDefinition,
        context: WorkflowContext,
        step_statuses: dict[str, StepStatus],
        graph: DependencyGraph,
    ) -> None:
        """Executes a single step with routing, execution, verification, and recovery."""
        step_id = step.step_id
        step_statuses[step_id] = StepStatus.RUNNING

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.update_step_status(
                workflow_id=workflow_id,
                step_id=step_id,
                status=StepStatus.RUNNING.value,
                started_at=datetime.now(UTC),
            )

        # 1. Routing
        routing = self.router.route_step(step)
        assigned_agent = routing.assigned_agent_id
        self.router.record_start(assigned_agent)

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.record_agent_message(
                message_id=f"msg_{uuid.uuid4().hex[:10]}",
                workflow_id=workflow_id,
                sender_agent_id="router",
                recipient_agent_id=assigned_agent,
                message_type=MessageType.TASK_ASSIGNMENT.value,
                payload_json={"explanation": routing.explanation, "is_fallback": routing.is_fallback},
                step_id=step_id,
            )

        cap_handler = self.capability_registry.get(step.capability_id)
        requires_ai = cap_handler.requires_ai if cap_handler else False

        retry_count = 0
        max_retries = step.max_retries

        while True:
            # 2. Resolve input bindings from context
            resolved_inputs = context.resolve_bindings(step.input_bindings)

            output_result: dict[str, Any] | None = None
            step_error: Exception | str | None = None

            # 3. Execute with semaphore controls
            sem = self._llm_semaphore if requires_ai else self._parallel_semaphore
            start_time = datetime.now(UTC)

            try:
                async with sem:
                    output_result = await self.capability_registry.execute(
                        capability_id=step.capability_id,
                        input_data=resolved_inputs,
                        context=context.to_dict(),
                    )
            except Exception as exc:
                logger.error("Step '%s' execution raised exception: %s", step_id, exc)
                step_error = exc

            end_time = datetime.now(UTC)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # 4. Verify output if execution succeeded
            verification_passed = False
            verification_obj = None

            if output_result is not None and not step_error:
                verification_obj = await self.verifier.verify_step(
                    step=step,
                    output_data=output_result,
                    context=context.to_dict(),
                )
                async with get_db_session() as session:
                    repo = WorkflowRepository(session)
                    await repo.record_verification_result(
                        verification_id=f"ver_{uuid.uuid4().hex[:10]}",
                        workflow_id=workflow_id,
                        step_id=step_id,
                        verification_type=verification_obj.verification_type,
                        status=verification_obj.status.value,
                        passed=verification_obj.passed,
                        evidence_json=verification_obj.evidence,
                        details=verification_obj.details,
                    )
                verification_passed = verification_obj.passed
                if not verification_passed:
                    step_error = f"Verification failed: {verification_obj.details}"

            # 5. Handle Outcome
            if verification_passed and output_result is not None:
                # SUCCESS
                async with get_db_session() as session:
                    repo = WorkflowRepository(session)
                    await repo.record_agent_execution(
                        execution_id=f"exec_{uuid.uuid4().hex[:10]}",
                        agent_id=assigned_agent,
                        workflow_id=workflow_id,
                        step_id=step_id,
                        status="completed",
                        duration_ms=duration_ms,
                    )
                    await repo.update_step_status(
                        workflow_id=workflow_id,
                        step_id=step_id,
                        status=StepStatus.COMPLETED.value,
                        output_result_json=output_result,
                        verification_status=VerificationStatus.PASS.value,
                        completed_at=end_time,
                    )
                    await repo.record_agent_message(
                        message_id=f"msg_{uuid.uuid4().hex[:10]}",
                        workflow_id=workflow_id,
                        sender_agent_id=assigned_agent,
                        recipient_agent_id="supervisor",
                        message_type=MessageType.TASK_RESULT.value,
                        payload_json={"status": "completed", "duration_ms": duration_ms},
                        step_id=step_id,
                    )

                context.set_step_output(step_id, output_result, {"duration_ms": duration_ms})
                step_statuses[step_id] = StepStatus.COMPLETED
                self.router.record_finish(assigned_agent)
                return

            # 6. Failure Recovery Flow
            self.router.record_finish(assigned_agent)
            recovery_decision = self.recovery.decide_recovery_action(
                step=step,
                error=str(step_error or "Unknown failure"),
                current_retry=retry_count,
            )

            async with get_db_session() as session:
                repo = WorkflowRepository(session)
                await repo.record_recovery_attempt(
                    attempt_id=f"rec_{uuid.uuid4().hex[:10]}",
                    workflow_id=workflow_id,
                    step_id=step_id,
                    failure_category=recovery_decision.failure_category.value,
                    recovery_action=recovery_decision.action,
                    attempt_number=retry_count + 1,
                    success=(recovery_decision.action == "retry"),
                    details_json={"reason": recovery_decision.reason},
                )

            if recovery_decision.action == "retry":
                retry_count += 1
                logger.info("Retrying step '%s' (attempt %d/%d)...", step_id, retry_count, max_retries)
                await asyncio.sleep(0.5)
                continue

            # Terminal Failure for this step
            step_statuses[step_id] = StepStatus.FAILED
            async with get_db_session() as session:
                repo = WorkflowRepository(session)
                await repo.record_agent_execution(
                    execution_id=f"exec_{uuid.uuid4().hex[:10]}",
                    agent_id=assigned_agent,
                    workflow_id=workflow_id,
                    step_id=step_id,
                    status="failed",
                    duration_ms=duration_ms,
                )
                await repo.update_step_status(
                    workflow_id=workflow_id,
                    step_id=step_id,
                    status=StepStatus.FAILED.value,
                    error_info_json={"error": str(step_error), "category": recovery_decision.failure_category.value},
                    verification_status=VerificationStatus.FAIL.value,
                    completed_at=end_time,
                )
            logger.error("Step '%s' failed permanently: %s", step_id, recovery_decision.reason)
            return
