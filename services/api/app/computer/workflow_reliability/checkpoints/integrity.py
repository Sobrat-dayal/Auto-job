"""Checkpoint integrity validation and verification."""

import hashlib
from app.computer.workflow_reliability.contracts import ExecutionCheckpoint
from app.computer.workflow_reliability.errors import CheckpointIntegrityError


class CheckpointIntegrityValidator:
    """Verifies that an ExecutionCheckpoint matches its computed cryptographic signature."""

    @classmethod
    def seal_checkpoint(cls, checkpoint: ExecutionCheckpoint) -> ExecutionCheckpoint:
        """Compute and set integrity hash on checkpoint, returning the sealed checkpoint."""
        checkpoint.integrity_hash = checkpoint.compute_integrity()
        return checkpoint

    @classmethod
    def verify_checkpoint(cls, checkpoint: ExecutionCheckpoint) -> bool:
        """Verify whether the checkpoint matches its computed cryptographic signature."""
        expected = checkpoint.compute_integrity()
        return bool(checkpoint.integrity_hash and checkpoint.integrity_hash == expected)

    @staticmethod
    def validate_integrity(checkpoint: ExecutionCheckpoint) -> None:
        """Assert checkpoint integrity hash; raises CheckpointIntegrityError on mismatch."""
        expected_hash = checkpoint.compute_integrity()
        if not checkpoint.integrity_hash:
            checkpoint.integrity_hash = expected_hash
            return

        if checkpoint.integrity_hash != expected_hash:
            raise CheckpointIntegrityError(
                f"Checkpoint '{checkpoint.checkpoint_id}' integrity validation failed. Hash mismatch."
            )
