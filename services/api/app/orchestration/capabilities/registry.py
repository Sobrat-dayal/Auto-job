"""Central Capability Registry holding all available, typed capabilities."""

import logging
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.capabilities.code_inspect import CodeInspectCapability
from app.orchestration.capabilities.data_transform import DataTransformCapability
from app.orchestration.capabilities.output_validate import OutputValidateCapability
from app.orchestration.capabilities.structured_extract import StructuredExtractCapability
from app.orchestration.capabilities.text_classify import TextClassifyCapability
from app.orchestration.capabilities.text_compare import TextCompareCapability
from app.orchestration.capabilities.text_summarize import TextSummarizeCapability
from app.orchestration.contracts import CapabilityDefinition

logger = logging.getLogger("autonom.orchestration.capabilities.registry")


class CapabilityRegistry:
    """Registry managing available capabilities and coordinating execution."""

    def __init__(self) -> None:
        self._capabilities: dict[str, BaseCapability] = {}
        self._register_default_capabilities()

    def _register_default_capabilities(self) -> None:
        defaults: list[BaseCapability] = [
            TextSummarizeCapability(),
            TextClassifyCapability(),
            StructuredExtractCapability(),
            TextCompareCapability(),
            DataTransformCapability(),
            OutputValidateCapability(),
            CodeInspectCapability(),
        ]
        for cap in defaults:
            self.register(cap)

    def register(self, capability: BaseCapability) -> None:
        """Register a new capability handler."""
        self._capabilities[capability.capability_id] = capability
        logger.debug("Registered capability: %s (v%s)", capability.capability_id, capability.version)

    def get(self, capability_id: str) -> BaseCapability | None:
        """Get capability handler by ID."""
        return self._capabilities.get(capability_id)

    def list_definitions(self) -> list[CapabilityDefinition]:
        """Return list of typed specifications for all registered capabilities."""
        return [cap.definition for cap in self._capabilities.values()]

    def list_ids(self) -> list[str]:
        """Return list of all registered capability IDs."""
        return list(self._capabilities.keys())

    async def execute(
        self,
        capability_id: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a registered capability by ID with input data."""
        handler = self.get(capability_id)
        if not handler:
            raise KeyError(f"Capability '{capability_id}' not found in registry")
        return await handler.execute(input_data, context)


# Global singleton instance
_capability_registry: CapabilityRegistry | None = None


def get_capability_registry() -> CapabilityRegistry:
    """Return shared CapabilityRegistry singleton."""
    global _capability_registry
    if _capability_registry is None:
        _capability_registry = CapabilityRegistry()
    return _capability_registry
