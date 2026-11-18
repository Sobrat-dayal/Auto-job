"""Unit tests for Stage 20 Side-Effect Ledger, Idempotency, and Crash Recovery."""

import pytest
from app.computer.workflow_reliability.checkpoints.manager import CheckpointManager
from app.computer.workflow_reliability.checkpoints.state_fingerprints import StateFingerprintService
from app.computer.workflow_reliability.contracts import (
    CheckpointType,
    ProcedureExecution,
    ProcedureExecutionStatus,
    ProcedureStep,
    RecoveryClassification,
    ReplayMode,
    ReusableProcedure,
    SideEffectClass,
    SideEffectOutcome,
)
from app.computer.workflow_reliability.errors import DuplicateSideEffectBlockedError
from app.computer.workflow_reliability.recovery.idempotency import IdempotencyClassifier
from app.computer.workflow_reliability.recovery.reconciler import CrashReconciler
from app.computer.workflow_reliability.recovery.resume_planner import ResumePlanner
from app.computer.workflow_reliability.recovery.side_effects import SideEffectLedger


def test_idempotency_classifier():
    classifier = IdempotencyClassifier()
    assert classifier.classify_action("browser", "inspect_dom") == SideEffectClass.READ_ONLY
    assert classifier.classify_action("desktop", "inspect_window") == SideEffectClass.READ_ONLY
    assert classifier.classify_action("browser", "navigate") == SideEffectClass.IDEMPOTENT
    assert classifier.classify_action("browser", "submit_form") == SideEffectClass.NON_IDEMPOTENT
    assert classifier.classify_action("desktop", "send_keys") == SideEffectClass.NON_IDEMPOTENT


def test_side_effect_ledger_duplicate_blocking():
    ledger = SideEffectLedger()
    intent_hash = ledger.compute_intent_hash(
        target_system="https://jobs.example.com",
        operation="submit_application",
        parameters={"job_id": "12345", "candidate": "Sobrat"},
    )
    # Register first time
    effect = ledger.record_intent(
        execution_id="exec_side_1",
        step_id="step_submit",
        side_effect_class=SideEffectClass.NON_IDEMPOTENT,
        target_system="https://jobs.example.com",
        operation="submit_application",
        parameters={"job_id": "12345", "candidate": "Sobrat"},
    )
    assert effect.outcome == SideEffectOutcome.PENDING
    ledger.confirm_effect(effect.effect_id, {"response_code": 200})

    # Attempting to re-execute the same non-idempotent action must raise DuplicateSideEffectBlockedError
    with pytest.raises(DuplicateSideEffectBlockedError):
        ledger.record_intent(
            execution_id="exec_side_1",
            step_id="step_submit",
            side_effect_class=SideEffectClass.NON_IDEMPOTENT,
            target_system="https://jobs.example.com",
            operation="submit_application",
            parameters={"job_id": "12345", "candidate": "Sobrat"},
        )


def test_resume_planner_skips_verified_steps():
    planner = ResumePlanner()
    fps = StateFingerprintService()
    fp = fps.capture_fingerprint(window_title="Browser", process_name="msedge.exe")

    chk_mgr = CheckpointManager()
    chk = chk_mgr.create_checkpoint(
        execution_id="exec_res_1",
        step_id="step_2",
        step_index=2,
        checkpoint_type=CheckpointType.POST_ACTION,
        fingerprint=fp,
        scope_variables={},
        completed_steps=["step_1", "step_2"],
    )

    proc = ReusableProcedure(
        procedure_id="proc_res",
        version=1,
        name="Multi Step Procedure",
        category="general",
        steps=[
            ProcedureStep(step_id="step_1", order_index=1, name="Init", action_type="navigate", target_surface="browser"),
            ProcedureStep(step_id="step_2", order_index=2, name="Fill Form", action_type="fill", target_surface="browser"),
            ProcedureStep(step_id="step_3", order_index=3, name="Submit", action_type="submit", target_surface="browser"),
        ],
    )

    ledger = SideEffectLedger()
    plan = planner.plan_resume(
        execution_id="exec_res_1",
        procedure=proc,
        checkpoint=chk,
        side_effect_ledger=ledger,
    )
    assert plan.can_resume is True
    assert plan.resume_step_index == 3
    assert plan.actions_to_skip == ["step_1", "step_2"]
    assert plan.actions_to_reexecute == ["step_3"]
    assert plan.classification == RecoveryClassification.SAFE_TO_RETRY
