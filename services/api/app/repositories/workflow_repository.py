"""Repository for managing multi-agent workflows, plans, steps, DAG dependencies, executions, and verification audits."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    AgentConfigurationRecord,
    AgentExecutionRecord,
    AgentMessageRecord,
    RecoveryAttemptRecord,
    VerificationResultRecord,
    WorkflowDependencyRecord,
    WorkflowPlanRecord,
    WorkflowRecord,
    WorkflowStepRecord,
)


class WorkflowRepository:
    """Async repository for persistent multi-agent workflows and DAG execution states."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_workflow(
        self,
        workflow_id: str,
        title: str,
        goal: str,
        priority: str = "normal",
        context_json: dict[str, Any] | None = None,
        constraints_json: dict[str, Any] | None = None,
    ) -> WorkflowRecord:
        """Creates a new workflow record."""
        record = WorkflowRecord(
            id=workflow_id,
            title=title,
            goal=goal,
            status="created",
            priority=priority,
            context_json=context_json or {},
            constraints_json=constraints_json or {},
            total_steps=0,
            completed_steps=0,
            failed_steps=0,
            total_cost_usd=0.0,
            total_tokens=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_workflow(self, workflow_id: str) -> WorkflowRecord | None:
        """Retrieves a workflow by ID with eager loading of plans and steps."""
        stmt = (
            select(WorkflowRecord)
            .options(
                selectinload(WorkflowRecord.plans),
                selectinload(WorkflowRecord.steps),
            )
            .where(WorkflowRecord.id == workflow_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_workflows(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[WorkflowRecord], int]:
        """Lists workflows with optional status filtering and pagination."""
        base_query = select(WorkflowRecord)
        count_query = select(func.count(WorkflowRecord.id))

        if status:
            base_query = base_query.where(WorkflowRecord.status == status)
            count_query = count_query.where(WorkflowRecord.status == status)

        base_query = (
            base_query.options(
                selectinload(WorkflowRecord.plans),
                selectinload(WorkflowRecord.steps),
            )
            .order_by(desc(WorkflowRecord.created_at))
            .offset(offset)
            .limit(limit)
        )

        items_res = await self.session.execute(base_query)
        count_res = await self.session.execute(count_query)

        items = list(items_res.scalars().all())
        total = count_res.scalar() or 0
        return items, total

    async def update_workflow_status(
        self,
        workflow_id: str,
        status: str,
        error_message: str | None = None,
        active_plan_id: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> WorkflowRecord | None:
        """Updates the status and timestamps of a workflow."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None

        workflow.status = status
        workflow.updated_at = datetime.now(UTC)

        if error_message is not None:
            workflow.error_message = error_message
        if active_plan_id is not None:
            workflow.active_plan_id = active_plan_id
        if started_at is not None:
            workflow.started_at = started_at
        if completed_at is not None:
            workflow.completed_at = completed_at

        await self.session.flush()
        return workflow

    async def update_workflow_metrics(
        self,
        workflow_id: str,
        total_steps: int | None = None,
        completed_steps: int | None = None,
        failed_steps: int | None = None,
        cost_delta_usd: float = 0.0,
        tokens_delta: int = 0,
        context_updates: dict[str, Any] | None = None,
    ) -> WorkflowRecord | None:
        """Updates aggregate progress metrics, tokens, and context dictionary."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None

        if total_steps is not None:
            workflow.total_steps = total_steps
        if completed_steps is not None:
            workflow.completed_steps = completed_steps
        if failed_steps is not None:
            workflow.failed_steps = failed_steps

        if cost_delta_usd != 0.0:
            workflow.total_cost_usd = round(workflow.total_cost_usd + cost_delta_usd, 6)
        if tokens_delta != 0:
            workflow.total_tokens = workflow.total_tokens + tokens_delta

        if context_updates:
            ctx = dict(workflow.context_json or {})
            ctx.update(context_updates)
            workflow.context_json = ctx

        workflow.updated_at = datetime.now(UTC)
        await self.session.flush()
        return workflow

    async def save_plan(
        self,
        plan_id: str,
        workflow_id: str,
        version: int,
        goal: str,
        plan_json: dict[str, Any],
        success_criteria_json: list[Any] | None = None,
    ) -> WorkflowPlanRecord:
        """Persists a new plan version for a workflow and deactivates prior versions."""
        # Deactivate previous active plans for this workflow
        await self.session.execute(
            update(WorkflowPlanRecord)
            .where(WorkflowPlanRecord.workflow_id == workflow_id)
            .values(is_active=False)
        )

        plan = WorkflowPlanRecord(
            id=plan_id,
            workflow_id=workflow_id,
            version=version,
            goal=goal,
            plan_json=plan_json,
            success_criteria_json=success_criteria_json or [],
            is_active=True,
            created_at=datetime.now(UTC),
        )
        self.session.add(plan)

        # Update workflow's active plan pointer
        await self.session.execute(
            update(WorkflowRecord)
            .where(WorkflowRecord.id == workflow_id)
            .values(active_plan_id=plan_id, updated_at=datetime.now(UTC))
        )

        await self.session.flush()
        return plan

    async def get_active_plan(self, workflow_id: str) -> WorkflowPlanRecord | None:
        """Retrieves the active plan record for a workflow."""
        stmt = (
            select(WorkflowPlanRecord)
            .where(
                WorkflowPlanRecord.workflow_id == workflow_id,
                WorkflowPlanRecord.is_active == True,  # noqa: E712
            )
            .order_by(desc(WorkflowPlanRecord.version))
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_plan_by_id(self, plan_id: str) -> WorkflowPlanRecord | None:
        """Retrieves a specific plan record by its ID."""
        stmt = select(WorkflowPlanRecord).where(WorkflowPlanRecord.id == plan_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_steps(
        self,
        workflow_id: str,
        plan_id: str,
        steps: list[dict[str, Any]],
    ) -> list[WorkflowStepRecord]:
        """Bulk creates step records for a plan."""
        created_steps: list[WorkflowStepRecord] = []
        for s in steps:
            step_record = WorkflowStepRecord(
                id=str(uuid4()),
                workflow_id=workflow_id,
                plan_id=plan_id,
                step_id=s["step_id"],
                title=s.get("title", s["step_id"]),
                description=s.get("description", ""),
                capability_id=s["capability_id"],
                assigned_agent_id=s.get("assigned_agent_id"),
                status=s.get("status", "pending"),
                input_bindings_json=s.get("input_bindings", {}),
                output_result_json=None,
                error_info_json=None,
                task_id=None,
                verification_status=None,
                verification_result_json=None,
                retry_count=0,
                max_retries=s.get("max_retries", 2),
                timeout_seconds=s.get("timeout_seconds", 60),
                created_at=datetime.now(UTC),
            )
            self.session.add(step_record)
            created_steps.append(step_record)

        await self.session.flush()
        return created_steps

    async def get_steps(
        self,
        workflow_id: str,
        plan_id: str | None = None,
    ) -> list[WorkflowStepRecord]:
        """Retrieves steps for a workflow, optionally filtered by plan version."""
        stmt = select(WorkflowStepRecord).where(WorkflowStepRecord.workflow_id == workflow_id)
        if plan_id:
            stmt = stmt.where(WorkflowStepRecord.plan_id == plan_id)
        stmt = stmt.order_by(WorkflowStepRecord.created_at)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_step(self, workflow_id: str, step_id: str) -> WorkflowStepRecord | None:
        """Retrieves a single step by workflow ID and step identifier."""
        stmt = select(WorkflowStepRecord).where(
            WorkflowStepRecord.workflow_id == workflow_id,
            WorkflowStepRecord.step_id == step_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_step_status(
        self,
        workflow_id: str,
        step_id: str,
        status: str,
        assigned_agent_id: str | None = None,
        task_id: str | None = None,
        output_result_json: dict[str, Any] | None = None,
        error_info_json: dict[str, Any] | None = None,
        verification_status: str | None = None,
        verification_result_json: dict[str, Any] | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> WorkflowStepRecord | None:
        """Updates the status and execution state of a specific step."""
        step = await self.get_step(workflow_id, step_id)
        if not step:
            return None

        step.status = status
        if assigned_agent_id is not None:
            step.assigned_agent_id = assigned_agent_id
        if task_id is not None:
            step.task_id = task_id
        if output_result_json is not None:
            step.output_result_json = output_result_json
        if error_info_json is not None:
            step.error_info_json = error_info_json
        if verification_status is not None:
            step.verification_status = verification_status
        if verification_result_json is not None:
            step.verification_result_json = verification_result_json
        if started_at is not None:
            step.started_at = started_at
        if completed_at is not None:
            step.completed_at = completed_at

        await self.session.flush()
        return step

    async def increment_step_retry(self, workflow_id: str, step_id: str) -> int:
        """Increments the retry counter for a step and returns the updated count."""
        step = await self.get_step(workflow_id, step_id)
        if not step:
            return 0
        step.retry_count += 1
        await self.session.flush()
        return step.retry_count

    async def save_dependencies(
        self,
        workflow_id: str,
        dependencies: list[tuple[str, str]],
    ) -> list[WorkflowDependencyRecord]:
        """Saves DAG dependencies (step_id depends on depends_on_step_id)."""
        recs: list[WorkflowDependencyRecord] = []
        for step_id, dep_id in dependencies:
            rec = WorkflowDependencyRecord(
                id=str(uuid4()),
                workflow_id=workflow_id,
                step_id=step_id,
                depends_on_step_id=dep_id,
                created_at=datetime.now(UTC),
            )
            self.session.add(rec)
            recs.append(rec)
        await self.session.flush()
        return recs

    async def get_dependencies(self, workflow_id: str) -> list[tuple[str, str]]:
        """Retrieves all DAG edges for a workflow."""
        stmt = select(WorkflowDependencyRecord).where(
            WorkflowDependencyRecord.workflow_id == workflow_id
        )
        res = await self.session.execute(stmt)
        return [(r.step_id, r.depends_on_step_id) for r in res.scalars().all()]

    async def record_agent_execution(
        self,
        execution_id: str,
        agent_id: str,
        workflow_id: str,
        step_id: str,
        status: str,
        model_used: str | None = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
        duration_ms: int = 0,
    ) -> AgentExecutionRecord:
        """Records an agent execution trace entry."""
        rec = AgentExecutionRecord(
            id=execution_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            step_id=step_id,
            status=status,
            model_used=model_used,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
            created_at=datetime.now(UTC),
            completed_at=datetime.now(UTC) if status in ("completed", "failed") else None,
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def record_agent_message(
        self,
        message_id: str,
        workflow_id: str,
        sender_agent_id: str,
        recipient_agent_id: str,
        message_type: str,
        payload_json: dict[str, Any],
        step_id: str | None = None,
    ) -> AgentMessageRecord:
        """Records a typed inter-agent message in the workflow audit ledger."""
        rec = AgentMessageRecord(
            id=message_id,
            workflow_id=workflow_id,
            sender_agent_id=sender_agent_id,
            recipient_agent_id=recipient_agent_id,
            step_id=step_id,
            message_type=message_type,
            payload_json=payload_json,
            created_at=datetime.now(UTC),
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def list_agent_messages(
        self,
        workflow_id: str,
        limit: int = 100,
    ) -> list[AgentMessageRecord]:
        """Lists inter-agent messages for a workflow in chronological order."""
        stmt = (
            select(AgentMessageRecord)
            .where(AgentMessageRecord.workflow_id == workflow_id)
            .order_by(AgentMessageRecord.created_at)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    get_agent_messages = list_agent_messages

    async def list_agent_executions(
        self,
        workflow_id: str,
    ) -> list[AgentExecutionRecord]:
        """Lists execution traces for all agents in a workflow."""
        stmt = (
            select(AgentExecutionRecord)
            .where(AgentExecutionRecord.workflow_id == workflow_id)
            .order_by(AgentExecutionRecord.created_at)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    get_agent_executions = list_agent_executions

    async def get_executions_for_agent(
        self,
        agent_id: str,
        limit: int = 50,
    ) -> list[AgentExecutionRecord]:
        """Lists recent execution traces for a specific agent across all workflows."""
        stmt = (
            select(AgentExecutionRecord)
            .where(AgentExecutionRecord.agent_id == agent_id)
            .order_by(AgentExecutionRecord.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_agent_configuration(self, agent_id: str) -> AgentConfigurationRecord | None:
        """Retrieves stored configuration overrides for an agent."""
        stmt = select(AgentConfigurationRecord).where(AgentConfigurationRecord.agent_id == agent_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_agent_configuration(
        self,
        agent_id: str,
        enabled: bool = True,
        preferred_model: str | None = None,
        concurrency_limit: int = 1,
        timeout_seconds: int = 60,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        local_first: bool = True,
        cloud_permitted: bool = False,
        allowed_capabilities: list[str] | None = None,
        custom_settings: dict[str, Any] | None = None,
    ) -> AgentConfigurationRecord:
        """Saves or updates persisted configuration for an agent."""
        cfg = await self.get_agent_configuration(agent_id)
        if not cfg:
            cfg = AgentConfigurationRecord(
                agent_id=agent_id,
                enabled=enabled,
                preferred_model=preferred_model,
                concurrency_limit=concurrency_limit,
                timeout_seconds=timeout_seconds,
                temperature=temperature,
                max_tokens=max_tokens,
                local_first=local_first,
                cloud_permitted=cloud_permitted,
                allowed_capabilities_json=allowed_capabilities or [],
                custom_settings_json=custom_settings or {},
            )
            self.session.add(cfg)
        else:
            cfg.enabled = enabled
            cfg.preferred_model = preferred_model
            cfg.concurrency_limit = concurrency_limit
            cfg.timeout_seconds = timeout_seconds
            cfg.temperature = temperature
            cfg.max_tokens = max_tokens
            cfg.local_first = local_first
            cfg.cloud_permitted = cloud_permitted
            if allowed_capabilities is not None:
                cfg.allowed_capabilities_json = allowed_capabilities
            if custom_settings is not None:
                cfg.custom_settings_json = custom_settings
        await self.session.flush()
        return cfg

    async def record_verification_result(
        self,
        verification_id: str,
        workflow_id: str,
        step_id: str,
        verification_type: str,
        status: str,
        passed: bool,
        evidence_json: dict[str, Any],
        details: str | None = None,
    ) -> VerificationResultRecord:
        """Records a verification audit outcome."""
        rec = VerificationResultRecord(
            id=verification_id,
            workflow_id=workflow_id,
            step_id=step_id,
            verification_type=verification_type,
            status=status,
            passed=passed,
            evidence_json=evidence_json,
            details=details,
            created_at=datetime.now(UTC),
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def list_verification_results(
        self,
        workflow_id: str,
    ) -> list[VerificationResultRecord]:
        """Lists verification audit results for a workflow."""
        stmt = (
            select(VerificationResultRecord)
            .where(VerificationResultRecord.workflow_id == workflow_id)
            .order_by(VerificationResultRecord.created_at)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    get_verification_results = list_verification_results

    async def record_recovery_attempt(
        self,
        attempt_id: str,
        workflow_id: str,
        step_id: str,
        failure_category: str,
        recovery_action: str,
        attempt_number: int,
        success: bool,
        details_json: dict[str, Any],
    ) -> RecoveryAttemptRecord:
        """Records a failure recovery attempt in the workflow audit ledger."""
        rec = RecoveryAttemptRecord(
            id=attempt_id,
            workflow_id=workflow_id,
            step_id=step_id,
            failure_category=failure_category,
            recovery_action=recovery_action,
            attempt_number=attempt_number,
            success=success,
            details_json=details_json,
            created_at=datetime.now(UTC),
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def list_recovery_attempts(
        self,
        workflow_id: str,
    ) -> list[RecoveryAttemptRecord]:
        """Lists recovery attempts for a workflow."""
        stmt = (
            select(RecoveryAttemptRecord)
            .where(RecoveryAttemptRecord.workflow_id == workflow_id)
            .order_by(RecoveryAttemptRecord.created_at)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    get_recovery_attempts = list_recovery_attempts

    async def get_workflow_summary_stats(self) -> dict[str, Any]:
        """Returns aggregate operational statistics across all workflows."""
        total_res = await self.session.execute(select(func.count(WorkflowRecord.id)))
        completed_res = await self.session.execute(
            select(func.count(WorkflowRecord.id)).where(WorkflowRecord.status == "completed")
        )
        running_res = await self.session.execute(
            select(func.count(WorkflowRecord.id)).where(
                WorkflowRecord.status.in_(["running", "queued", "verifying", "recovering"])
            )
        )
        paused_res = await self.session.execute(
            select(func.count(WorkflowRecord.id)).where(WorkflowRecord.status == "paused")
        )
        failed_res = await self.session.execute(
            select(func.count(WorkflowRecord.id)).where(WorkflowRecord.status == "failed")
        )

        total = total_res.scalar() or 0
        completed = completed_res.scalar() or 0
        running = running_res.scalar() or 0
        paused = paused_res.scalar() or 0
        failed = failed_res.scalar() or 0

        completion_rate = (completed / total * 100.0) if total > 0 else 100.0

        return {
            "total_workflows": total,
            "completed_workflows": completed,
            "running_workflows": running,
            "paused_workflows": paused,
            "failed_workflows": failed,
            "completion_rate_percent": round(completion_rate, 1),
        }

    get_workflow_stats = get_workflow_summary_stats

    async def reconcile_active_workflows(self) -> list[str]:
        """Reconciles workflows that were left running or verifying when backend stopped."""
        active_statuses = ["running", "verifying", "recovering", "planning"]
        stmt = select(WorkflowRecord).where(WorkflowRecord.status.in_(active_statuses))
        res = await self.session.execute(stmt)
        reconciled_ids: list[str] = []

        for wf in res.scalars().all():
            wf.status = "paused"
            wf.error_message = "Workflow paused during backend service restart; safe to resume."
            wf.updated_at = datetime.now(UTC)
            reconciled_ids.append(wf.id)

            # Reconcile any in-flight steps
            await self.session.execute(
                update(WorkflowStepRecord)
                .where(
                    WorkflowStepRecord.workflow_id == wf.id,
                    WorkflowStepRecord.status.in_(["running", "verifying"]),
                )
                .values(status="paused")
            )

        if reconciled_ids:
            await self.session.flush()

        return reconciled_ids
