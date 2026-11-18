"""Cross-method Observation Coordinator for the Hybrid Computer Engine."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.adapters.registry import InteractionAdapterRegistry, get_adapter_registry
from app.hybrid.contracts import (
    InteractionObservation,
    ObservationRequest,
    SurfaceType,
)
from app.hybrid.routing.router import HybridMethodRouter

logger = logging.getLogger("autonom.hybrid.observations.coordinator")


class ObservationCoordinator:
    """Coordinates normalized observations across DOM, UIA, Win32, and visual captures."""

    def __init__(
        self,
        registry: Optional[InteractionAdapterRegistry] = None,
        router: Optional[HybridMethodRouter] = None,
    ) -> None:
        self.registry = registry or get_adapter_registry()
        self.router = router or HybridMethodRouter(registry=self.registry)

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Capture and normalize observations from the target surface."""
        target = request.target
        method = request.preferred_method

        if method is None:
            # Let router decide method for observation
            method, _ = await self.router.route(target=target, preferred_method=request.preferred_method)

        adapter = self.registry.get(method)
        if not adapter:
            raise KeyError(f"Adapter for method '{method.value}' not found in registry")

        obs = await adapter.observe(request)
        logger.debug("Captured observation %s via %s", obs.observation_id, method.value)
        return obs
