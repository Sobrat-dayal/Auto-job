"""Sources package re-exports (Stage 26)."""

from app.recruitment.discovery.sources.ats_detection import (
    AtsDetectionResult,
    detect_ats_from_html,
    detect_ats_from_url,
)
from app.recruitment.discovery.sources.employer_sources import (
    EmployerSourceManager,
    employer_source_manager,
)
from app.recruitment.discovery.sources.registry import SourceRegistry, source_registry

__all__ = [
    "AtsDetectionResult",
    "detect_ats_from_html",
    "detect_ats_from_url",
    "EmployerSourceManager",
    "employer_source_manager",
    "SourceRegistry",
    "source_registry",
]
