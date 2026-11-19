"""Generic Authorized Structured JSON Feed Connector (Stage 26).

Extracts job postings from JSON API endpoints using declarative field mappings.
"""

from datetime import UTC, datetime
from typing import Any, Optional

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
    SourceAccessStatus,
    SourceCategory,
    SourceValidationResult,
)
from app.recruitment.discovery.extraction.compensation import extract_compensation
from app.recruitment.discovery.extraction.html_text import extract_text_from_html
from app.recruitment.discovery.extraction.locations import parse_location_string
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient


class JsonFeedConnector(BaseSourceConnector):
    """Connector for discovering jobs from structured JSON feeds and endpoints."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.JSON_FEED

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=self.connector_id,
            version="1.0.0",
            provider_name="Structured JSON Job Feed",
            endpoint_category=SourceCategory.STRUCTURED_JSON_FEED,
            authentication_method="none",
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Requires valid JSON schema and mapped fields",
            ],
            last_verified_doc_url="https://jsonfeed.org",
        )

    def _resolve_path(self, data: Any, path: str) -> Any:
        if not path or path == ".":
            return data
        parts = path.split(".")
        curr = data
        for part in parts:
            if isinstance(curr, dict):
                curr = curr.get(part)
            elif isinstance(curr, list) and part.isdigit():
                idx = int(part)
                curr = curr[idx] if 0 <= idx < len(curr) else None
            else:
                return None
        return curr

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """Validate feed endpoint reachability and JSON response."""
        feed_url = config.feed_url or f"https://{config.official_domain}"
        start_time = datetime.now(UTC)
        try:
            resp = await client.get(
                feed_url,
                rate_limit_rpm=config.rate_limit_rpm,
                headers={"Accept": "application/json, */*"},
            )
            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            if resp.status_code == 200:
                payload = resp.json()
                items_path = config.custom_params.get("items_path", "jobs") if config.custom_params else "jobs"
                items = self._resolve_path(payload, items_path)
                if items is None and isinstance(payload, list):
                    items = payload
                
                if isinstance(items, list):
                    count = len(items)
                    return SourceValidationResult(
                        source_id=config.id,
                        is_valid=True,
                        detected_connector=self.connector_id,
                        access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                        available_postings_count=count,
                        response_latency_ms=latency,
                        message=f"JSON feed verified successfully ({count} postings found)",
                    )
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    access_status=SourceAccessStatus.UNAVAILABLE,
                    response_latency_ms=latency,
                    message=f"JSON response received but items path '{items_path}' did not resolve to a list",
                )
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                access_status=SourceAccessStatus.UNAVAILABLE,
                response_latency_ms=latency,
                message=f"Feed returned HTTP status {resp.status_code}",
            )
        except Exception as exc:
            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                access_status=SourceAccessStatus.UNAVAILABLE,
                response_latency_ms=latency,
                message=f"JSON feed validation failed: {str(exc)}",
            )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        """Fetch and extract job postings using declarative mapping."""
        feed_url = config.feed_url or f"https://{config.official_domain}"
        resp = await client.get(
            feed_url,
            rate_limit_rpm=config.rate_limit_rpm,
            headers={"Accept": "application/json, */*"},
        )
        if resp.status_code != 200:
            return []

        payload = resp.json()
        cparams = config.custom_params or {}
        items_path = cparams.get("items_path", "jobs")
        items = self._resolve_path(payload, items_path)
        if items is None and isinstance(payload, list):
            items = payload

        if not isinstance(items, list):
            return []

        retrieved_at = datetime.now(UTC).isoformat()
        postings: list[ExtractedPosting] = []

        id_key = cparams.get("id_field", "id")
        title_key = cparams.get("title_field", "title")
        url_key = cparams.get("url_field", "url")
        desc_key = cparams.get("description_field", "description")
        loc_key = cparams.get("location_field", "location")
        dept_key = cparams.get("department_field", "department")
        date_key = cparams.get("posted_date_field", "posted_date")
        comp_key = cparams.get("compensation_field", "compensation")

        for item in items:
            if not isinstance(item, dict):
                continue
            
            posting_id = str(item.get(id_key) or "")
            title = str(item.get(title_key) or "").strip()
            url = str(item.get(url_key) or "") or feed_url

            if not posting_id or not title:
                continue

            raw_desc = str(item.get(desc_key) or "")
            plain_desc = extract_text_from_html(raw_desc)
            
            raw_loc = str(item.get(loc_key) or "")
            loc = parse_location_string(raw_loc) if raw_loc else ExtractedLocation()

            raw_comp = item.get(comp_key)
            comp = None
            if isinstance(raw_comp, str):
                comp = extract_compensation(raw_comp)
            elif isinstance(raw_comp, dict):
                comp = extract_compensation(str(raw_comp))

            department = str(item.get(dept_key) or "") or None
            posted_date = str(item.get(date_key) or "") or None
            employer = config.employer_name or config.name or "Employer"

            provenance = {
                "title": FieldProvenance(
                    source_id=config.id,
                    retrieved_at=retrieved_at,
                    raw_field_path=f"items.{title_key}",
                    parser_method="json_mapping",
                    confidence=ExtractionConfidence.HIGH,
                ),
            }

            postings.append(
                ExtractedPosting(
                    native_posting_id=posting_id,
                    title=title,
                    employer_name=employer,
                    official_posting_url=url,
                    application_url=url,
                    location=loc,
                    department=department,
                    compensation=comp,
                    posted_date=posted_date,
                    description_text=plain_desc,
                    description_html=raw_desc,
                    raw_source_data=item,
                    provenance=provenance,
                )
            )

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        """Fetch detail for a posting."""
        postings = await self.fetch_postings(config, client)
        for p in postings:
            if p.native_posting_id == native_posting_id:
                return p
        return None
