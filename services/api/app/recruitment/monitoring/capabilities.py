"""Internal Agent Capabilities for Stage 30 Recruitment Monitoring."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.monitoring.contracts import (
    JobWatchCreateRequest,
    OpportunityQueueUpdateRequest,
)
from app.recruitment.monitoring.service import recruitment_monitoring_service

logger = logging.getLogger("autonom.recruitment.monitoring.capabilities")


class MonitoringCapabilities:
    """Registers agent capabilities under recruitment.monitoring.*."""

    @staticmethod
    async def list_watches(owner_id: str, profile_id: str | None = None) -> list[dict[str, Any]]:
        watches = await recruitment_monitoring_service.list_watches(owner_id=owner_id, profile_id=profile_id)
        return [w.model_dump(mode="json") for w in watches]

    @staticmethod
    async def create_watch(owner_id: str, data: dict[str, Any]) -> dict[str, Any]:
        req = JobWatchCreateRequest(**data)
        watch = await recruitment_monitoring_service.create_watch(owner_id=owner_id, req=req)
        return watch.model_dump(mode="json")

    @staticmethod
    async def validate_watch(watch_id: str) -> dict[str, Any]:
        return await recruitment_monitoring_service.validate_watch(watch_id=watch_id)

    @staticmethod
    async def get_schedule(watch_id: str) -> dict[str, Any]:
        preview = await recruitment_monitoring_service.preview_schedule(watch_id=watch_id)
        return preview.model_dump(mode="json")

    @staticmethod
    async def start_run(watch_id: str, worker_id: str = "agent-worker") -> dict[str, Any]:
        run = await recruitment_monitoring_service.run_now(watch_id=watch_id, worker_id=worker_id)
        return run.model_dump(mode="json")

    @staticmethod
    async def get_run(run_id: str) -> dict[str, Any]:
        run = await recruitment_monitoring_service.get_run(run_id=run_id)
        return run.model_dump(mode="json")

    @staticmethod
    async def pause_watch(watch_id: str) -> dict[str, Any]:
        watch = await recruitment_monitoring_service.pause_watch(watch_id=watch_id)
        return watch.model_dump(mode="json")

    @staticmethod
    async def resume_watch(watch_id: str) -> dict[str, Any]:
        watch = await recruitment_monitoring_service.resume_watch(watch_id=watch_id)
        return watch.model_dump(mode="json")

    @staticmethod
    async def get_changes(canonical_job_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        changes = await recruitment_monitoring_service.list_job_changes(canonical_job_id=canonical_job_id, limit=limit)
        return [c.model_dump(mode="json") for c in changes]

    @staticmethod
    async def get_opportunities(
        applicant_profile_id: str,
        priority: str | None = None,
        queue_status: str | None = None,
    ) -> list[dict[str, Any]]:
        opps = await recruitment_monitoring_service.list_opportunities(
            applicant_profile_id=applicant_profile_id,
            priority=priority,
            queue_status=queue_status,
        )
        return [o.model_dump(mode="json") for o in opps]

    @staticmethod
    async def get_alerts(owner_id: str, unread_only: bool = False) -> list[dict[str, Any]]:
        alerts = await recruitment_monitoring_service.list_alerts(owner_id=owner_id, unread_only=unread_only)
        return [a.model_dump(mode="json") for a in alerts]

    @staticmethod
    def get_source_health() -> list[dict[str, Any]]:
        health = recruitment_monitoring_service.list_source_health()
        return [h.model_dump(mode="json") for h in health]

    @staticmethod
    async def get_worker_health() -> list[dict[str, Any]]:
        health = await recruitment_monitoring_service.list_worker_health()
        return [h.model_dump(mode="json") for h in health]

    @staticmethod
    async def get_diagnostics(timezone: str = "UTC") -> dict[str, Any]:
        diag = await recruitment_monitoring_service.get_diagnostics(timezone=timezone)
        return diag.model_dump(mode="json")


monitoring_capabilities = MonitoringCapabilities()
