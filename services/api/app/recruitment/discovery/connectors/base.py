"""Abstract Base Class for all Job Source Connectors (Stage 26)."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from app.recruitment.discovery.contracts import (
    ConnectorId,
    ConnectorManifest,
    ExtractedPosting,
    JobSourceConfig,
    SourceValidationResult,
)
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient


class BaseSourceConnector(ABC):
    """Abstract connector protocol implemented by all provider adapters."""

    @property
    @abstractmethod
    def connector_id(self) -> ConnectorId:
        """Unique identifier for this connector."""
        ...

    @property
    @abstractmethod
    def manifest(self) -> ConnectorManifest:
        """Connector capabilities and documentation metadata."""
        ...

    @abstractmethod
    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """Validate that the source endpoint/board exists and is reachable."""
        ...

    @abstractmethod
    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        """Fetch published job postings from this source."""
        ...

    @abstractmethod
    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        """Fetch detailed information for a specific job posting."""
        ...
