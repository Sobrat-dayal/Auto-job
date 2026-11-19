"""Master Job Discovery Service (Stage 26).

Central orchestrator for Multi-Source Job Discovery, official API connectors,
source registration, incremental fetching, change detection, and agent integration.
"""

from typing import Any, Optional

from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.connectors.registry import ConnectorRegistry, connector_registry
from app.recruitment.discovery.contracts import (
    ConnectorId,
    ConnectorManifest,
    DiscoveryOverviewStats,
    DiscoverySettingsConfig,
    DiscoveryTaskCreateRequest,
    DiscoveryTaskRecord,
    EmployerCareerPageCreateRequest,
    EmployerCareerSource,
    JobSourceConfig,
    JobSourceCreateRequest,
    JobSourceHealth,
    JobSourceObservation,
    JobSourceSnapshot,
    JobSourceUpdateRequest,
    ManualImportRequest,
    PostingAvailability,
    PrefilterOutcome,
    SourceValidationResult,
    UrlImportRequest,
)
from app.recruitment.discovery.integrations.agents import (
    JobDiscoveryAgentAdapter,
    job_discovery_agent_adapter,
)
from app.recruitment.discovery.sources.employer_sources import (
    EmployerSourceManager,
    employer_source_manager,
)
from app.recruitment.discovery.sources.registry import SourceRegistry, source_registry
from app.recruitment.discovery.synchronization.coordinator import (
    DiscoveryCoordinator,
    discovery_coordinator,
)


class JobDiscoveryService:
    """Master facade for recruitment job discovery engine."""

    def __init__(
        self,
        connectors: Optional[ConnectorRegistry] = None,
        sources: Optional[SourceRegistry] = None,
        employers: Optional[EmployerSourceManager] = None,
        coordinator: Optional[DiscoveryCoordinator] = None,
        agent_adapter: Optional[JobDiscoveryAgentAdapter] = None,
    ) -> None:
        self.connectors = connectors or connector_registry
        self.sources = sources or source_registry
        self.employers = employers or employer_source_manager
        self.coordinator = coordinator or discovery_coordinator
        self.agent_adapter = agent_adapter or job_discovery_agent_adapter

    # -------------------------------------------------------------------------
    # Connectors & Manifests
    # -------------------------------------------------------------------------
    def list_connectors(self) -> list[ConnectorManifest]:
        return self.connectors.list_manifests()

    def get_connector_manifest(self, connector_id: ConnectorId | str) -> Optional[ConnectorManifest]:
        return self.connectors.get_manifest(connector_id)

    # -------------------------------------------------------------------------
    # Sources Management
    # -------------------------------------------------------------------------
    def list_sources(self, enabled_only: bool = False) -> list[JobSourceConfig]:
        return self.sources.list_sources(enabled_only=enabled_only)

    def get_source(self, source_id: str) -> JobSourceConfig:
        return self.sources.get_source(source_id)

    def create_source(self, req: JobSourceCreateRequest) -> JobSourceConfig:
        return self.sources.create_source(req)

    def update_source(self, source_id: str, req: JobSourceUpdateRequest) -> JobSourceConfig:
        return self.sources.update_source(source_id, req)

    def delete_source(self, source_id: str) -> bool:
        return self.sources.delete_source(source_id)

    def get_source_health(self, source_id: str) -> JobSourceHealth:
        return self.sources.get_health(source_id)

    def list_all_health(self) -> list[JobSourceHealth]:
        return self.sources.list_health()

    async def validate_source(self, source_id: str) -> SourceValidationResult:
        src = self.get_source(source_id)
        conn = self.connectors.get_connector(src.connector_id)
        result = await conn.validate_source(src, self.coordinator.http_client)
        src.access_status = result.access_status
        return result

    async def refresh_source(self, source_id: str) -> JobSourceSnapshot:
        return await self.coordinator.sync_source(source_id=source_id)

    # -------------------------------------------------------------------------
    # Employer Career Sources
    # -------------------------------------------------------------------------
    def list_employer_sources(self, enabled_only: bool = False) -> list[EmployerCareerSource]:
        return self.employers.list_employers(enabled_only=enabled_only)

    def add_employer_source(self, req: EmployerCareerPageCreateRequest) -> EmployerCareerSource:
        return self.employers.add_employer(req)

    def get_employer_source(self, employer_id: str) -> Optional[EmployerCareerSource]:
        return self.employers.get_employer(employer_id)

    def delete_employer_source(self, employer_id: str) -> bool:
        return self.employers.delete_employer(employer_id)

    # -------------------------------------------------------------------------
    # Import
    # -------------------------------------------------------------------------
    async def import_url(self, req: UrlImportRequest) -> JobSourceObservation:
        return await self.coordinator.import_from_url(req)

    def import_manual(self, req: ManualImportRequest) -> JobSourceObservation:
        return self.coordinator.import_manual(req)

    # -------------------------------------------------------------------------
    # Observations & Postings
    # -------------------------------------------------------------------------
    def list_observations(
        self,
        source_id: Optional[str] = None,
        availability: Optional[PostingAvailability] = None,
        prefilter: Optional[PrefilterOutcome] = None,
        query: Optional[str] = None,
        limit: int = 100,
    ) -> list[JobSourceObservation]:
        return self.coordinator.list_observations(
            source_id=source_id,
            availability=availability,
            prefilter=prefilter,
            query=query,
            limit=limit,
        )

    def get_observation(self, observation_id: str) -> Optional[JobSourceObservation]:
        return self.coordinator.get_observation(observation_id)

    # -------------------------------------------------------------------------
    # Tasks
    # -------------------------------------------------------------------------
    def create_task(self, req: DiscoveryTaskCreateRequest) -> DiscoveryTaskRecord:
        task = self.coordinator.create_task(req)
        self.coordinator.start_task_background(task.id)
        return task

    def get_task(self, task_id: str) -> Optional[DiscoveryTaskRecord]:
        return self.coordinator.get_task(task_id)

    def list_tasks(self, limit: int = 50) -> list[DiscoveryTaskRecord]:
        return self.coordinator.list_tasks(limit=limit)

    def cancel_task(self, task_id: str) -> bool:
        return self.coordinator.cancel_task(task_id)

    # -------------------------------------------------------------------------
    # Diagnostics & Settings
    # -------------------------------------------------------------------------
    def get_overview_stats(self) -> DiscoveryOverviewStats:
        return self.coordinator.get_overview_stats()

    def get_settings(self) -> DiscoverySettingsConfig:
        return self.coordinator.get_settings()

    def update_settings(self, settings: DiscoverySettingsConfig) -> DiscoverySettingsConfig:
        return self.coordinator.update_settings(settings)


# Global singleton instance
job_discovery_service = JobDiscoveryService()
