"""State-aware Replay Executor with dynamic target resolution and checkpointing."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional

from app.computer.workflow_reliability.checkpoints.manager import CheckpointManager
from app.computer.workflow_reliability.contracts import (
    CheckpointPolicy,
    CheckpointType,
    ExecutionCheckpoint,
    ProcedureExecution,
    ProcedureExecutionStatus,
    ProcedureStep,
    RecoveryPlan,
    ReplayMode,
    ReusableProcedure,
    SideEffectClass,
    SideEffectOutcome,
)
from app.computer.workflow_reliability.errors import (
    DuplicateSideEffectBlockedError,
    EmergencyStopActiveError,
    PostconditionFailedError,
    PreconditionFailedError,
    ReplayError,
)
from app.computer.workflow_reliability.procedures.parameters import ParameterEngine
from app.computer.workflow_reliability.recovery.idempotency import IdempotencyClassifier
from app.computer.workflow_reliability.recovery.side_effects import SideEffectLedger
from app.computer.workflow_reliability.replay.conditions import StepConditionEvaluator
from app.computer.workflow_reliability.replay.targets import DynamicTargetResolver

logger = logging.getLogger("autonom.reliability.replay_executor")

PARAM_PLACEHOLDER_REGEX = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


class ReplayExecutor:
    """Executes procedures in DRY_RUN, STEP_BY_STEP, AUTOMATIC, or RESUME_FROM_CHECKPOINT mode."""

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        side_effect_ledger: SideEffectLedger,
        action_dispatcher: Optional[Callable[[ProcedureStep, Dict[str, Any]], Any]] = None,
        emergency_guard: Optional[Any] = None,
    ) -> None:
        self.checkpoint_manager = checkpoint_manager
        self.side_effect_ledger = side_effect_ledger
        self.action_dispatcher = action_dispatcher
        self.emergency_guard = emergency_guard

    async def execute(
        self,
        procedure: ReusableProcedure,
        arguments: Dict[str, Any],
        mode: ReplayMode = ReplayMode.AUTOMATIC_AUTHORIZED,
        recovery_plan: Optional[RecoveryPlan] = None,
    ) -> ProcedureExecution:
        """Execute or resume a procedure run."""
        bound_args = ParameterEngine.validate_and_bind(procedure.parameters, arguments)

        execution = ProcedureExecution(
            procedure_id=procedure.procedure_id,
            version=procedure.version,
            mode=mode,
            status=ProcedureExecutionStatus.RUNNING,
            parameters=bound_args,
        )

        steps_to_skip = set(recovery_plan.steps_to_skip if recovery_plan else [])
        if recovery_plan and recovery_plan.steps_to_skip:
            execution.completed_steps = list(recovery_plan.steps_to_skip)
            logger.info("Resuming execution from recovery plan: skipping %d steps", len(steps_to_skip))

        start_time = time.perf_counter()

        try:
            for idx, step in enumerate(procedure.steps):
                execution.current_step_index = idx

                # 1. Skip previously verified steps during recovery
                if step.step_id in steps_to_skip:
                    logger.debug("Skipping already verified step: %s", step.step_id)
                    continue

                # 2. Check Emergency Stop
                if self.emergency_guard and hasattr(self.emergency_guard, "ensure_execution_allowed"):
                    self.emergency_guard.ensure_execution_allowed()

                # 3. Resolve input bindings (substituting {{param_name}})
                resolved_inputs = self._resolve_input_bindings(step.input_bindings, bound_args)

                # 4. Dynamic Target Re-resolution
                resolved_target = await DynamicTargetResolver.resolve_live_target(
                    step.target, preferred_method=step.preferred_method
                )

                # 5. Precondition Evaluation
                mock_obs = {"window_title": resolved_target.get("element_name") or "", "url": resolved_target.get("url") or ""}
                pre_ok, pre_msg = StepConditionEvaluator.evaluate_preconditions(step.preconditions, mock_obs)
                if not pre_ok:
                    raise PreconditionFailedError(f"Precondition failed for step {step.step_id}: {pre_msg}")

                # 6. Pre-action Checkpoint (BEFORE_IRREVERSIBLE)
                if step.checkpoint_policy == CheckpointPolicy.BEFORE_IRREVERSIBLE:
                    chk = self.checkpoint_manager.create_checkpoint(
                        execution_id=execution.execution_id,
                        procedure_id=procedure.procedure_id,
                        procedure_version=procedure.version,
                        step_index=idx,
                        checkpoint_type=CheckpointType.STEP,
                        completed_step_ids=execution.completed_steps,
                    )
                    execution.latest_checkpoint_id = chk.checkpoint_id

                # 7. Side-effect Ledger Intent Recording
                side_effect = None
                if step.side_effect_class in (SideEffectClass.NON_IDEMPOTENT, SideEffectClass.IRREVERSIBLE):
                    dest = resolved_target.get("url") or resolved_target.get("dom_selector") or "external_service"
                    side_effect = self.side_effect_ledger.record_intent(
                        execution_id=execution.execution_id,
                        step_id=step.step_id,
                        action_category=step.action_type,
                        destination=str(dest),
                        parameters=resolved_inputs,
                    )
                    execution.side_effect_count += 1

                # 8. Action Execution (unless in DRY_RUN mode)
                action_result = {"verification_status": "success"}
                if mode != ReplayMode.DRY_RUN and self.action_dispatcher:
                    res = await self.action_dispatcher(step, resolved_inputs)
                    if isinstance(res, dict):
                        action_result = res

                # 9. Postcondition Evaluation
                post_ok, post_msg = StepConditionEvaluator.evaluate_postconditions(step.postconditions, action_result)
                if not post_ok:
                    raise PostconditionFailedError(f"Postcondition failed for step {step.step_id}: {post_msg}")

                # 10. Confirm Side-Effect Outcome
                if side_effect:
                    self.side_effect_ledger.confirm_outcome(
                        side_effect.effect_id,
                        outcome=SideEffectOutcome.CONFIRMED,
                        evidence={"step_id": step.step_id, "time": datetime.now(timezone.utc).isoformat()},
                    )

                execution.completed_steps.append(step.step_id)

                # 11. Post-action Checkpoint
                chk = self.checkpoint_manager.create_checkpoint(
                    execution_id=execution.execution_id,
                    procedure_id=procedure.procedure_id,
                    procedure_version=procedure.version,
                    step_index=idx + 1,
                    checkpoint_type=CheckpointType.STEP,
                    completed_step_ids=execution.completed_steps,
                )
                execution.latest_checkpoint_id = chk.checkpoint_id

            execution.status = ProcedureExecutionStatus.COMPLETED

        except Exception as exc:
            logger.error("Procedure execution failed at step %d: %s", execution.current_step_index, exc)
            execution.status = ProcedureExecutionStatus.FAILED
            execution.error_message = str(exc)

            # Failure checkpoint
            try:
                chk = self.checkpoint_manager.create_checkpoint(
                    execution_id=execution.execution_id,
                    procedure_id=procedure.procedure_id,
                    procedure_version=procedure.version,
                    step_index=execution.current_step_index,
                    checkpoint_type=CheckpointType.RECOVERY,
                    completed_step_ids=execution.completed_steps,
                )
                execution.latest_checkpoint_id = chk.checkpoint_id
            except Exception as chk_exc:
                logger.error("Failed to commit recovery checkpoint: %s", chk_exc)

            raise

        finally:
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            execution.checkpoints = self.checkpoint_manager.list_checkpoints(execution.execution_id)
            execution.side_effects = self.side_effect_ledger.get_execution_effects(execution.execution_id)
            execution.total_steps = len(procedure.steps)

        return execution

    def _resolve_input_bindings(self, bindings: Dict[str, Any], bound_args: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute {{param_name}} placeholders with bound parameter values."""
        resolved: Dict[str, Any] = {}
        for k, v in bindings.items():
            if isinstance(v, str):
                match = PARAM_PLACEHOLDER_REGEX.match(v.strip())
                if match:
                    param_name = match.group(1)
                    resolved[k] = bound_args.get(param_name, v)
                else:
                    resolved[k] = v
            else:
                resolved[k] = v
        return resolved
