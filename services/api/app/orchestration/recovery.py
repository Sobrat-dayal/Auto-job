"""Recovery Agent classifying runtime failures, coordinating bounded retries, and proposing replanning."""

import logging
from typing import Any

from app.ai.errors import (
    ContextLimitExceededError,
    GPUMemoryExhaustedError,
    InferenceTimeoutError,
    InvalidStructuredOutputError,
    ModelNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.orchestration.contracts import (
    FailureCategory,
    RecoveryAction,
    WorkflowStepDefinition,
)

logger = logging.getLogger("autonom.orchestration.recovery")


class RecoveryAgent:
    """Agent diagnosing failure categories and deciding remediation actions (retry, fallback, replan, fail)."""

    def __init__(self) -> None:
        self.agent_id = "recovery"
        self.name = "Recovery Agent"

    def classify_failure(self, error: Exception | str) -> FailureCategory:
        """Classify an exception or error message into one of 13 normalized failure categories."""
        if isinstance(error, Exception):
            if isinstance(error, ProviderUnavailableError):
                return FailureCategory.PROVIDER_UNAVAILABLE
            if isinstance(error, ModelNotFoundError):
                return FailureCategory.MODEL_UNAVAILABLE
            if isinstance(error, (TimeoutError, InferenceTimeoutError)):
                return FailureCategory.TIMEOUT
            if isinstance(error, RateLimitError):
                return FailureCategory.RATE_LIMIT
            if isinstance(error, InvalidStructuredOutputError):
                return FailureCategory.INVALID_OUTPUT
            if isinstance(error, (GPUMemoryExhaustedError, MemoryError)):
                return FailureCategory.RESOURCE_EXHAUSTED
            if isinstance(error, KeyError) and "capability" in str(error).lower():
                return FailureCategory.MISSING_CAPABILITY

        msg = str(error).lower()
        if "timeout" in msg or "timed out" in msg:
            return FailureCategory.TIMEOUT
        if "rate limit" in msg or "429" in msg or "too many requests" in msg:
            return FailureCategory.RATE_LIMIT
        if "provider" in msg or "connection refused" in msg or "unreachable" in msg:
            return FailureCategory.PROVIDER_UNAVAILABLE
        if "model" in msg and ("not found" in msg or "unavailable" in msg):
            return FailureCategory.MODEL_UNAVAILABLE
        if "verification" in msg or "validation failed" in msg:
            return FailureCategory.FAILED_VERIFICATION
        if "capability" in msg and ("not found" in msg or "missing" in msg):
            return FailureCategory.MISSING_CAPABILITY
        if "gpu" in msg or "vram" in msg or "out of memory" in msg or "cuda" in msg:
            return FailureCategory.RESOURCE_EXHAUSTED
        if "authorization" in msg or "permission denied" in msg:
            return FailureCategory.AUTHORIZATION_REQUIRED
        if "dependency" in msg or "upstream" in msg:
            return FailureCategory.DEPENDENCY_FAILURE
        if "cancel" in msg:
            return FailureCategory.CANCELLED_BY_USER
        if "interrupted" in msg or "shutdown" in msg:
            return FailureCategory.BACKEND_INTERRUPTION

        return FailureCategory.UNKNOWN_EXTERNAL_OUTCOME

    def decide_recovery_action(
        self,
        step: WorkflowStepDefinition,
        error: Exception | str,
        current_retry: int,
        replan_count: int = 0,
        max_replans: int = 2,
    ) -> RecoveryAction:
        """Determine whether to retry, switch model, trigger replan, or fail."""
        category = self.classify_failure(error)
        step_id = step.step_id
        max_retries = getattr(step, "max_retries", 2)
        safe_to_retry = getattr(step, "idempotent", True)

        # 1. Non-retryable errors
        if category == FailureCategory.AUTHORIZATION_REQUIRED:
            return RecoveryAction(
                action="wait_authorization",
                failure_category=category,
                reason="User authorization required before proceeding.",
                step_id=step_id,
                attempt_number=current_retry + 1,
                safe_to_retry=False,
            )

        if category == FailureCategory.CANCELLED_BY_USER:
            return RecoveryAction(
                action="fail",
                failure_category=category,
                reason="Cancelled by user.",
                step_id=step_id,
                attempt_number=current_retry,
                safe_to_retry=False,
            )

        # 2. Bounded retries
        if current_retry < max_retries and safe_to_retry:
            if category in (
                FailureCategory.TIMEOUT,
                FailureCategory.RATE_LIMIT,
                FailureCategory.RESOURCE_EXHAUSTED,
                FailureCategory.INVALID_OUTPUT,
            ):
                return RecoveryAction(
                    action="retry",
                    failure_category=category,
                    reason=f"Transient failure ({category.value}); retry {current_retry + 1}/{max_retries}.",
                    step_id=step_id,
                    attempt_number=current_retry + 1,
                    safe_to_retry=True,
                )

        # 3. Model unavailable / Provider unavailable -> propose alternate model
        if category in (FailureCategory.PROVIDER_UNAVAILABLE, FailureCategory.MODEL_UNAVAILABLE):
            if current_retry < max_retries:
                return RecoveryAction(
                    action="alternate_model",
                    failure_category=category,
                    reason="Target provider/model unavailable; attempting fallback route.",
                    step_id=step_id,
                    attempt_number=current_retry + 1,
                    safe_to_retry=True,
                )

        # 4. Replanning if retries exhausted and within replan budget
        if replan_count < max_replans and category in (
            FailureCategory.FAILED_VERIFICATION,
            FailureCategory.MISSING_CAPABILITY,
            FailureCategory.DEPENDENCY_FAILURE,
            FailureCategory.INVALID_OUTPUT,
            FailureCategory.TIMEOUT,
        ):
            return RecoveryAction(
                action="replan",
                failure_category=category,
                reason=f"Step '{step_id}' failed after {current_retry} retries; triggering dynamic plan revision.",
                step_id=step_id,
                attempt_number=current_retry + 1,
                safe_to_retry=False,
            )

        # 5. Terminal failure
        return RecoveryAction(
            action="fail",
            failure_category=category,
            reason=f"Unrecoverable failure or retry budget exhausted: {error}",
            step_id=step_id,
            attempt_number=current_retry,
            safe_to_retry=False,
        )
