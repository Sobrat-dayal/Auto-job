"""Job Source Registry and Health Tracker (Stage 26).

Manages discovered and user-configured job sources, tracking configuration,
credentials, availability policies, and health telemetry.
"""

from datetime import UTC, datetime
import logging
from typing import Optional
from uuid import uuid4

from app.recruitment.discovery.contracts import (
    ConnectorId,
    JobSourceConfig,
    JobSourceCreateRequest,
    JobSourceHealth,
    JobSourceUpdateRequest,
    SourceAccessStatus,
    SourceCategory,
)
from app.recruitment.discovery.errors import SourceNotFoundError

logger = logging.getLogger("autonom.recruitment.discovery.sources.registry")


class SourceRegistry:
    """Manages active job sources and their health metrics."""

    def __init__(self) -> None:
        self._sources: dict[str, JobSourceConfig] = {}
        self._health: dict[str, JobSourceHealth] = {}
        self._seed_default_sources()

    def _seed_default_sources(self) -> None:
        seeds = [
            JobSourceConfig(
                id="src_greenhouse_stripe",
                name="Stripe Careers (Greenhouse)",
                connector_id=ConnectorId.GREENHOUSE,
                category=SourceCategory.EMPLOYER_ATS_BOARD,
                official_domain="boards-api.greenhouse.io",
                board_token="stripe",
                employer_name="Stripe",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
                rate_limit_rpm=30,
            ),
            JobSourceConfig(
                id="src_greenhouse_github",
                name="GitHub Careers (Greenhouse)",
                connector_id=ConnectorId.GREENHOUSE,
                category=SourceCategory.EMPLOYER_ATS_BOARD,
                official_domain="boards-api.greenhouse.io",
                board_token="github",
                employer_name="GitHub",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
                rate_limit_rpm=30,
            ),
            JobSourceConfig(
                id="src_lever_netflix",
                name="Netflix Careers (Lever)",
                connector_id=ConnectorId.LEVER,
                category=SourceCategory.EMPLOYER_ATS_BOARD,
                official_domain="api.lever.co",
                board_token="netflix",
                site_id="netflix",
                employer_name="Netflix",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
                rate_limit_rpm=30,
            ),
            JobSourceConfig(
                id="src_ashby_openai",
                name="OpenAI Careers (Ashby)",
                connector_id=ConnectorId.ASHBY,
                category=SourceCategory.EMPLOYER_ATS_BOARD,
                official_domain="api.ashbyhq.com",
                board_token="openai",
                employer_name="OpenAI",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
                rate_limit_rpm=30,
            ),
            JobSourceConfig(
                id="src_usajobs_gov",
                name="USAJOBS (Federal Opportunities)",
                connector_id=ConnectorId.USAJOBS,
                category=SourceCategory.OFFICIAL_PUBLIC_API,
                official_domain="data.usajobs.gov",
                employer_name="US Federal Government",
                access_status=SourceAccessStatus.REQUIRES_CREDENTIALS,
                is_enabled=False,  # disabled by default until user adds credentials
                rate_limit_rpm=20,
            ),
        ]
        for s in seeds:
            self._sources[s.id] = s
            self._health[s.id] = JobSourceHealth(source_id=s.id)

    def list_sources(
        self,
        enabled_only: bool = False,
        category: Optional[SourceCategory] = None,
    ) -> list[JobSourceConfig]:
        sources = list(self._sources.values())
        if enabled_only:
            sources = [s for s in sources if s.is_enabled]
        if category:
            sources = [s for s in sources if s.category == category]
        return sorted(sources, key=lambda x: x.name.lower())

    def get_source(self, source_id: str) -> JobSourceConfig:
        if source_id not in self._sources:
            raise SourceNotFoundError(f"Job source with ID '{source_id}' not found")
        return self._sources[source_id]

    def create_source(self, req: JobSourceCreateRequest) -> JobSourceConfig:
        source_id = f"src_{uuid4().hex[:8]}"
        config = JobSourceConfig(
            id=source_id,
            name=req.name,
            connector_id=req.connector_id,
            category=req.category,
            official_domain=req.official_domain,
            board_token=req.board_token,
            site_id=req.site_id,
            feed_url=req.feed_url,
            employer_name=req.employer_name,
            is_enabled=req.is_enabled,
            rate_limit_rpm=req.rate_limit_rpm,
            custom_headers=req.custom_headers,
            custom_params=req.custom_params,
            access_status=SourceAccessStatus.UNVERIFIED,
        )
        self._sources[source_id] = config
        self._health[source_id] = JobSourceHealth(source_id=source_id)
        return config

    def update_source(self, source_id: str, req: JobSourceUpdateRequest) -> JobSourceConfig:
        src = self.get_source(source_id)
        if req.name is not None:
            src.name = req.name
        if req.board_token is not None:
            src.board_token = req.board_token
        if req.site_id is not None:
            src.site_id = req.site_id
        if req.feed_url is not None:
            src.feed_url = req.feed_url
        if req.employer_name is not None:
            src.employer_name = req.employer_name
        if req.is_enabled is not None:
            src.is_enabled = req.is_enabled
        if req.rate_limit_rpm is not None:
            src.rate_limit_rpm = req.rate_limit_rpm
        if req.custom_headers is not None:
            src.custom_headers = req.custom_headers
        if req.custom_params is not None:
            src.custom_params = req.custom_params

        src.updated_at = datetime.now(UTC).isoformat()
        return src

    def delete_source(self, source_id: str) -> bool:
        if source_id in self._sources:
            del self._sources[source_id]
            self._health.pop(source_id, None)
            return True
        return False

    def get_health(self, source_id: str) -> JobSourceHealth:
        if source_id not in self._health:
            self._health[source_id] = JobSourceHealth(source_id=source_id)
        return self._health[source_id]

    def list_health(self) -> list[JobSourceHealth]:
        return list(self._health.values())

    def record_health(
        self,
        source_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
        retrieved_count: int = 0,
        rate_limited: bool = False,
    ) -> JobSourceHealth:
        now_str = datetime.now(UTC).isoformat()
        health = self.get_health(source_id)
        health.last_checked_at = now_str
        health.response_latency_ms = latency_ms

        if success:
            health.last_successful_fetch = now_str
            health.retrieved_count += retrieved_count
            health.consecutive_failures = 0
            health.current_status = SourceAccessStatus.AVAILABLE_PUBLIC
            health.status_message = "Healthy"
        else:
            health.last_failed_fetch = now_str
            health.error_count += 1
            health.consecutive_failures += 1
            if rate_limited:
                health.rate_limited_count += 1
                health.current_status = SourceAccessStatus.TEMPORARILY_RATE_LIMITED
                health.status_message = error or "Rate limited"
            else:
                health.status_message = error or "Fetch failed"
                if health.consecutive_failures >= 3:
                    health.current_status = SourceAccessStatus.UNAVAILABLE

        return health


# Global singleton instance
source_registry = SourceRegistry()
