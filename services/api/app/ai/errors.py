"""Normalized exception hierarchy for the AI Model Gateway."""

from typing import Any


class AIGatewayError(Exception):
    """Base exception for all AI Gateway operations."""

    def __init__(
        self,
        message: str,
        error_code: str = "ai_gateway_error",
        retryable: bool = False,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.retryable = retryable
        self.details = details or {}


class ProviderUnavailableError(AIGatewayError):
    """Raised when the target provider service cannot be reached or is offline."""

    def __init__(self, provider_id: str, reason: str = "Provider daemon is unreachable") -> None:
        super().__init__(
            message=f"Provider '{provider_id}' is unavailable: {reason}",
            error_code="provider_unavailable",
            retryable=True,
            details={"provider_id": provider_id, "reason": reason},
        )


class AuthenticationError(AIGatewayError):
    """Raised when provider credentials are invalid or missing."""

    def __init__(self, provider_id: str, reason: str = "Invalid API key or credentials") -> None:
        super().__init__(
            message=f"Authentication failed for provider '{provider_id}': {reason}",
            error_code="authentication_failed",
            retryable=False,
            details={"provider_id": provider_id},
        )


class ModelNotFoundError(AIGatewayError):
    """Raised when the requested model is not found in the provider catalog."""

    def __init__(self, model_id: str, provider_id: str) -> None:
        super().__init__(
            message=f"Model '{model_id}' was not found on provider '{provider_id}'.",
            error_code="model_not_found",
            retryable=False,
            details={"model_id": model_id, "provider_id": provider_id},
        )


class UnsupportedCapabilityError(AIGatewayError):
    """Raised when a requested feature (vision, json schema, tools) is not supported by the model."""

    def __init__(self, model_id: str, capability: str) -> None:
        super().__init__(
            message=f"Model '{model_id}' does not support required capability '{capability}'.",
            error_code="unsupported_capability",
            retryable=False,
            details={"model_id": model_id, "capability": capability},
        )


class ContextLimitExceededError(AIGatewayError):
    """Raised when input prompt + output reservation exceeds model context window."""

    def __init__(self, prompt_tokens: int, context_limit: int, model_id: str) -> None:
        super().__init__(
            message=(
                f"Context limit exceeded for model '{model_id}': "
                f"prompt requires {prompt_tokens} tokens, limit is {context_limit} tokens."
            ),
            error_code="context_limit_exceeded",
            retryable=False,
            details={"prompt_tokens": prompt_tokens, "context_limit": context_limit, "model_id": model_id},
        )


class RateLimitError(AIGatewayError):
    """Raised when provider returns HTTP 429 Too Many Requests."""

    def __init__(self, provider_id: str, retry_after_seconds: float = 5.0) -> None:
        super().__init__(
            message=f"Rate limit exceeded for provider '{provider_id}'. Retry after {retry_after_seconds}s.",
            error_code="rate_limit_exceeded",
            retryable=True,
            details={"provider_id": provider_id, "retry_after_seconds": retry_after_seconds},
        )
        self.retry_after_seconds = retry_after_seconds


class InferenceTimeoutError(AIGatewayError):
    """Raised when inference generation exceeds timeout limit."""

    def __init__(self, timeout_seconds: float, provider_id: str, model_id: str) -> None:
        super().__init__(
            message=f"Inference request timed out after {timeout_seconds}s on {provider_id}:{model_id}.",
            error_code="inference_timeout",
            retryable=True,
            details={"timeout_seconds": timeout_seconds, "provider_id": provider_id, "model_id": model_id},
        )


class GPUMemoryExhaustedError(AIGatewayError):
    """Raised when local VRAM is insufficient to load or run local model."""

    def __init__(self, required_mb: int, available_mb: int, model_id: str) -> None:
        super().__init__(
            message=(
                f"Insufficient VRAM for local model '{model_id}': "
                f"estimated {required_mb} MB needed, only {available_mb} MB available."
            ),
            error_code="gpu_memory_exhausted",
            retryable=False,
            details={"required_mb": required_mb, "available_mb": available_mb, "model_id": model_id},
        )


class InvalidStructuredOutputError(AIGatewayError):
    """Raised when model fails to produce valid structured JSON adhering to the target schema."""

    def __init__(self, raw_output: str, validation_error: str) -> None:
        super().__init__(
            message=f"Model output failed schema validation: {validation_error}",
            error_code="invalid_structured_output",
            retryable=True,
            details={"raw_output": raw_output[:500], "validation_error": validation_error},
        )


class BudgetExceededError(AIGatewayError):
    """Raised when estimated or actual request cost exceeds configured budget."""

    def __init__(self, estimated_cost: float, max_budget: float) -> None:
        super().__init__(
            message=f"Request cost ${estimated_cost:.4f} exceeds budget of ${max_budget:.4f}.",
            error_code="budget_exceeded",
            retryable=False,
            details={"estimated_cost": estimated_cost, "max_budget": max_budget},
        )


class RequestCancelledError(AIGatewayError):
    """Raised when the user or supervisor cancelled the active generation."""

    def __init__(self, request_id: str) -> None:
        super().__init__(
            message=f"Inference request '{request_id}' was cancelled.",
            error_code="request_cancelled",
            retryable=False,
            details={"request_id": request_id},
        )
