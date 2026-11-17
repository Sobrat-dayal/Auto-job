"""Central registry managing registered providers and discovered model metadata."""

import asyncio
import logging
from typing import Any

from app.ai.contracts import ModelInfo, ProviderHealth
from app.ai.errors import ProviderUnavailableError
from app.ai.providers.base import AIProvider

logger = logging.getLogger("autonom.ai.registry")


class ProviderRegistry:
    """Registry coordinating multiple AI providers and unified model discovery."""

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._cached_models: dict[str, ModelInfo] = {}  # key: "provider_id:model_id"
        self._cached_health: dict[str, ProviderHealth] = {}

    def register(self, provider: AIProvider) -> None:
        """Registers a new AI provider adapter."""
        self._providers[provider.provider_id] = provider
        logger.info(f"Registered AI Provider: '{provider.provider_id}' ({provider.display_name})")

    def register_model(self, model: ModelInfo) -> None:
        """Registers a model explicitly into the cache."""
        self._cached_models[model.id] = model

    def get(self, provider_id: str) -> AIProvider:
        """Retrieves an existing registered provider."""
        provider = self._providers.get(provider_id)
        if not provider:
            raise ProviderUnavailableError(provider_id, f"Provider '{provider_id}' is not registered.")
        return provider

    def list_providers(self) -> list[dict[str, Any]]:
        """Returns safe summary list of registered providers."""
        summaries = []
        for p_id, p in self._providers.items():
            health = self._cached_health.get(p_id)
            summaries.append(
                {
                    "provider_id": p.provider_id,
                    "display_name": p.display_name,
                    "provider_type": p.provider_type,
                    "is_healthy": health.is_healthy if health else False,
                    "status": health.status if health else "unknown",
                    "latency_ms": health.latency_ms if health else None,
                }
            )
        return summaries

    async def check_all_health(self) -> dict[str, ProviderHealth]:
        """Runs health checks concurrently across all registered providers."""
        tasks = [p.health() for p in self._providers.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for p_id, res in zip(self._providers.keys(), results):
            if isinstance(res, ProviderHealth):
                self._cached_health[p_id] = res
            else:
                self._cached_health[p_id] = ProviderHealth(
                    provider_id=p_id,
                    is_healthy=False,
                    status="unavailable",
                    error_message=str(res),
                )
        return dict(self._cached_health)

    async def discover_all_models(self) -> list[ModelInfo]:
        """Discovers models across all registered providers and refreshes registry cache."""
        all_models: list[ModelInfo] = []
        for p_id, provider in self._providers.items():
            try:
                models = await provider.list_models()
                for m in models:
                    self._cached_models[m.id] = m
                    all_models.append(m)
            except Exception as exc:
                logger.warning(f"Error discovering models from provider '{p_id}': {exc}")

        return all_models

    def list_models(self, provider_id: str | None = None) -> list[ModelInfo]:
        """Returns list of cached discovered models."""
        if provider_id:
            return [m for m in self._cached_models.values() if m.provider_id == provider_id]
        return list(self._cached_models.values())

    def get_model(self, provider_id: str, model_id: str) -> ModelInfo | None:
        """Retrieves model by provider and model ID."""
        key = f"{provider_id}:{model_id}"
        return self._cached_models.get(key)
