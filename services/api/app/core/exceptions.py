"""Domain and application exceptions for the AUTONOM API service."""

from typing import Any


class AutonomException(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or {}


# --- Task Exceptions ---


class TaskNotFoundError(AutonomException):
    def __init__(self, task_id: str) -> None:
        super().__init__(
            message=f"Task with ID '{task_id}' was not found.",
            code="TASK_NOT_FOUND",
            status_code=404,
            retryable=False,
            details={"task_id": task_id},
        )


class InvalidTaskTransitionError(AutonomException):
    def __init__(self, current_state: str, target_state: str, task_id: str | None = None) -> None:
        super().__init__(
            message=f"Cannot transition task from state '{current_state}' to '{target_state}'.",
            code="INVALID_TASK_TRANSITION",
            status_code=409,
            retryable=False,
            details={
                "current_state": current_state,
                "target_state": target_state,
                "task_id": task_id,
            },
        )


class UnknownTaskTypeError(AutonomException):
    def __init__(self, task_type: str, registered_types: list[str] | None = None) -> None:
        super().__init__(
            message=f"Unknown or unpermitted task type '{task_type}'.",
            code="UNKNOWN_TASK_TYPE",
            status_code=400,
            retryable=False,
            details={"task_type": task_type, "permitted_types": registered_types or []},
        )


class TaskExecutionError(AutonomException):
    def __init__(self, message: str, task_id: str | None = None, retryable: bool = False) -> None:
        super().__init__(
            message=message,
            code="TASK_EXECUTION_FAILED",
            status_code=500,
            retryable=retryable,
            details={"task_id": task_id} if task_id else {},
        )


class TaskTimeoutError(AutonomException):
    def __init__(self, task_id: str, timeout_seconds: float) -> None:
        super().__init__(
            message=f"Task '{task_id}' exceeded execution timeout of {timeout_seconds} seconds.",
            code="TASK_TIMEOUT",
            status_code=504,
            retryable=True,
            details={"task_id": task_id, "timeout_seconds": timeout_seconds},
        )


class TaskCancelledError(AutonomException):
    def __init__(self, task_id: str, reason: str = "Cancellation requested") -> None:
        super().__init__(
            message=f"Task '{task_id}' was cancelled: {reason}.",
            code="TASK_CANCELLED",
            status_code=400,
            retryable=False,
            details={"task_id": task_id, "reason": reason},
        )


# --- Worker & Queue Exceptions ---


class QueueFullError(AutonomException):
    def __init__(self, current_size: int, max_size: int) -> None:
        super().__init__(
            message=f"Task queue is full ({current_size}/{max_size}). Backpressure applied.",
            code="QUEUE_SATURATED",
            status_code=429,
            retryable=True,
            details={"current_size": current_size, "max_size": max_size},
        )


class WorkerCapacityError(AutonomException):
    def __init__(self, active_workers: int, max_workers: int) -> None:
        super().__init__(
            message=f"No worker capacity available ({active_workers}/{max_workers} active).",
            code="WORKER_CAPACITY_EXHAUSTED",
            status_code=503,
            retryable=True,
            details={"active_workers": active_workers, "max_workers": max_workers},
        )


# --- Security & Auth Exceptions ---


class AuthenticationError(AutonomException):
    def __init__(self, message: str = "Missing or invalid authentication credentials.") -> None:
        super().__init__(
            message=message,
            code="UNAUTHENTICATED",
            status_code=401,
            retryable=False,
        )


class AuthorizationError(AutonomException):
    def __init__(self, message: str = "Insufficient permissions for this operation.") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            retryable=False,
        )


# --- Service Exceptions ---


class ServiceUnavailableError(AutonomException):
    def __init__(self, service_name: str, reason: str = "Service is not ready or shutting down") -> None:
        super().__init__(
            message=f"Service '{service_name}' is currently unavailable: {reason}.",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            retryable=True,
            details={"service_name": service_name, "reason": reason},
        )
