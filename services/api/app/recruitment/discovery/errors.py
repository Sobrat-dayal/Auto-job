"""Domain exceptions for Multi-Source Job Discovery Engine (Stage 26)."""

from typing import Optional


class JobDiscoveryError(Exception):
    """Base exception for all job discovery operations."""

    def __init__(self, message: str, code: str = "DISCOVERY_ERROR", details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class SourceNotFoundError(JobDiscoveryError):
    def __init__(self, source_id: str) -> None:
        super().__init__(
            f"Job source with ID '{source_id}' was not found.",
            code="SOURCE_NOT_FOUND",
            details={"source_id": source_id},
        )


class ConnectorNotFoundError(JobDiscoveryError):
    def __init__(self, connector_id: str) -> None:
        super().__init__(
            f"Connector with ID '{connector_id}' is not registered.",
            code="CONNECTOR_NOT_FOUND",
            details={"connector_id": connector_id},
        )


class SourceAccessRestrictedError(JobDiscoveryError):
    def __init__(self, source_id: str, reason: str) -> None:
        super().__init__(
            f"Access to job source '{source_id}' is restricted: {reason}",
            code="SOURCE_ACCESS_RESTRICTED",
            details={"source_id": source_id, "reason": reason},
        )


class InvalidSourceConfigError(JobDiscoveryError):
    def __init__(self, source_id: str, message: str) -> None:
        super().__init__(
            f"Invalid configuration for source '{source_id}': {message}",
            code="INVALID_SOURCE_CONFIG",
            details={"source_id": source_id, "message": message},
        )


class RateLimitExceededError(JobDiscoveryError):
    def __init__(self, source_id: str, retry_after_seconds: Optional[int] = None) -> None:
        super().__init__(
            f"Rate limit exceeded for source '{source_id}'. Retry after {retry_after_seconds or 60}s.",
            code="RATE_LIMIT_EXCEEDED",
            details={"source_id": source_id, "retry_after_seconds": retry_after_seconds},
        )


class SSRFSecurityError(JobDiscoveryError):
    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            f"SSRF security violation for URL '{url}': {reason}",
            code="SSRF_SECURITY_VIOLATION",
            details={"url": url, "reason": reason},
        )


class ExtractionFailedError(JobDiscoveryError):
    def __init__(self, source_id: str, message: str) -> None:
        super().__init__(
            f"Extraction failed for source '{source_id}': {message}",
            code="EXTRACTION_FAILED",
            details={"source_id": source_id, "message": message},
        )


class TaskCancelledError(JobDiscoveryError):
    def __init__(self, task_id: str) -> None:
        super().__init__(
            f"Discovery task '{task_id}' was cancelled.",
            code="TASK_CANCELLED",
            details={"task_id": task_id},
        )


class PartialSnapshotError(JobDiscoveryError):
    def __init__(self, source_id: str, message: str) -> None:
        super().__init__(
            f"Partial snapshot warning for source '{source_id}': {message}",
            code="PARTIAL_SNAPSHOT",
            details={"source_id": source_id, "message": message},
        )
