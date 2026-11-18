"""Unit tests for Stage 20 Durable Checkpoints and State Fingerprint Integrity."""

import pytest
from app.computer.workflow_reliability.checkpoints.integrity import CheckpointIntegrityValidator
from app.computer.workflow_reliability.checkpoints.manager import CheckpointManager
from app.computer.workflow_reliability.checkpoints.state_fingerprints import StateFingerprintService
from app.computer.workflow_reliability.contracts import (
    CheckpointType,
    ExecutionCheckpoint,
    StateFingerprint,
)
from app.computer.workflow_reliability.errors import CheckpointIntegrityError


def test_state_fingerprint_capture():
    fps = StateFingerprintService()
    fp = fps.capture_fingerprint(
        window_title="Calculator",
        process_name="calc.exe",
        url="https://autonom.ai/app",
    )
    assert fp.active_window_title == "Calculator"
    assert fp.active_process_name == "calc.exe"
    assert fp.browser_url == "https://autonom.ai/app"
    assert fp.fingerprint_id.startswith("fp_")


def test_checkpoint_integrity_hash_verification():
    validator = CheckpointIntegrityValidator()
    fp = StateFingerprint(
        fingerprint_id="fp_test",
        active_window_title="Notepad",
        active_process_name="notepad.exe",
    )
    cp = ExecutionCheckpoint(
        checkpoint_id="chk_test_1",
        execution_id="exec_100",
        step_id="step_1",
        step_index=1,
        checkpoint_type=CheckpointType.POST_ACTION,
        state_fingerprint=fp,
        scope_variables={"counter": 42},
        completed_steps=["step_1"],
    )
    hashed_cp = validator.seal_checkpoint(cp)
    assert hashed_cp.integrity_hash != ""
    assert validator.verify_checkpoint(hashed_cp) is True

    # Tampering with checkpoint content invalidates the hash
    tampered_cp = hashed_cp.model_copy(update={"step_index": 99})
    assert validator.verify_checkpoint(tampered_cp) is False


def test_checkpoint_manager_persistence_and_retrieval():
    mgr = CheckpointManager()
    fp = StateFingerprint(
        fingerprint_id="fp_test_2",
        active_window_title="Edge",
        active_process_name="msedge.exe",
    )
    cp = mgr.create_checkpoint(
        execution_id="exec_200",
        step_id="step_submit",
        step_index=2,
        checkpoint_type=CheckpointType.PRE_SIDE_EFFECT,
        fingerprint=fp,
        scope_variables={"query": "test"},
        completed_steps=["step_init", "step_submit"],
    )
    assert cp.execution_id == "exec_200"

    history = mgr.get_checkpoints("exec_200")
    assert len(history) == 1
    assert history[0].step_id == "step_submit"

    latest = mgr.get_latest_valid_checkpoint("exec_200")
    assert latest is not None
    assert latest.checkpoint_id == cp.checkpoint_id
