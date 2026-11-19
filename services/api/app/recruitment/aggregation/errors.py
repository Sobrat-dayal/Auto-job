"""Domain exceptions for Job Aggregation Engine (Stage 27)."""


class AggregationError(Exception):
    """Base exception for all aggregation engine errors."""
    pass


class CanonicalJobNotFoundError(AggregationError):
    """Raised when a canonical job ID does not exist."""
    pass


class CanonicalEmployerNotFoundError(AggregationError):
    """Raised when an employer ID does not exist."""
    pass


class DuplicateCandidateNotFoundError(AggregationError):
    """Raised when a duplicate candidate pair ID does not exist."""
    pass


class MergeValidationError(AggregationError):
    """Raised when a merge operation violates safety constraints."""
    pass


class SplitValidationError(AggregationError):
    """Raised when a split operation cannot be performed."""
    pass


class CircularMergeError(MergeValidationError):
    """Raised when attempting to merge a job into itself or a cyclic alias."""
    pass


class ConflictNotFoundError(AggregationError):
    """Raised when a field conflict ID cannot be found."""
    pass


class TaskNotFoundError(AggregationError):
    """Raised when an aggregation task ID is not found."""
    pass


class AuthorizationDeniedError(AggregationError):
    """Raised when an operation lacks necessary Stage 14 permissions."""
    pass


class EmergencyStopActiveError(AggregationError):
    """Raised when the emergency stop is active, blocking identity operations."""
    pass
