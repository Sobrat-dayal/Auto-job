"""OpenAI cloud AI inference provider adapter."""

import json
import logging
import time
from typing import Any, AsyncIterator, Callable

import httpx

from app.ai.budgets import budget_manager
from app.ai.contracts import (
    InferenceChunk,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ModelPricing,
    ProviderHealth,
    TokenUsage,
)
from app.ai.errors import (
    AuthenticationError,
    InferenceTimeoutError,
    ModelNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.ai.providers.base import AIProvider

logger = logging.getLogger("autonom.ai.providers.openai")

STANDARD_OPENAI_MODELS: list[dict[str, Any]] = [
    {
        "id": "gpt-4o",
        "display_name": "GPT-4o (Omni Flagship)",
        "context_window": 128000,
        "max_output_tokens": 16384,
        "capabilities": ["chat", "streaming", "structured_output", "tool_calling", "vision"],
        "pricing": ModelPricing(input_cost_per_million=2.50, output_cost_per_million=10.00),
    },
    {
        "id": "gpt-4o-mini",
        "display_name": "GPT-4o Mini (Fast & Cost-Efficient)",
        "context_window": 128000,
        "max_output_tokens": 16384,
        "capabilities": ["chat", "streaming", "structured_output", "tool_calling", "vision"],
        "pricing": ModelPricing(input_cost_per_million=0.15, output_cost_per_million=0.60),
    },
    {
        "id": "o1-mini",
        "display_name": "o1-mini (Reasoning & Math)",
        "context_window": 128000,
        "max_output_tokens": 65536,
        "capabilities": ["chat", "streaming", "structured_output", "reasoning"],
        "pricing": ModelPricing(input_cost_per_million=3.00, output_cost_per_million=12.00),
    },
]


class OpenAIProvider(AIProvider):
    """Cloud provider adapter for OpenAI and compatible endpoints."""

    def __init__(
        self,
        provider_id: str = "openai",
        display_name: str = "OpenAI",
        base_url: str = "https://api.openai.com/v1",
        api_key_resolver: Callable[[], str | None] | None = None,
    ) -> None:
        super().__init__(provider_id=provider_id, display_name=display_name, provider_type="cloud")
        self.base_url = base_url.rstrip("/")
        self._api_key_resolver = api_key_resolver

    def get_api_key(self) -> str | None:
        """Resolves active API key via injected resolver."""
        if self._api_key_resolver:
            return self._api_key_resolver()
        return None

    def _headers(self) -> dict[str, str]:
        """Constructs headers including Bearer authorization."""
        key = self.get_api_key()
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    def _client(self, timeout: float = 60.0) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, headers=self._headers(), timeout=timeout)

    async def health(self) -> ProviderHealth:
        """Verifies OpenAI endpoint connectivity and credential validity."""
        key = self.get_api_key()
        if not key:
            return ProviderHealth(
                provider_id=self.provider_id,
                is_healthy=False,
                status="auth_required",
                error_message="API key not configured in secure vault",
            )

        start = time.perf_counter()
        try:
            async with self._client(timeout=5.0) as client:
                res = await client.get("/models")
                latency = round((time.perf_counter() - start) * 1000.0, 2)
                if res.status_code == 200:
                    return ProviderHealth(
                        provider_id=self.provider_id,
                        is_healthy=True,
                        status="available",
                        latency_ms=latency,
                    )
                if res.status_code in (401, 403):
                    return ProviderHealth(
                        provider_id=self.provider_id,
                        is_healthy=False,
                        status="auth_required",
                        latency_ms=latency,
                        error_message="Invalid OpenAI API key",
                    )
                return ProviderHealth(
                    provider_id=self.provider_id,
                    is_healthy=False,
                    status="unavailable",
                    latency_ms=latency,
                    error_message=f"HTTP {res.status_code}: {res.text[:100]}",
                )
        except Exception as exc:
            return ProviderHealth(
                provider_id=self.provider_id,
                is_healthy=False,
                status="unavailable",
                latency_ms=None,
                error_message=f"Connection to OpenAI failed: {exc}",
            )

    async def list_models(self) -> list[ModelInfo]:
        """Returns standard recognized models and attempts discovery if key is configured."""
        models: list[ModelInfo] = []
        is_configured = bool(self.get_api_key())

        for m in STANDARD_OPENAI_MODELS:
            models.append(
                ModelInfo(
                    id=f"{self.provider_id}:{m['id']}",
                    provider_id=self.provider_id,
                    model_id=m["id"],
                    display_name=m["display_name"],
                    provider_type="cloud",
                    is_available=is_configured,
                    context_window=m["context_window"],
                    max_output_tokens=m["max_output_tokens"],
                    capabilities=m["capabilities"],
                    pricing=m["pricing"],
                    status_message="Cloud API Available" if is_configured else "Requires API Key",
                )
            )
        return models

    async def get_model(self, model_id: str) -> ModelInfo:
        """Retrieves metadata for specified model."""
        models = await self.list_models()
        for m in models:
            if m.model_id == model_id or m.id == f"{self.provider_id}:{model_id}":
                return m
        # Fallback for dynamic model names
        return ModelInfo(
            id=f"{self.provider_id}:{model_id}",
            provider_id=self.provider_id,
            model_id=model_id,
            display_name=model_id,
            provider_type="cloud",
            is_available=bool(self.get_api_key()),
            context_window=128000,
            max_output_tokens=4096,
            capabilities=["chat", "streaming", "structured_output"],
            pricing=budget_manager.get_pricing(self.provider_id, model_id),
            status_message="Custom Cloud Model",
        )

    def _prepare_payload(self, request: InferenceRequest) -> dict[str, Any]:
        """Prepares standard OpenAI chat completion JSON payload."""
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        for msg in request.messages:
            item = {"role": msg.role, "content": msg.content}
            if msg.name:
                item["name"] = msg.name
            messages.append(item)

        model_name = request.model_preference or "gpt-4o"
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens,
        }

        if request.response_format == "json_object":
            payload["response_format"] = {"type": "json_object"}
        elif request.response_format == "json_schema" and request.json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "result_schema", "schema": request.json_schema, "strict": True},
            }

        return payload

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Executes complete non-streaming chat completion."""
        if not self.get_api_key():
            raise AuthenticationError(self.provider_id, "API key is not configured in secure vault.")

        payload = self._prepare_payload(request)
        payload["stream"] = False

        start_time = time.perf_counter()
        try:
            async with self._client(timeout=request.timeout_seconds) as client:
                res = await client.post("/chat/completions", json=payload)

                if res.status_code in (401, 403):
                    raise AuthenticationError(self.provider_id, f"Invalid API credentials: {res.text}")
                if res.status_code == 404:
                    raise ModelNotFoundError(payload["model"], self.provider_id)
                if res.status_code == 429:
                    raise RateLimitError(self.provider_id)
                if res.status_code != 200:
                    raise ProviderUnavailableError(self.provider_id, f"HTTP {res.status_code}: {res.text}")

                data = res.json()
        except httpx.TimeoutException as exc:
            raise InferenceTimeoutError(request.timeout_seconds, self.provider_id, payload["model"]) from exc
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(self.provider_id, f"Connection failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        choices = data.get("choices", [])
        if not choices:
            raise ProviderUnavailableError(self.provider_id, "No choices returned in OpenAI response.")

        first_choice = choices[0]
        content = first_choice.get("message", {}).get("content", "")
        finish_reason = first_choice.get("finish_reason", "stop")

        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", 0)
        completion_tokens = raw_usage.get("completion_tokens", 0)
        total_tokens = raw_usage.get("total_tokens", prompt_tokens + completion_tokens)

        cost_usd = budget_manager.calculate_cost(self.provider_id, payload["model"], prompt_tokens, completion_tokens)

        structured_data = None
        if request.response_format in ("json_object", "json_schema") and content:
            try:
                structured_data = json.loads(content)
            except Exception:
                pass

        return InferenceResponse(
            request_id=request.request_id,
            provider_id=self.provider_id,
            model_id=payload["model"],
            content=content,
            finish_reason=finish_reason,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                source="reported",
            ),
            estimated_cost_usd=cost_usd,
            latency_ms=latency_ms,
            structured_data=structured_data,
        )

    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceChunk]:
        """Streams chat completion tokens from OpenAI via SSE."""
        if not self.get_api_key():
            raise AuthenticationError(self.provider_id, "API key is not configured in secure vault.")

        payload = self._prepare_payload(request)
        payload["stream"] = True
        payload["stream_options"] = {"include_usage": True}

        try:
            async with self._client(timeout=request.timeout_seconds) as client:
                async with client.stream("POST", "/chat/completions", json=payload) as response:
                    if response.status_code in (401, 403):
                        raise AuthenticationError(self.provider_id, "Invalid API credentials.")
                    if response.status_code == 429:
                        raise RateLimitError(self.provider_id)
                    if response.status_code != 200:
                        body = await response.aread()
                        raise ProviderUnavailableError(
                            self.provider_id, f"HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                        )

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[len("data: ") :].strip()
                        if data_str == "[DONE]":
                            break

                        try:
                            chunk_data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        choices = chunk_data.get("choices", [])
                        delta = ""
                        finish_reason = None
                        if choices:
                            first_choice = choices[0]
                            delta = first_choice.get("delta", {}).get("content", "") or ""
                            finish_reason = first_choice.get("finish_reason")

                        usage = None
                        if "usage" in chunk_data and chunk_data["usage"]:
                            u = chunk_data["usage"]
                            usage = TokenUsage(
                                prompt_tokens=u.get("prompt_tokens", 0),
                                completion_tokens=u.get("completion_tokens", 0),
                                total_tokens=u.get("total_tokens", 0),
                                source="reported",
                            )

                        yield InferenceChunk(
                            request_id=request.request_id,
                            provider_id=self.provider_id,
                            model_id=payload["model"],
                            delta=delta,
                            finish_reason=finish_reason,
                            usage=usage,
                        )
        except httpx.TimeoutException as exc:
            raise InferenceTimeoutError(request.timeout_seconds, self.provider_id, payload["model"]) from exc
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(self.provider_id, f"Streaming connection failed: {exc}") from exc
