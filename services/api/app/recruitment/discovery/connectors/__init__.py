"""Connectors package re-exports (Stage 26)."""

from app.recruitment.discovery.connectors.ashby import AshbyConnector
from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.connectors.career_page import CareerPageConnector
from app.recruitment.discovery.connectors.greenhouse import GreenhouseConnector
from app.recruitment.discovery.connectors.json_feed import JsonFeedConnector
from app.recruitment.discovery.connectors.lever import LeverConnector
from app.recruitment.discovery.connectors.manual_import import ManualImportConnector
from app.recruitment.discovery.connectors.registry import ConnectorRegistry, connector_registry
from app.recruitment.discovery.connectors.rss_atom import RssAtomConnector
from app.recruitment.discovery.connectors.url_import import UrlImportConnector
from app.recruitment.discovery.connectors.usajobs import USAJobsConnector

__all__ = [
    "BaseSourceConnector",
    "AshbyConnector",
    "CareerPageConnector",
    "GreenhouseConnector",
    "JsonFeedConnector",
    "LeverConnector",
    "ManualImportConnector",
    "RssAtomConnector",
    "UrlImportConnector",
    "USAJobsConnector",
    "ConnectorRegistry",
    "connector_registry",
]
