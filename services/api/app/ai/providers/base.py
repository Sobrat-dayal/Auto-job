"""Base protocol and abstract class for AI inference provider adapters."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.ai.contracts import (
    InferenceChunk,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)


class AIProvider(ABC):
    """Abstract base class for all AI inference providers."""

    def __init__(self, provider_id: str, display_name: str, provider_type: str = "cloud") -> None:
        self.provider_id = provider_id
        self.display_name = display_name
        self.provider_type = provider_type  # "local" or "cloud"

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Performs a real connectivity and availability check against the provider."""

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Discovers and returns available models from the provider."""

    @abstractmethod
    async def get_model(self, model_id: str) -> ModelInfo:
        """Retrieves metadata for a specific model ID."""

    @abstractmethod
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Executes complete non-streaming inference and returns normalized response."""

    @abstractmethod
    async def stream(self, request: InferenceRequest) -> AsyncIterator[InferenceChunk]:
        """Executes inference and yields incremental normalized token chunks."""

    async def load_model(self, model_id: str) -> bool:
        """Optional model pre-loading (primarily for local providers like Ollama)."""
        return True

    async def unload_model(self, model_id: str) -> bool:
        """Optional model unloading to free VRAM (primarily for local providers)."""
        return True

    def supports_capability(self, model_id: str, capability: str) -> bool:
        """Checks if the provider/model supports a specific capability."""
        return True
