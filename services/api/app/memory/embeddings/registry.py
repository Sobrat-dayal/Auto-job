"""Registry managing embedding models, privacy classification, and dimension constraints."""

import logging
from typing import Optional

from app.memory.contracts import SensitivityCategory
from app.memory.embeddings.provider import (
    BaseEmbeddingProvider,
    DeterministicLocalEmbeddingEngine,
    OllamaEmbeddingProvider,
)

logger = logging.getLogger("autonom.memory.embeddings.registry")


class EmbeddingModelMetadata:
    """Metadata describing an embedding model's properties."""

    def __init__(
        self,
        model_id: str,
        display_name: str,
        provider_type: str,  # local, ollama, cloud
        dimension: int,
        max_tokens: int = 512,
        requires_network: bool = False,
    ) -> None:
        self.model_id = model_id
        self.display_name = display_name
        self.provider_type = provider_type
        self.dimension = dimension
        self.max_tokens = max_tokens
        self.requires_network = requires_network


class EmbeddingRegistry:
    """Registry coordinating active embedding providers and privacy guards."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseEmbeddingProvider] = {}
        self._metadata: dict[str, EmbeddingModelMetadata] = {}

        # 1. Register default local engine
        local_engine = DeterministicLocalEmbeddingEngine(dimension=384, model_id="local-minilm-l6")
        self.register_provider(
            local_engine,
            EmbeddingModelMetadata(
                model_id="local-minilm-l6",
                display_name="Local MiniLM-L6 (Fast Deterministic)",
                provider_type="local",
                dimension=384,
                requires_network=False,
            ),
        )

        # 2. Register Ollama provider with local fallback
        ollama_provider = OllamaEmbeddingProvider(
            model_id="nomic-embed-text",
            fallback_engine=local_engine,
        )
        self.register_provider(
            ollama_provider,
            EmbeddingModelMetadata(
                model_id="nomic-embed-text",
                display_name="Ollama Nomic Embed Text",
                provider_type="ollama",
                dimension=384,
                requires_network=False,
            ),
        )

        self._active_model_id = "local-minilm-l6"

    def register_provider(self, provider: BaseEmbeddingProvider, metadata: EmbeddingModelMetadata) -> None:
        self._providers[metadata.model_id] = provider
        self._metadata[metadata.model_id] = metadata

    def get_active_provider(self) -> BaseEmbeddingProvider:
        return self._providers.get(self._active_model_id) or self._providers["local-minilm-l6"]

    def set_active_model(self, model_id: str) -> bool:
        if model_id in self._providers:
            self._active_model_id = model_id
            return True
        return False

    def get_metadata(self, model_id: Optional[str] = None) -> Optional[EmbeddingModelMetadata]:
        target = model_id or self._active_model_id
        return self._metadata.get(target)

    def validate_egress(self, sensitivity: SensitivityCategory, model_id: Optional[str] = None) -> bool:
        """Verifies if a memory of given sensitivity is permitted to use the specified embedding model.

        Cloud providers are prohibited for PERSONAL, SENSITIVE, RESTRICTED, or SECRET data.
        """
        meta = self.get_metadata(model_id)
        if not meta:
            return True
        if meta.requires_network and sensitivity in (
            SensitivityCategory.PERSONAL,
            SensitivityCategory.SENSITIVE,
            SensitivityCategory.RESTRICTED,
            SensitivityCategory.SECRET,
        ):
            logger.warning(
                f"Data egress blocked: cannot use network-dependent model '{meta.model_id}' "
                f"for sensitivity '{sensitivity}'"
            )
            return False
        return True


# Global singleton registry
embedding_registry = EmbeddingRegistry()
