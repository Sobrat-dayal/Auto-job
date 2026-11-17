"""Ollama local AI inference provider adapter."""

import json
import logging
import time
from typing import Any, AsyncIterator

import httpx

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
    InferenceTimeoutError,
    ModelNotFoundError,
    ProviderUnavailableError,
)
from app.ai.providers.base import AIProvider

logger = logging.getLogger("autonom.ai.providers.ollama")


class OllamaProvider(AIProvider):
    """Local inference adapter communicating with the Ollama daemon via REST API."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434", default_keep_alive: str = "5m") -> None:
        super().__init__(provider_id="ollama", display_name="Ollama (Local Engine)", provider_type="local")
        self.base_url = base_url.rstrip("/")
        self.default_keep_alive = default_keep_alive

    def _client(self, timeout: float = 60.0) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def health(self) -> ProviderHealth:
        """Checks if the local Ollama daemon is reachable on loopback."""
        start = time.perf_counter()
        try:
            async with self._client(timeout=3.0) as client:
                res = await client.get("/api/version")
                latency = round((time.perf_counter() - start) * 1000.0, 2)
                if res.status_code == 200:
                    return ProviderHealth(
                        provider_id=self.provider_id,
                        is_healthy=True,
                        status="available",
                        latency_ms=latency,
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
                error_message=f"Ollama daemon not reachable at {self.base_url}: {exc}",
            )

    async def list_models(self) -> list[ModelInfo]:
        """Discovers locally installed models via GET /api/tags."""
        try:
            async with self._client(timeout=5.0) as client:
                res = await client.get("/api/tags")
                if res.status_code != 200:
                    raise ProviderUnavailableError(self.provider_id, f"HTTP {res.status_code}: {res.text}")
                data = res.json()
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(self.provider_id, f"Cannot connect to {self.base_url}: {exc}") from exc

        models: list[ModelInfo] = []
        raw_models = data.get("models", [])

        for rm in raw_models:
            model_name = rm.get("name", "unknown")
            size_bytes = rm.get("size")
            details = rm.get("details", {})
            quantization = details.get("quantization_level")

            capabilities = ["chat", "streaming", "structured_output"]
            if "vision" in model_name.lower() or "llava" in model_name.lower():
                capabilities.append("vision")

            models.append(
                ModelInfo(
                    id=f"ollama:{model_name}",
                    provider_id=self.provider_id,
                    model_id=model_name,
                    display_name=model_name,
                    provider_type="local",
                    is_available=True,
                    context_window=8192,
                    max_output_tokens=4096,
                    capabilities=capabilities,
                    pricing=ModelPricing(input_cost_per_million=0.0, output_cost_per_million=0.0),
                    reported_size_bytes=size_bytes,
                    quantization=quantization,
                    status_message="Installed locally",
                )
            )

        return models

    async def get_model(self, model_id: str) -> ModelInfo:
        """Retrieves details of a local model."""
        models = await self.list_models()
        for m in models:
            if m.model_id == model_id or m.id == f"ollama:{model_id}":
                return m
        raise ModelNotFoundError(model_id, self.provider_id)

    async def list_running_models(self) -> list[str]:
        """Queries running/loaded models via GET /api/ps."""
        try:
            async with self._client(timeout=3.0) as client:
                res = await client.get("/api/ps")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception as exc:
            logger.debug(f"Failed to query /api/ps from Ollama: {exc}")
        return []

    async def load_model(self, model_id: str) -> bool:
        """Pre-loads local model into memory with configured keep_alive."""
        try:
            async with self._client(timeout=120.0) as client:
                res = await client.post(
                    "/api/generate",
                    json={"model": model_id, "prompt": "", "keep_alive": self.default_keep_alive},
                )
                return res.status_code == 200
        except Exception as exc:
            logger.warning(f"Error loading model '{model_id}': {exc}")
            return False

    async def unload_model(self, model_id: str) -> bool:
        """Unloads model by setting keep_alive to 0."""
        try:
            async with self._client(timeout=10.0) as client:
                res = await client.post(
                    "/api/generate",
                    json={"model": model_id, "prompt": "", "keep_alive": 0},
                )
                return res.status_code == 200
        except Exception as exc:
            logger.warning(f"Error unloading model '{model_id}': {exc}")
            return False

    def _prepare_payload(self, request: InferenceRequest) -> dict[str, Any]:
        """Prepares Ollama /api/chat payload."""
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        payload: dict[str, Any] = {
            "model": request.model_preference or "llama3.1:8b",
            "messages": messages,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens,
            },
            "keep_alive": self.default_keep_alive,
        }

        if request.response_format in ("json_object", "json_schema"):
            payload["format"] = "json"

        return payload

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Executes complete non-streaming inference on Ollama."""
        payload = self._prepare_payload(request)
        payload["stream"] = False

        start_time = time.perf_counter()
        try:
            async with self._client(timeout=request.timeout_seconds) as client:
                res = await client.post("/api/chat", json=payload)
                if res.status_code == 404:
                    raise ModelNotFoundError(payload["model"], self.provider_id)
                if res.status_code != 200:
                    raise ProviderUnavailableError(self.provider_id, f"HTTP {res.status_code}: {res.text}")

                data = res.json()
        except httpx.TimeoutException as exc:
            raise InferenceTimeoutError(request.timeout_seconds, self.provider_id, payload["model"]) from exc
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(self.provider_id, f"Connection failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        message_data = data.get("message", {})
        content = message_data.get("content", "")

        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        # Parse structured data if requested
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
            finish_reason="stop",
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                source="reported" if (prompt_tokens or completion_tokens) else "estimated",
            ),
            estimated_cost_usd=0.0,  # Local inference is always $0.00
            latency_ms=latency_ms,
            structured_data=structured_data,
        )

    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceChunk]:
        """Streams tokens from Ollama via /api/chat line-by-line."""
        payload = self._prepare_payload(request)
        payload["stream"] = True

        try:
            async with self._client(timeout=request.timeout_seconds) as client:
                async with client.stream("POST", "/api/chat", json=payload) as response:
                    if response.status_code == 404:
                        raise ModelNotFoundError(payload["model"], self.provider_id)
                    if response.status_code != 200:
                        body = await response.aread()
                        raise ProviderUnavailableError(
                            self.provider_id, f"HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                        )

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk_data = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        delta = chunk_data.get("message", {}).get("content", "")
                        is_done = chunk_data.get("done", False)

                        usage = None
                        if is_done:
                            p_tok = chunk_data.get("prompt_eval_count", 0)
                            c_tok = chunk_data.get("eval_count", 0)
                            usage = TokenUsage(
                                prompt_tokens=p_tok,
                                completion_tokens=c_tok,
                                total_tokens=p_tok + c_tok,
                                source="reported" if (p_tok or c_tok) else "estimated",
                            )

                        yield InferenceChunk(
                            request_id=request.request_id,
                            provider_id=self.provider_id,
                            model_id=payload["model"],
                            delta=delta,
                            finish_reason="stop" if is_done else None,
                            usage=usage,
                        )
        except httpx.TimeoutException as exc:
            raise InferenceTimeoutError(request.timeout_seconds, self.provider_id, payload["model"]) from exc
        except httpx.RequestError as exc:
            raise ProviderUnavailableError(self.provider_id, f"Streaming connection failed: {exc}") from exc
