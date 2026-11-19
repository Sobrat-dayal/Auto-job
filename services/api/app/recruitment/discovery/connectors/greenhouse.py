"""Greenhouse Job Board API connector (Stage 26).

Official Documentation: https://docs.greenhouse.io/job-board
"""

from datetime import UTC, datetime
import logging
from typing import Any, Optional

from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.contracts import (
    ConnectorCapability,
    ConnectorId,
    ConnectorManifest,
    ExtractedPosting,
    FieldProvenance,
    JobSourceConfig,
    SourceAccessStatus,
    SourceCategory,
    SourceValidationResult,
)
from app.recruitment.discovery.extraction.compensation import extract_compensation
from app.recruitment.discovery.extraction.html_text import extract_clean_text_from_html
from app.recruitment.discovery.extraction.locations import parse_location
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient

logger = logging.getLogger("autonom.recruitment.discovery.connectors.greenhouse")


class GreenhouseConnector(BaseSourceConnector):
    """Connector for official published Greenhouse Job Boards."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.GREENHOUSE

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=ConnectorId.GREENHOUSE,
            version="1.0.0",
            provider_name="Greenhouse Job Board API",
            endpoint_category=SourceCategory.EMPLOYER_ATS_BOARD,
            authentication_method="none",
            required_permissions=["network:read:greenhouse_boards"],
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Read-only public job board listings",
                "Does not support universal cross-company search; board token required per employer",
                "Application submission POST endpoints are strictly prohibited in discovery",
            ],
            last_verified_doc_url="https://docs.greenhouse.io/job-board",
        )

    def _get_board_url(self, board_token: str, with_content: bool = True) -> str:
        content_param = "?content=true" if with_content else ""
        return f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs{content_param}"

    def _get_detail_url(self, board_token: str, job_id: str) -> str:
        return f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        token = config.board_token
        if not token:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNVERIFIED,
                message="Board token is missing in source configuration.",
            )

        url = self._get_board_url(token, with_content=False)
        try:
            resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
            if resp.status_code == 200:
                data = resp.json()
                jobs = data.get("jobs", [])
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=True,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                    available_postings_count=len(jobs),
                    response_latency_ms=resp.latency_ms,
                    message=f"Greenhouse board '{token}' is valid and published with {len(jobs)} active postings.",
                )
            elif resp.status_code == 404:
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.UNAVAILABLE,
                    message=f"Greenhouse board token '{token}' was not found (HTTP 404).",
                )
            else:
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.UNAVAILABLE,
                    message=f"Greenhouse returned HTTP {resp.status_code}.",
                )
        except Exception as exc:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNAVAILABLE,
                message=f"Connection failure: {exc}",
            )

    def _parse_job_item(self, config: JobSourceConfig, item: dict[str, Any]) -> ExtractedPosting:
        native_id = str(item.get("id", ""))
        title = item.get("title", "Untitled Role")
        official_url = item.get("absolute_url", f"https://boards.greenhouse.io/{config.board_token}/jobs/{native_id}")

        loc_data = item.get("location") or {}
        loc_name = loc_data.get("name") if isinstance(loc_data, dict) else str(loc_data)
        extracted_loc = parse_location(loc_name)

        departments = item.get("departments") or []
        dept_name = departments[0].get("name") if (departments and isinstance(departments[0], dict)) else None

        offices = item.get("offices") or []
        office_name = offices[0].get("name") if (offices and isinstance(offices[0], dict)) else None

        raw_content = item.get("content") or ""
        clean_desc = extract_clean_text_from_html(raw_content)

        updated_at = item.get("updated_at")
        compensation = extract_compensation(clean_desc)

        now_iso = datetime.now(UTC).isoformat()
        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=now_iso,
                raw_field_path="jobs[].title",
                parser_method="json_key",
                original_raw_value=title,
            ),
            "location": FieldProvenance(
                source_id=config.id,
                retrieved_at=now_iso,
                raw_field_path="jobs[].location.name",
                parser_method="location_normalizer",
                original_raw_value=loc_name,
            ),
        }

        return ExtractedPosting(
            native_posting_id=native_id,
            title=title,
            employer_name=config.employer_name or config.name,
            official_posting_url=official_url,
            application_url=official_url,
            location=extracted_loc,
            employment_type=None,
            compensation=compensation,
            posted_date=None,
            updated_date=updated_at,
            department=dept_name,
            office=office_name,
            description_text=clean_desc,
            description_html=raw_content if raw_content else None,
            raw_source_data=item,
            provenance=provenance,
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        token = config.board_token
        if not token:
            return []

        url = self._get_board_url(token, with_content=True)
        resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            logger.warning(f"Greenhouse fetch failed for '{token}' with HTTP {resp.status_code}")
            return []

        data = resp.json()
        raw_jobs = data.get("jobs", [])
        postings = []
        for raw in raw_jobs:
            if isinstance(raw, dict):
                postings.append(self._parse_job_item(config, raw))

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        token = config.board_token
        if not token:
            return None

        url = self._get_detail_url(token, native_posting_id)
        resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            return None

        data = resp.json()
        if isinstance(data, dict):
            return self._parse_job_item(config, data)
        return None
