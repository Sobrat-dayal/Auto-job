"""Configurable OpenAI-compatible provider adapter (LM Studio, vLLM, DeepSeek, LocalAI)."""

from typing import Any, Callable

from app.ai.contracts import ModelInfo, ModelPricing
from app.ai.providers.openai import OpenAIProvider


class OpenAICompatibleProvider(OpenAIProvider):
    """Generic adapter for any service exposing the OpenAI chat completion REST format."""

    def __init__(
        self,
        provider_id: str,
        display_name: str,
        base_url: str,
        provider_type: str = "cloud",
        api_key_resolver: Callable[[], str | None] | None = None,
        custom_models: list[dict[str, Any]] | None = None,
        supports_json_schema: bool = True,
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            display_name=display_name,
            base_url=base_url,
            api_key_resolver=api_key_resolver,
        )
        self.provider_type = provider_type
        self.custom_models = custom_models or []
        self.supports_json_schema = supports_json_schema

    async def list_models(self) -> list[ModelInfo]:
        """Discovers models via GET /models or falls back to configured models."""
        discovered: list[ModelInfo] = []
        try:
            async with self._client(timeout=5.0) as client:
                res = await client.get("/models")
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get("data", []):
                        m_id = item.get("id", "default")
                        discovered.append(
                            ModelInfo(
                                id=f"{self.provider_id}:{m_id}",
                                provider_id=self.provider_id,
                                model_id=m_id,
                                display_name=m_id,
                                provider_type=self.provider_type,  # type: ignore[arg-type]
                                is_available=True,
                                context_window=8192,
                                max_output_tokens=4096,
                                capabilities=["chat", "streaming"]
                                + (["structured_output"] if self.supports_json_schema else []),
                                pricing=ModelPricing(input_cost_per_million=0.0, output_cost_per_million=0.0)
                                if self.provider_type == "local"
                                else ModelPricing(input_cost_per_million=0.50, output_cost_per_million=1.50),
                                status_message="Discovered via /models",
                            )
                        )
                    if discovered:
                        return discovered
        except Exception:
            pass

        # Fallback to configured custom models
        for cm in self.custom_models:
            m_id = cm.get("id", "custom-model")
            discovered.append(
                ModelInfo(
                    id=f"{self.provider_id}:{m_id}",
                    provider_id=self.provider_id,
                    model_id=m_id,
                    display_name=cm.get("display_name", m_id),
                    provider_type=self.provider_type,  # type: ignore[arg-type]
                    is_available=True,
                    context_window=cm.get("context_window", 8192),
                    max_output_tokens=cm.get("max_output_tokens", 4096),
                    capabilities=cm.get("capabilities", ["chat", "streaming"]),
                    pricing=cm.get("pricing", ModelPricing()),
                    status_message="Configured custom model",
                )
            )

        return discovered
