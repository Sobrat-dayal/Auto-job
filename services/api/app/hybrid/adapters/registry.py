"""Registry managing all Hybrid Interaction Adapters."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.adapters.base import BaseInteractionAdapter
from app.hybrid.adapters.browser import BrowserDOMAdapter
from app.hybrid.adapters.uia import WindowsUIAAdapter
from app.hybrid.adapters.visual import VisualAdapter
from app.hybrid.adapters.win32 import Win32Adapter
from app.hybrid.contracts import CapabilityProbe, InteractionMethod, InteractionTarget, MethodHealthStatus

logger = logging.getLogger("autonom.hybrid.adapters.registry")


class InteractionAdapterRegistry:
    """Registry maintaining active computer interaction adapters and telemetry."""

    def __init__(self) -> None:
        self._adapters: dict[InteractionMethod, BaseInteractionAdapter] = {}
        self._health: dict[InteractionMethod, MethodHealthStatus] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """Register the 4 standard computer interaction adapters."""
        self.register(BrowserDOMAdapter())
        self.register(WindowsUIAAdapter())
        self.register(Win32Adapter())
        self.register(VisualAdapter())

    def register(self, adapter: BaseInteractionAdapter) -> None:
        """Register or replace an adapter."""
        self._adapters[adapter.method] = adapter
        if adapter.method not in self._health:
            self._health[adapter.method] = MethodHealthStatus(
                method=adapter.method,
                status="operational",
            )
        logger.debug("Registered hybrid adapter: %s", adapter.method.value)

    def get(self, method: InteractionMethod) -> Optional[BaseInteractionAdapter]:
        """Retrieve an adapter by method identifier."""
        return self._adapters.get(method)

    def list_methods(self) -> list[InteractionMethod]:
        """List registered method IDs."""
        return list(self._adapters.keys())

    def get_health(self, method: InteractionMethod) -> MethodHealthStatus:
        """Get health status record for a method."""
        return self._health.get(
            method,
            MethodHealthStatus(method=method, status="unknown"),
        )

    def list_health(self) -> list[MethodHealthStatus]:
        """List all method health records."""
        return list(self._health.values())

    def record_attempt(
        self,
        method: InteractionMethod,
        success: bool,
        latency_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Update operational telemetry for a method."""
        rec = self._health.get(method)
        if not rec:
            rec = MethodHealthStatus(method=method)
            self._health[method] = rec

        if success:
            rec.success_count += 1
            rec.status = "operational"
        else:
            rec.failure_count += 1
            rec.last_error = error
            if rec.failure_count >= 5 and rec.success_count == 0:
                rec.status = "degraded"

        # Running average latency
        total = rec.success_count + rec.failure_count
        rec.avg_latency_ms = ((rec.avg_latency_ms * (total - 1)) + latency_ms) / total

    async def probe_all(self, target: InteractionTarget) -> dict[InteractionMethod, CapabilityProbe]:
        """Probe all registered adapters against a target concurrently."""
        probes: dict[InteractionMethod, CapabilityProbe] = {}
        for method, adapter in self._adapters.items():
            try:
                probe = await adapter.probe(target)
                probes[method] = probe
            except Exception as exc:
                logger.warning("Adapter %s probe failed: %s", method.value, exc)
                probes[method] = CapabilityProbe(
                    method=method,
                    is_available=False,
                    is_applicable=False,
                    confidence_score=0.0,
                    supported_actions=[],
                    reason=f"Probe exception: {exc}",
                )
        return probes


# Global singleton instance
_adapter_registry: Optional[InteractionAdapterRegistry] = None


def get_adapter_registry() -> InteractionAdapterRegistry:
    """Return shared InteractionAdapterRegistry singleton."""
    global _adapter_registry
    if _adapter_registry is None:
        _adapter_registry = InteractionAdapterRegistry()
    return _adapter_registry
