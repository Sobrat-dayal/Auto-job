"""Stage 20: Workflow Reliability & Computer Action Recording Exception Hierarchy."""

from typing import Any, Dict, Optional


class WorkflowReliabilityError(Exception):
    """Base exception for all Stage 20 Workflow Reliability operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RecordingError(WorkflowReliabilityError):
    """Base exception for recording session failures."""
    pass


class RecordingActiveError(RecordingError):
    """Raised when an operation conflicts with an ongoing recording session."""
    pass


class RecordingClosedError(RecordingError):
    """Raised when an operation attempts to record into a non-active session."""
    pass


class RecordingScopeExceededError(RecordingError):
    """Raised when an action target falls outside authorized recording scopes."""
    pass


class ProcedureError(WorkflowReliabilityError):
    """Base exception for procedure operations."""
    pass


class ProcedureCompilationError(ProcedureError):
    """Raised when compiling an action sequence into a procedure fails."""
    pass


class ProcedureValidationError(ProcedureError):
    """Raised when a procedure definition violates safety or structural constraints."""
    pass


class ProcedureNotFoundError(ProcedureError):
    """Raised when a procedure ID or version does not exist."""
    pass


class ProcedureVersionConflictError(ProcedureError):
    """Raised when attempting to modify an immutable published procedure version."""
    pass


class ReplayError(WorkflowReliabilityError):
    """Base exception for replay execution failures."""
    pass


class ReplayPreflightFailedError(ReplayError):
    """Raised when preflight safety checks fail prior to replay execution."""
    pass


class EmergencyStopActiveError(ReplayError):
    """Raised when an active emergency stop prevents execution or replay."""
    pass


class TargetReResolutionError(ReplayError):
    """Raised when an action target cannot be safely re-resolved in the live UI."""
    pass


class PreconditionFailedError(ReplayError):
    """Raised when a step's required UI or application state is not met."""
    pass


class PostconditionFailedError(ReplayError):
    """Raised when post-action mutation verification fails."""
    pass


class CheckpointError(WorkflowReliabilityError):
    """Base exception for checkpoint operations."""
    pass


class CheckpointIntegrityError(CheckpointError):
    """Raised when a checkpoint's hash or schema validation fails."""
    pass


class CheckpointRestorationError(CheckpointError):
    """Raised when state reconciliation during checkpoint restoration fails."""
    pass


class SideEffectError(WorkflowReliabilityError):
    """Base exception for side-effect ledger operations."""
    pass


class DuplicateSideEffectBlockedError(SideEffectError):
    """Raised when attempting to replay an action with an already confirmed side effect."""
    pass


class UnknownOutcomeBlockedError(SideEffectError):
    """Raised when an external operation's outcome is indeterminate and replay is prohibited."""
    pass


class NonIdempotentReplayBlockedError(SideEffectError):
    """Raised when an unconfirmed non-idempotent action cannot be safely replayed."""
    pass


class RecoveryError(WorkflowReliabilityError):
    """Base exception for recovery operations."""
    pass


class RecoveryPlanningError(RecoveryError):
    """Raised when generating a recovery plan fails."""
    pass


class UnrecoverableExecutionError(RecoveryError):
    """Raised when an execution cannot be safely resumed and must be aborted."""
    pass
