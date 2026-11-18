"""Method health tracking and latency telemetry for Hybrid Engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.hybrid.contracts import InteractionMethod, MethodHealthStatus


class MethodHealthTracker:
    """Tracks latency, failure rates, and availability state for each interaction method."""

    def __init__(self) -> None:
        self._records: dict[InteractionMethod, MethodHealthStatus] = {
            m: MethodHealthStatus(method=m, status="operational")
            for m in InteractionMethod
        }

    def get_status(self, method: InteractionMethod) -> MethodHealthStatus:
        """Get health record for method."""
        return self._records.get(method, MethodHealthStatus(method=method))

    def list_all(self) -> list[MethodHealthStatus]:
        """List all method health records."""
        return list(self._records.values())

    def record_execution(
        self,
        method: InteractionMethod,
        success: bool,
        latency_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Update metrics following an execution attempt."""
        rec = self._records[method]
        rec.last_used_at = datetime.now(timezone.utc)
        if success:
            rec.success_count += 1
            rec.status = "operational"
        else:
            rec.failure_count += 1
            rec.last_error = error
            if rec.failure_count >= 5 and rec.success_count == 0:
                rec.status = "degraded"

        total = rec.success_count + rec.failure_count
        rec.avg_latency_ms = round(((rec.avg_latency_ms * (total - 1)) + latency_ms) / total, 2)
