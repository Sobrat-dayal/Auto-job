"""Exceptions for the Stage 19 Hybrid Computer Interaction Engine."""


class HybridError(Exception):
    """Base exception for all hybrid computer interaction errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RoutingError(HybridError):
    """Raised when method routing fails."""
    pass


class NoEligibleMethodError(RoutingError):
    """Raised when no interaction adapter is eligible for the target and action."""
    pass


class TargetResolutionError(HybridError):
    """Raised when target cannot be resolved or mapped to a live surface."""
    pass


class StaleTargetError(HybridError):
    """Raised when a target handle, selector, or bounding box is no longer valid."""
    pass


class FallbackBlockedError(HybridError):
    """Raised when method fallback is forbidden by policy, safety rule, or non-idempotent guard."""
    pass


class FallbackLimitExceededError(HybridError):
    """Raised when maximum fallback depth has been reached to prevent infinite switching loops."""
    pass


class NonIdempotentActionBlockedError(HybridError):
    """Raised when an irreversible or non-idempotent action fails with uncertain outcome and cannot be replayed."""
    pass


class EmergencyStopActiveError(HybridError):
    """Raised when global emergency stop is active and blocks execution."""
    pass


class SessionLockedError(HybridError):
    """Raised when the Windows session is locked or non-interactive."""
    pass
