"""Domain errors and typed exceptions for Stage 30 Recruitment Monitoring."""

from __future__ import annotations


class MonitoringError(Exception):
    """Base exception for all recruitment monitoring operations."""
    pass


class ProfileNotFoundError(MonitoringError):
    """Raised when a requested monitoring profile is not found."""
    pass


class ProfileValidationError(MonitoringError):
    """Raised when a monitoring profile configuration fails validation."""
    pass


class WatchNotFoundError(MonitoringError):
    """Raised when a requested job watch is not found."""
    pass


class WatchValidationError(MonitoringError):
    """Raised when job watch configuration or schedule fails validation."""
    pass


class WatchRateLimitedError(MonitoringError):
    """Raised when a watch cannot execute due to provider rate limiting cooldown."""
    pass


class ScheduleValidationError(MonitoringError):
    """Raised when a recurrence rule or cron expression is invalid or unbounded."""
    pass


class LeaseConflictError(MonitoringError):
    """Raised when attempting to acquire a task lease already held by another active worker."""
    pass


class QuotaExceededError(MonitoringError):
    """Raised when a provider or global request budget is exceeded."""
    pass


class EmergencyStopActiveError(MonitoringError):
    """Raised when a monitoring run or privileged operation is blocked by Emergency Stop."""
    pass


class AuthorizationExpiredError(MonitoringError):
    """Raised when an active grant for autonomous monitoring has expired or been revoked."""
    pass


class RunNotFoundError(MonitoringError):
    """Raised when a monitoring run is not found."""
    pass


class QueueEntryNotFoundError(MonitoringError):
    """Raised when an opportunity queue entry is not found."""
    pass


class AlertRuleNotFoundError(MonitoringError):
    """Raised when an alert rule is not found."""
    pass


class AlertEventNotFoundError(MonitoringError):
    """Raised when an alert event is not found."""
    pass


class DependencyInvalidationError(MonitoringError):
    """Raised when dependency invalidation or graph resolution fails."""
    pass
