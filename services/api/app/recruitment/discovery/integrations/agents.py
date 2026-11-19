"""Specialist Agent Integration for Job Discovery Engine (Stage 26).

Provides programmatic adapter methods for JobDiscoveryAgent, Supervisor, and Orchestrator.
"""

from typing import Any, Optional

from app.recruitment.discovery.connectors.registry import connector_registry
from app.recruitment.discovery.contracts import (
    DiscoveryTaskCreateRequest,
    ManualImportRequest,
    UrlImportRequest,
)
from app.recruitment.discovery.sources.registry import source_registry
from app.recruitment.discovery.synchronization.coordinator import discovery_coordinator


class JobDiscoveryAgentAdapter:
    """Agent adapter exposing high-level discovery operations to specialist agents."""

    def __init__(self) -> None:
        self.coordinator = discovery_coordinator
        self.sources = source_registry
        self.connectors = connector_registry

    def list_sources(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        """List configured job sources."""
        sources = self.sources.list_sources(enabled_only=enabled_only)
        return [
            {
                "id": s.id,
                "name": s.name,
                "connector_id": s.connector_id.value,
                "category": s.category.value,
                "official_domain": s.official_domain,
                "employer_name": s.employer_name,
                "access_status": s.access_status.value,
                "is_enabled": s.is_enabled,
                "rate_limit_rpm": s.rate_limit_rpm,
            }
            for s in sources
        ]

    async def fetch_source(
        self,
        source_id: str,
        strategy_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Trigger sync for a specific source and return snapshot metrics."""
        snapshot = await self.coordinator.sync_source(source_id=source_id, strategy_id=strategy_id)
        return {
            "snapshot_id": snapshot.id,
            "source_id": snapshot.source_id,
            "completeness": snapshot.completeness.value,
            "total_observed": snapshot.total_observed,
            "new_count": snapshot.new_count,
            "updated_count": snapshot.updated_count,
            "unchanged_count": snapshot.unchanged_count,
            "closed_count": snapshot.closed_count,
            "error_message": snapshot.error_message,
        }

    async def import_url(
        self,
        url: str,
        employer_name: Optional[str] = None,
        target_role: Optional[str] = None,
    ) -> dict[str, Any]:
        """Import a single job URL into the discovery observation pool."""
        req = UrlImportRequest(url=url, employer_name=employer_name, target_role=target_role)
        obs = await self.coordinator.import_from_url(req)
        return {
            "observation_id": obs.id,
            "title": obs.title,
            "employer": obs.employer,
            "url": obs.source_url,
            "prefilter_status": obs.prefilter_status.value,
            "prefilter_reasons": obs.prefilter_reasons,
        }

    def import_manual(
        self,
        title: str,
        employer_name: str,
        description: str,
        source_url: Optional[str] = None,
        location: Optional[str] = None,
        work_arrangement: Optional[str] = None,
        compensation_text: Optional[str] = None,
    ) -> dict[str, Any]:
        """Import a manually entered job posting."""
        req = ManualImportRequest(
            title=title,
            employer_name=employer_name,
            description=description,
            source_url=source_url,
            location=location,
            work_arrangement=work_arrangement,
            compensation_text=compensation_text,
        )
        obs = self.coordinator.import_manual(req)
        return {
            "observation_id": obs.id,
            "title": obs.title,
            "employer": obs.employer,
            "prefilter_status": obs.prefilter_status.value,
            "prefilter_reasons": obs.prefilter_reasons,
        }

    def start_discovery_task(
        self,
        source_ids: list[str],
        strategy_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Queue a background multi-source discovery task."""
        req = DiscoveryTaskCreateRequest(source_ids=source_ids, strategy_id=strategy_id)
        task = self.coordinator.create_task(req)
        self.coordinator.start_task_background(task.id)
        return {
            "task_id": task.id,
            "status": task.status.value,
            "selected_sources": task.selected_sources,
        }

    def get_task_status(self, task_id: str) -> Optional[dict[str, Any]]:
        task = self.coordinator.get_task(task_id)
        if not task:
            return None
        return {
            "task_id": task.id,
            "status": task.status.value,
            "total_postings_found": task.total_postings_found,
            "new_postings_count": task.new_postings_count,
            "errors": task.errors,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
        }

    def get_discovery_summary(self) -> dict[str, Any]:
        stats = self.coordinator.get_overview_stats()
        return stats.model_dump()


# Singleton instance
job_discovery_agent_adapter = JobDiscoveryAgentAdapter()
