"""Resume Planner: computes safe continuation paths from checkpoints without duplicating work."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.computer.workflow_reliability.contracts import (
    ExecutionCheckpoint,
    RecoveryClassification,
    RecoveryPlan,
    ReusableProcedure,
    SideEffectClass,
)
from app.computer.workflow_reliability.errors import RecoveryPlanningError
from app.computer.workflow_reliability.recovery.side_effects import SideEffectLedger

logger = logging.getLogger("autonom.reliability.resume_planner")


class ResumePlanner:
    """Plans continuation from a checkpoint by identifying completed, skipped, and remaining steps."""

    @classmethod
    def generate_plan(
        cls,
        procedure: ReusableProcedure,
        checkpoint: ExecutionCheckpoint,
        side_effect_ledger: SideEffectLedger,
    ) -> RecoveryPlan:
        """Create a structured recovery plan."""
        completed_set = set(checkpoint.completed_step_ids)
        steps_to_skip: List[str] = []
        steps_to_revalidate: List[str] = []
        steps_to_execute: List[str] = []
        uncertain_operations: List[Dict[str, Any]] = []

        all_step_ids = [s.step_id for s in procedure.steps]
        step_map = {s.step_id: s for s in procedure.steps}

        # 1. Inspect completed steps
        for sid in all_step_ids:
            if sid in completed_set:
                steps_to_skip.append(sid)
            else:
                steps_to_execute.append(sid)

        # 2. Check for uncertain external side effects
        execution_effects = side_effect_ledger.get_execution_effects(checkpoint.execution_id)
        for eff in execution_effects:
            if eff.outcome == "unknown_outcome":
                uncertain_operations.append({
                    "effect_id": eff.effect_id,
                    "step_id": eff.step_id,
                    "destination": eff.destination,
                    "outcome": eff.outcome.value,
                })

        # 3. Classify recovery
        if uncertain_operations:
            classification = RecoveryClassification.EXTERNAL_OUTCOME_UNKNOWN
            can_resume = False
            explanation = "Cannot automatically resume: Indeterminate external outcome detected in side-effect ledger."
        elif not steps_to_execute:
            classification = RecoveryClassification.SAFE_TO_RESUME
            can_resume = True
            explanation = "All steps already completed in checkpoint."
        else:
            classification = RecoveryClassification.SAFE_TO_RESUME
            can_resume = True
            explanation = f"Safe to resume: skipping {len(steps_to_skip)} completed steps, executing remaining {len(steps_to_execute)} steps."

        return RecoveryPlan(
            execution_id=checkpoint.execution_id,
            checkpoint_id=checkpoint.checkpoint_id,
            classification=classification,
            can_resume=can_resume,
            steps_to_skip=steps_to_skip,
            steps_to_revalidate=steps_to_revalidate,
            steps_to_execute=steps_to_execute,
            actions_to_skip=steps_to_skip,
            actions_to_reexecute=steps_to_execute,
            resume_step_index=len(steps_to_skip) + 1,
            uncertain_operations=uncertain_operations,
            required_permissions=procedure.required_permissions,
            explanation=explanation,
            rationale=explanation,
        )

    @classmethod
    def plan_resume(
        cls,
        execution_id: str,
        procedure: ReusableProcedure,
        checkpoint: ExecutionCheckpoint,
        side_effect_ledger: SideEffectLedger,
    ) -> RecoveryPlan:
        """Alias for generate_plan with explicit execution_id."""
        plan = cls.generate_plan(procedure, checkpoint, side_effect_ledger)
        plan.execution_id = execution_id
        return plan
