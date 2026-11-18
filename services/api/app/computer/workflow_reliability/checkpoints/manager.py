"""Persistent Checkpoint Manager for execution milestones."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.computer.workflow_reliability.checkpoints.integrity import CheckpointIntegrityValidator
from app.computer.workflow_reliability.checkpoints.state_fingerprints import StateFingerprintService
from app.computer.workflow_reliability.contracts import (
    CheckpointType,
    ExecutionCheckpoint,
    StateFingerprint,
)
from app.computer.workflow_reliability.errors import CheckpointError, CheckpointIntegrityError

logger = logging.getLogger("autonom.reliability.checkpoint_manager")


class CheckpointManager:
    """Manages durable execution checkpoints and state preservation."""

    def __init__(self) -> None:
        # Map: execution_id -> List[ExecutionCheckpoint]
        self._checkpoints: Dict[str, List[ExecutionCheckpoint]] = {}

    def create_checkpoint(
        self,
        execution_id: str,
        procedure_id: str = "default_proc",
        procedure_version: int = 1,
        step_index: int = 0,
        checkpoint_type: CheckpointType = CheckpointType.STEP,
        completed_step_ids: Optional[List[str]] = None,
        verified_outputs: Optional[Dict[str, Any]] = None,
        artifact_refs: Optional[List[str]] = None,
        fingerprint: Optional[StateFingerprint] = None,
        pending_step_ids: Optional[List[str]] = None,
        side_effect_ledger_ids: Optional[List[str]] = None,
        step_id: Optional[str] = None,
        scope_variables: Optional[Dict[str, Any]] = None,
        completed_steps: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ExecutionCheckpoint:
        """Create and persist a verified execution checkpoint."""
        done_steps = completed_step_ids or completed_steps or []
        checkpoint = ExecutionCheckpoint(
            execution_id=execution_id,
            procedure_id=procedure_id,
            procedure_version=procedure_version,
            step_id=step_id,
            step_index=step_index,
            checkpoint_type=checkpoint_type,
            completed_step_ids=done_steps,
            completed_steps=done_steps,
            verified_outputs=verified_outputs or {},
            artifact_refs=artifact_refs or [],
            fingerprint=fingerprint or StateFingerprintService.capture_fingerprint(),
            state_fingerprint=fingerprint,
            scope_variables=scope_variables or {},
            pending_step_ids=pending_step_ids or [],
            side_effect_ledger_ids=side_effect_ledger_ids or [],
        )

        checkpoint.integrity_hash = checkpoint.compute_integrity()
        CheckpointIntegrityValidator.validate_integrity(checkpoint)

        if execution_id not in self._checkpoints:
            self._checkpoints[execution_id] = []

        self._checkpoints[execution_id].append(checkpoint)
        logger.info(
            "Checkpoint created: %s (exec: %s, step_idx: %d, type: %s)",
            checkpoint.checkpoint_id,
            execution_id,
            step_index,
            checkpoint_type.value,
        )
        return checkpoint

    def get_latest_checkpoint(self, execution_id: str) -> Optional[ExecutionCheckpoint]:
        """Retrieve the most recent verified checkpoint for an execution."""
        chk_list = self._checkpoints.get(execution_id, [])
        if not chk_list:
            return None
        # Return latest
        return chk_list[-1]

    def get_latest_valid_checkpoint(self, execution_id: str) -> Optional[ExecutionCheckpoint]:
        """Alias for get_latest_checkpoint."""
        return self.get_latest_checkpoint(execution_id)

    def list_checkpoints(self, execution_id: str) -> List[ExecutionCheckpoint]:
        """List all checkpoints for an execution in chronological order."""
        return list(self._checkpoints.get(execution_id, []))

    def get_checkpoints(self, execution_id: str) -> List[ExecutionCheckpoint]:
        """Alias for list_checkpoints."""
        return self.list_checkpoints(execution_id)

    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate integrity for a specific checkpoint ID."""
        for chk_list in self._checkpoints.values():
            for c in chk_list:
                if c.checkpoint_id == checkpoint_id:
                    try:
                        CheckpointIntegrityValidator.validate_integrity(c)
                        return True
                    except CheckpointIntegrityError:
                        return False
        return False
