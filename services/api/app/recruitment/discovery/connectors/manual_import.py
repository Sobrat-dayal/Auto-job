"""Manual Job Posting Import Connector (Stage 26).

Handles user-supplied job postings directly entered or pasted by the user.
"""

from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.contracts import (
    ConnectorCapability,
    ConnectorId,
    ConnectorManifest,
    ExtractionConfidence,
    ExtractedLocation,
    ExtractedPosting,
    FieldProvenance,
    JobSourceConfig,
    ManualImportRequest,
    SourceAccessStatus,
    SourceCategory,
    SourceValidationResult,
)
from app.recruitment.discovery.extraction.compensation import extract_compensation
from app.recruitment.discovery.extraction.locations import parse_location_string
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient


class ManualImportConnector(BaseSourceConnector):
    """Connector for manually imported and user-supplied job postings."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.MANUAL_IMPORT

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=self.connector_id,
            version="1.0.0",
            provider_name="Manual User Import",
            endpoint_category=SourceCategory.MANUAL_IMPORTED,
            authentication_method="none",
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
            ],
            provider_restrictions=[
                "User-supplied input; requires user verification",
            ],
            last_verified_doc_url="https://autonom.local/docs/manual-import",
        )

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """Manual sources are always valid."""
        return SourceValidationResult(
            source_id=config.id,
            is_valid=True,
            detected_connector=self.connector_id,
            access_status=SourceAccessStatus.MANUAL_IMPORT_ONLY,
            message="Manual import source is permanently available.",
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        """Manual sources do not poll endpoints."""
        return []

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        return None

    def create_from_request(
        self,
        req: ManualImportRequest,
        source_id: str = "manual_user_import",
    ) -> ExtractedPosting:
        """Convert a user ManualImportRequest into a typed ExtractedPosting."""
        retrieved_at = datetime.now(UTC).isoformat()
        posting_id = f"manual_{uuid4().hex[:10]}"

        # Location
        loc = parse_location_string(req.location) if req.location else ExtractedLocation()
        if req.work_arrangement:
            loc.workplace_type = req.work_arrangement
            if req.work_arrangement.lower() == "remote":
                loc.is_remote = True

        # Compensation
        comp = extract_compensation(req.compensation_text) if req.compensation_text else None
        if not comp and req.description:
            comp = extract_compensation(req.description)

        provenance = {
            "title": FieldProvenance(
                source_id=source_id,
                retrieved_at=retrieved_at,
                raw_field_path="user.title",
                parser_method="user_input",
                confidence=ExtractionConfidence.HIGH,
            ),
            "description": FieldProvenance(
                source_id=source_id,
                retrieved_at=retrieved_at,
                raw_field_path="user.description",
                parser_method="user_input",
                confidence=ExtractionConfidence.HIGH,
            ),
        }

        return ExtractedPosting(
            native_posting_id=posting_id,
            title=req.title,
            employer_name=req.employer_name,
            official_posting_url=req.source_url or "https://manual.autonom.local",
            application_url=req.application_url or req.source_url,
            location=loc,
            employment_type=req.employment_type,
            compensation=comp,
            posted_date=retrieved_at,
            description_text=req.description,
            provenance=provenance,
        )
