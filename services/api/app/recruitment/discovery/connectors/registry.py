"""Connector Registry (Stage 26).

Central registry managing all registered job source connectors and manifests.
"""

from typing import Optional
from app.recruitment.discovery.connectors.ashby import AshbyConnector
from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.connectors.career_page import CareerPageConnector
from app.recruitment.discovery.connectors.greenhouse import GreenhouseConnector
from app.recruitment.discovery.connectors.json_feed import JsonFeedConnector
from app.recruitment.discovery.connectors.lever import LeverConnector
from app.recruitment.discovery.connectors.manual_import import ManualImportConnector
from app.recruitment.discovery.connectors.rss_atom import RssAtomConnector
from app.recruitment.discovery.connectors.url_import import UrlImportConnector
from app.recruitment.discovery.connectors.usajobs import USAJobsConnector
from app.recruitment.discovery.contracts import ConnectorId, ConnectorManifest
from app.recruitment.discovery.errors import ConnectorNotFoundError


class ConnectorRegistry:
    """Registry maintaining active source connector implementations."""

    def __init__(self) -> None:
        self._connectors: dict[ConnectorId, BaseSourceConnector] = {}
        self._register_default_connectors()

    def _register_default_connectors(self) -> None:
        connectors: list[BaseSourceConnector] = [
            GreenhouseConnector(),
            LeverConnector(),
            AshbyConnector(),
            USAJobsConnector(),
            RssAtomConnector(),
            JsonFeedConnector(),
            CareerPageConnector(),
            ManualImportConnector(),
            UrlImportConnector(),
        ]
        for conn in connectors:
            self.register(conn)

    def register(self, connector: BaseSourceConnector) -> None:
        self._connectors[connector.connector_id] = connector

    def get_connector(self, connector_id: ConnectorId | str) -> BaseSourceConnector:
        cid = ConnectorId(connector_id) if isinstance(connector_id, str) else connector_id
        if cid not in self._connectors:
            raise ConnectorNotFoundError(f"No connector registered for ID '{cid}'")
        return self._connectors[cid]

    def list_connectors(self) -> list[BaseSourceConnector]:
        return list(self._connectors.values())

    def list_manifests(self) -> list[ConnectorManifest]:
        return [c.manifest for c in self._connectors.values()]

    def get_manifest(self, connector_id: ConnectorId | str) -> Optional[ConnectorManifest]:
        cid = ConnectorId(connector_id) if isinstance(connector_id, str) else connector_id
        if cid in self._connectors:
            return self._connectors[cid].manifest
        return None


# Global registry singleton
connector_registry = ConnectorRegistry()
