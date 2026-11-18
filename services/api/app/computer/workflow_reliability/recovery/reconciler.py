"""Crash and restart reconciler for interrupted workflow executions."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.computer.workflow_reliability.checkpoints.manager import CheckpointManager
from app.computer.workflow_reliability.contracts import (
    ProcedureExecution,
    ProcedureExecutionStatus,
    RecoveryClassification,
    RecoveryPlan,
    ReusableProcedure,
)
from app.computer.workflow_reliability.procedures.registry import ProcedureRegistry
from app.computer.workflow_reliability.recovery.resume_planner import ResumePlanner
from app.computer.workflow_reliability.recovery.side_effects import SideEffectLedger

logger = logging.getLogger("autonom.reliability.reconciler")


class CrashReconciler:
    """Detects interrupted executions upon backend startup and reconciles recovery state."""

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        side_effect_ledger: SideEffectLedger,
        procedure_registry: ProcedureRegistry,
    ) -> None:
        self.checkpoint_manager = checkpoint_manager
        self.side_effect_ledger = side_effect_ledger
        self.procedure_registry = procedure_registry

    def reconcile_execution(self, execution: ProcedureExecution) -> Optional[RecoveryPlan]:
        """Inspect an incomplete or interrupted execution and generate its recovery plan."""
        # If execution was running or preflight when interrupted, mark it as paused/pending recovery
        if execution.status in (ProcedureExecutionStatus.RUNNING, ProcedureExecutionStatus.PREFLIGHT):
            execution.status = ProcedureExecutionStatus.PAUSED
            execution.error_message = "Execution interrupted by system restart or process termination."

        proc = self.procedure_registry.get(execution.procedure_id, execution.version)
        if not proc:
            logger.warning("Cannot reconcile execution %s: Procedure not found", execution.execution_id)
            return None

        latest_chk = self.checkpoint_manager.get_latest_checkpoint(execution.execution_id)
        if not latest_chk:
            # No checkpoints exist: cannot safely resume partial work
            logger.info("No checkpoint available for interrupted execution %s", execution.execution_id)
            return RecoveryPlan(
                execution_id=execution.execution_id,
                checkpoint_id="none",
                classification=RecoveryClassification.NONRECOVERABLE,
                can_resume=False,
                steps_to_skip=[],
                steps_to_revalidate=[],
                steps_to_execute=[s.step_id for s in proc.steps],
                explanation="No durable checkpoint was committed prior to interruption.",
            )

        plan = ResumePlanner.generate_plan(proc, latest_chk, self.side_effect_ledger)
        logger.info(
            "Reconciled execution %s: %s (can_resume: %s)",
            execution.execution_id,
            plan.classification.value,
            plan.can_resume,
        )
        return plan
