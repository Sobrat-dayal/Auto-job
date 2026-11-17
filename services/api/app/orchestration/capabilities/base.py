"""Base capability interface and abstract contract for multi-agent capabilities."""

import abc
from typing import Any

from app.orchestration.contracts import CapabilityDefinition, VerificationPolicy


class BaseCapability(abc.ABC):
    """Abstract base class for all executable agent capabilities."""

    capability_id: str
    name: str
    version: str = "1.0.0"
    description: str
    requires_ai: bool = False
    is_deterministic: bool = True
    default_verification_policy: VerificationPolicy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds: int = 60
    idempotent: bool = True

    @property
    def definition(self) -> CapabilityDefinition:
        """Return the typed capability specification metadata."""
        return CapabilityDefinition(
            capability_id=self.capability_id,
            name=self.name,
            version=self.version,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            requires_ai=self.requires_ai,
            is_deterministic=self.is_deterministic,
            default_verification_policy=self.default_verification_policy,
            timeout_seconds=self.timeout_seconds,
            idempotent=self.idempotent,
        )

    @property
    @abc.abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """JSON schema defining expected input bindings."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def output_schema(self) -> dict[str, Any]:
        """JSON schema defining produced output structure."""
        raise NotImplementedError

    @abc.abstractmethod
    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute the capability against resolved inputs and return typed output dictionary."""
        raise NotImplementedError
