"""Supervisor Agent providing master coordination over multi-agent workflows."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any
import uuid

from app.db.engine import get_db_session
from app.orchestration.context import WorkflowContext
from app.orchestration.contracts import (
    PriorityLevel,
    StepStatus,
    WorkflowCreateRequest,
    WorkflowPlan,
    WorkflowReplanRequest,
    WorkflowResponse,
    WorkflowStatus,
    WorkflowStepDefinition,
    WorkflowStepResponse,
    WorkflowSummary,
)
from app.orchestration.planner import PlanningAgent
from app.orchestration.recovery import RecoveryAgent
from app.orchestration.router import TaskRouterAgent
from app.orchestration.scheduler import ExecutionScheduler
from app.orchestration.verifier import VerificationAgent
from app.repositories.workflow_repository import WorkflowRepository

logger = logging.getLogger("autonom.orchestration.supervisor")


class SupervisorAgent:
    """Master workflow coordinator managing lifecycle transitions, planning, and execution runs."""

    def __init__(self) -> None:
        self.planner = PlanningAgent()
        self.router = TaskRouterAgent()
        self.verifier = VerificationAgent()
        self.recovery = RecoveryAgent()
        self.scheduler = ExecutionScheduler(
            router=self.router,
            verifier=self.verifier,
            recovery=self.recovery,
        )

        # Active workflow runtime controllers: workflow_id -> control events
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._pause_events: dict[str, asyncio.Event] = {}
        self._active_tasks: dict[str, asyncio.Task] = {}

    async def create_workflow(self, request: WorkflowCreateRequest) -> WorkflowResponse:
        """Create a new workflow record and generate initial plan."""
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
        title = request.title or (request.goal[:60] + ("..." if len(request.goal) > 60 else ""))

        initial_context = {
            "inputs": {
                "goal": request.goal,
                **request.constraints,
            }
        }
        if "job_description" in request.constraints:
            initial_context["inputs"]["job_description"] = request.constraints["job_description"]
        elif "text" in request.constraints:
            initial_context["inputs"]["text"] = request.constraints["text"]
            initial_context["inputs"]["job_description"] = request.constraints["text"]

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.create_workflow(
                workflow_id=workflow_id,
                title=title,
                goal=request.goal,
                priority=request.priority.value,
                context_json=initial_context,
                constraints_json=request.constraints,
            )
            await repo.update_workflow_status(workflow_id, WorkflowStatus.PLANNING.value)

        # Generate plan automatically upon creation
        plan = await self.planner.create_plan(
            workflow_id=workflow_id,
            goal=request.goal,
            constraints=request.constraints,
            priority=request.priority,
            version=1,
        )

        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        raw_steps = [s.model_dump() for s in plan.steps]

        dependencies_pairs: list[tuple[str, str]] = []
        for s in plan.steps:
            for dep in s.dependencies:
                dependencies_pairs.append((s.step_id, dep))

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.save_plan(
                plan_id=plan_id,
                workflow_id=workflow_id,
                version=plan.version,
                goal=plan.goal,
                plan_json={"steps": raw_steps, "goal": plan.goal, "version": plan.version},
                success_criteria_json=plan.success_criteria,
            )
            await repo.save_steps(
                workflow_id=workflow_id,
                plan_id=plan_id,
                steps=raw_steps,
            )
            if dependencies_pairs:
                await repo.save_dependencies(
                    workflow_id=workflow_id,
                    dependencies=dependencies_pairs,
                )
            await repo.update_workflow_metrics(
                workflow_id=workflow_id,
                total_steps=len(plan.steps),
            )
            await repo.update_workflow_status(
                workflow_id,
                WorkflowStatus.PLAN_READY.value,
                active_plan_id=plan_id,
            )

        return await self.get_workflow_status(workflow_id)

    async def start_workflow(self, workflow_id: str, background: bool = True) -> WorkflowResponse:
        """Start executing a planned workflow."""
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            workflow = await repo.get_workflow(workflow_id)
            if not workflow:
                raise KeyError(f"Workflow '{workflow_id}' not found")

            active_plan_record = await repo.get_active_plan(workflow_id)
            if not active_plan_record:
                raise ValueError(f"Workflow '{workflow_id}' has no active plan to execute")

            raw_plan_json = active_plan_record.plan_json or {}
            steps_data = raw_plan_json.get("steps", [])
            steps_objs = [WorkflowStepDefinition(**s) for s in steps_data]

            plan = WorkflowPlan(
                workflow_id=workflow_id,
                version=active_plan_record.version,
                goal=active_plan_record.goal,
                steps=steps_objs,
                success_criteria=active_plan_record.success_criteria_json or [],
                max_parallel_steps=4,
            )
            plan_id = active_plan_record.id
            raw_context = workflow.context_json or {}

            await repo.update_workflow_status(
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING.value,
                started_at=datetime.now(UTC),
            )

        cancel_ev = asyncio.Event()
        pause_ev = asyncio.Event()
        self._cancel_events[workflow_id] = cancel_ev
        self._pause_events[workflow_id] = pause_ev

        inputs = raw_context.get("inputs", {})
        context = WorkflowContext(workflow_id=workflow_id, initial_inputs=inputs)

        async def _run() -> None:
            try:
                success = await self.scheduler.execute_plan(
                    workflow_id=workflow_id,
                    plan_id=plan_id,
                    plan=plan,
                    context=context,
                    cancel_event=cancel_ev,
                    pause_event=pause_ev,
                )
                final_status = WorkflowStatus.COMPLETED if success else WorkflowStatus.FAILED
                if cancel_ev.is_set():
                    final_status = WorkflowStatus.CANCELLED
            except Exception as exc:
                logger.error("Workflow '%s' execution crashed: %s", workflow_id, exc)
                final_status = WorkflowStatus.FAILED
            finally:
                async with get_db_session() as session:
                    repo = WorkflowRepository(session)
                    steps = await repo.get_steps(workflow_id, plan_id)
                    completed = sum(1 for s in steps if s.status == "completed")
                    failed = sum(1 for s in steps if s.status == "failed")
                    await repo.update_workflow_metrics(
                        workflow_id=workflow_id,
                        completed_steps=completed,
                        failed_steps=failed,
                        context_updates=context.to_dict(),
                    )
                    await repo.update_workflow_status(
                        workflow_id=workflow_id,
                        status=final_status.value,
                        completed_at=datetime.now(UTC),
                    )
                    # Record workflow episodic experience in memory
                    try:
                        from app.memory.integrations.supervisor import supervisor_memory
                        wf_model = await repo.get_workflow(workflow_id)
                        goal_text = wf_model.goal if wf_model else "Unknown workflow"
                        await supervisor_memory.record_workflow_experience(
                            workflow_id=workflow_id,
                            goal=goal_text,
                            success=(final_status == WorkflowStatus.COMPLETED),
                            lessons=f"Completed {completed} steps, failed {failed} steps.",
                        )
                    except Exception as mem_exc:
                        logger.debug("Failed recording workflow experience to memory: %s", mem_exc)
                self._active_tasks.pop(workflow_id, None)

        task = asyncio.create_task(_run())
        self._active_tasks[workflow_id] = task

        if not background:
            await task

        return await self.get_workflow_status(workflow_id)

    async def pause_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Pause a running workflow."""
        if workflow_id in self._pause_events:
            self._pause_events[workflow_id].set()
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.update_workflow_status(workflow_id, WorkflowStatus.PAUSED.value)
        return await self.get_workflow_status(workflow_id)

    async def resume_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Resume a paused workflow."""
        if workflow_id in self._pause_events:
            self._pause_events[workflow_id].clear()
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.update_workflow_status(workflow_id, WorkflowStatus.RUNNING.value)
        return await self.get_workflow_status(workflow_id)

    async def cancel_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Cancel a running, queued, or planned workflow."""
        if workflow_id in self._cancel_events:
            self._cancel_events[workflow_id].set()
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.update_workflow_status(
                workflow_id=workflow_id,
                status=WorkflowStatus.CANCELLED.value,
                completed_at=datetime.now(UTC),
            )
        return await self.get_workflow_status(workflow_id)

    async def replan_workflow(self, workflow_id: str, request: WorkflowReplanRequest) -> WorkflowResponse:
        """Dynamically revise an existing workflow plan."""
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            workflow = await repo.get_workflow(workflow_id)
            if not workflow:
                raise KeyError(f"Workflow '{workflow_id}' not found")

            active_plan_record = await repo.get_active_plan(workflow_id)
            next_version = (active_plan_record.version + 1) if active_plan_record else 2

            await repo.update_workflow_status(workflow_id, WorkflowStatus.PLANNING.value)

        new_plan = await self.planner.create_plan(
            workflow_id=workflow_id,
            goal=workflow.goal,
            constraints={**(workflow.constraints_json or {}), **request.additional_constraints, "replan_reason": request.reason},
            priority=PriorityLevel(workflow.priority),
            version=next_version,
        )

        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        raw_steps = [s.model_dump() for s in new_plan.steps]
        dependencies_pairs = [
            (s.step_id, dep) for s in new_plan.steps for dep in s.dependencies
        ]

        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            await repo.save_plan(
                plan_id=plan_id,
                workflow_id=workflow_id,
                version=new_plan.version,
                goal=new_plan.goal,
                plan_json={"steps": raw_steps, "goal": new_plan.goal, "version": new_plan.version},
                success_criteria_json=new_plan.success_criteria,
            )
            await repo.save_steps(
                workflow_id=workflow_id,
                plan_id=plan_id,
                steps=raw_steps,
            )
            if dependencies_pairs:
                await repo.save_dependencies(
                    workflow_id=workflow_id,
                    dependencies=dependencies_pairs,
                )
            await repo.update_workflow_metrics(
                workflow_id=workflow_id,
                total_steps=len(new_plan.steps),
            )
            await repo.update_workflow_status(
                workflow_id,
                WorkflowStatus.PLAN_READY.value,
                active_plan_id=plan_id,
            )

        return await self.get_workflow_status(workflow_id)

    async def get_workflow_status(self, workflow_id: str) -> WorkflowResponse:
        """Retrieve comprehensive workflow status with plan and step details."""
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            rec = await repo.get_workflow(workflow_id)
            if not rec:
                raise KeyError(f"Workflow '{workflow_id}' not found")

            plan_rec = await repo.get_active_plan(workflow_id)
            steps_recs = await repo.get_steps(workflow_id)
            deps = await repo.get_dependencies(workflow_id)

            dep_map: dict[str, list[str]] = {}
            for s_id, dep_id in deps:
                dep_map.setdefault(s_id, []).append(dep_id)

            steps_responses = [
                WorkflowStepResponse(
                    id=s.id,
                    workflow_id=s.workflow_id,
                    plan_id=s.plan_id,
                    step_id=s.step_id,
                    title=s.title,
                    description=s.description or "",
                    capability_id=s.capability_id,
                    assigned_agent_id=s.assigned_agent_id,
                    status=StepStatus(s.status),
                    dependencies=dep_map.get(s.step_id, []),
                    input_bindings=s.input_bindings_json or {},
                    output_result=s.output_result_json,
                    error_info=s.error_info_json,
                    verification_status=s.verification_status,
                    retry_count=s.retry_count,
                    max_retries=s.max_retries,
                    timeout_seconds=s.timeout_seconds,
                    started_at=s.started_at,
                    completed_at=s.completed_at,
                    created_at=s.created_at,
                )
                for s in steps_recs
            ]

            active_plan = None
            if plan_rec:
                raw_plan = plan_rec.plan_json or {}
                raw_steps = raw_plan.get("steps", [])
                active_plan = WorkflowPlan(
                    workflow_id=workflow_id,
                    version=plan_rec.version,
                    goal=plan_rec.goal,
                    steps=[WorkflowStepDefinition(**s) for s in raw_steps],
                    success_criteria=plan_rec.success_criteria_json or [],
                    max_parallel_steps=4,
                )

            return WorkflowResponse(
                id=rec.id,
                title=rec.title,
                goal=rec.goal,
                status=WorkflowStatus(rec.status),
                priority=PriorityLevel(rec.priority),
                active_plan_id=rec.active_plan_id,
                active_plan=active_plan,
                steps=steps_responses,
                context=rec.context_json or {},
                constraints=rec.constraints_json or {},
                total_steps=rec.total_steps,
                completed_steps=rec.completed_steps,
                failed_steps=rec.failed_steps,
                total_cost_usd=rec.total_cost_usd,
                total_tokens=rec.total_tokens,
                error_message=rec.error_message,
                created_at=rec.created_at,
                started_at=rec.started_at,
                completed_at=rec.completed_at,
                updated_at=rec.updated_at,
            )

    async def list_workflows(
        self,
        status: WorkflowStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkflowSummary]:
        """List workflows with summaries."""
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            records, _ = await repo.list_workflows(
                status=status.value if status else None,
                limit=limit,
                offset=offset,
            )
            return [
                WorkflowSummary(
                    id=r.id,
                    title=r.title,
                    goal=r.goal,
                    status=WorkflowStatus(r.status),
                    priority=PriorityLevel(r.priority),
                    total_steps=r.total_steps,
                    completed_steps=r.completed_steps,
                    failed_steps=r.failed_steps,
                    total_cost_usd=r.total_cost_usd,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
                for r in records
            ]

    async def reconcile_active_workflows(self) -> int:
        """Reconcile orphaned in-flight workflows after backend restart."""
        async with get_db_session() as session:
            repo = WorkflowRepository(session)
            reconciled = await repo.reconcile_active_workflows()
            count = len(reconciled)
            if count > 0:
                logger.warning("Reconciled %d orphaned active workflows on supervisor startup", count)
            return count


# Global singleton instance
_supervisor_instance: SupervisorAgent | None = None


def get_supervisor_agent() -> SupervisorAgent:
    """Return shared SupervisorAgent singleton."""
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = SupervisorAgent()
    return _supervisor_instance
