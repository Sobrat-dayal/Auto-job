"""Factory and initialization wiring for the unified AI Gateway."""

import os

from app.ai.gateway import AIGateway
from app.ai.providers.ollama import OllamaProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.ai.registry import ProviderRegistry

# In-memory cached API key storage (populated from DPAPI vault or environment)
_api_keys: dict[str, str] = {}


def set_cached_api_key(provider_id: str, api_key: str | None) -> None:
    """Sets in-memory resolved API key for the provider."""
    if api_key:
        _api_keys[provider_id] = api_key
    else:
        _api_keys.pop(provider_id, None)


def get_cached_api_key(provider_id: str) -> str | None:
    """Retrieves cached API key, checking environment variable fallback."""
    if provider_id in _api_keys:
        return _api_keys[provider_id]
    if provider_id == "openai":
        return os.environ.get("OPENAI_API_KEY")
    return None


_gateway_instance: AIGateway | None = None


def create_ai_gateway(
    ollama_url: str = "http://127.0.0.1:11434",
    openai_base_url: str = "https://api.openai.com/v1",
) -> AIGateway:
    """Instantiates and wires the complete AI Model Gateway and default provider adapters."""
    registry = ProviderRegistry()

    # 1. Register Ollama local engine adapter
    ollama_provider = OllamaProvider(base_url=ollama_url)
    registry.register(ollama_provider)

    # 2. Register OpenAI cloud adapter
    openai_provider = OpenAIProvider(
        provider_id="openai",
        display_name="OpenAI",
        base_url=openai_base_url,
        api_key_resolver=lambda: get_cached_api_key("openai"),
    )
    registry.register(openai_provider)

    # 3. Register generic OpenAI-compatible custom adapter
    custom_provider = OpenAICompatibleProvider(
        provider_id="custom",
        display_name="Custom OpenAI-Compatible",
        base_url="http://127.0.0.1:8000/v1",
        provider_type="local",
        api_key_resolver=lambda: get_cached_api_key("custom"),
    )
    registry.register(custom_provider)

    return AIGateway(registry=registry)


def get_ai_gateway() -> AIGateway:
    """Returns global shared AIGateway singleton instance."""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = create_ai_gateway()
    return _gateway_instance


def reset_ai_gateway() -> AIGateway:
    """Resets global gateway singleton (for testing)."""
    global _gateway_instance
    _gateway_instance = create_ai_gateway()
    return _gateway_instance
