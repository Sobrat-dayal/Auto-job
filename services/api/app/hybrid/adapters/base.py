"""Base protocol and abstract class for Hybrid Interaction Adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from app.hybrid.contracts import (
    CapabilityProbe,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    ObservationRequest,
)


@runtime_checkable
class InteractionAdapter(Protocol):
    """Protocol defining the interface for all computer interaction adapters."""

    method: InteractionMethod

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Probe the adapter's applicability and readiness for a given target."""
        ...

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Capture observations from the target surface."""
        ...

    async def execute(self, request: InteractionAction) -> InteractionResult:
        """Execute an action against the target surface."""
        ...

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        """Verify the post-action state of the target."""
        ...


class BaseInteractionAdapter(ABC):
    """Abstract base class with common telemetry and helper routines."""

    def __init__(self, method: InteractionMethod) -> None:
        self.method = method
        self.is_healthy: bool = True
        self.total_invocations: int = 0
        self.failed_invocations: int = 0
        self.last_latency_ms: float = 0.0

    @abstractmethod
    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Probe method capability against the target."""
        pass

    @abstractmethod
    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Extract observation data from the target surface."""
        pass

    @abstractmethod
    async def execute(self, request: InteractionAction) -> InteractionResult:
        """Perform requested action using this method."""
        pass

    @abstractmethod
    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        """Validate whether the action resulted in the expected mutation."""
        pass
