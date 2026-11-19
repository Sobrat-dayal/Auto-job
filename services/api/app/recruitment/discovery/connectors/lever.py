"""Lever Postings API connector (Stage 26).

Official Documentation: https://github.com/lever/postings-api
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
from app.recruitment.discovery.extraction.locations import parse_location
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient

logger = logging.getLogger("autonom.recruitment.discovery.connectors.lever")


class LeverConnector(BaseSourceConnector):
    """Connector for official published Lever Postings."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.LEVER

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=ConnectorId.LEVER,
            version="1.0.0",
            provider_name="Lever Postings API",
            endpoint_category=SourceCategory.EMPLOYER_ATS_BOARD,
            authentication_method="none",
            required_permissions=["network:read:lever_postings"],
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.PAGINATION,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Read-only published job listings for public sites",
                "Does not permit fetching internal, unlisted, or confidential drafts",
                "Application submissions through Lever Apply API are not supported in discovery",
            ],
            last_verified_doc_url="https://github.com/lever/postings-api",
        )

    def _get_site_url(self, site: str, limit: int = 100, skip: int = 0) -> str:
        return f"https://api.lever.co/v0/postings/{site}?mode=json&limit={limit}&skip={skip}"

    def _get_detail_url(self, site: str, posting_id: str) -> str:
        return f"https://api.lever.co/v0/postings/{site}/{posting_id}"

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        site = config.site_id or config.board_token
        if not site:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNVERIFIED,
                message="Lever company/site identifier is missing in configuration.",
            )

        url = self._get_site_url(site, limit=5, skip=0)
        try:
            resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return SourceValidationResult(
                        source_id=config.id,
                        is_valid=True,
                        detected_connector=self.connector_id,
                        access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                        available_postings_count=len(data),
                        response_latency_ms=resp.latency_ms,
                        message=f"Lever site '{site}' is valid and published with at least {len(data)} postings.",
                    )
            elif resp.status_code == 404:
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.UNAVAILABLE,
                    message=f"Lever company site '{site}' was not found (HTTP 404).",
                )
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNAVAILABLE,
                message=f"Lever returned HTTP {resp.status_code}.",
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
        title = item.get("text", "Untitled Role")
        hosted_url = item.get("hostedUrl", f"https://jobs.lever.co/{config.site_id or config.board_token}/{native_id}")
        apply_url = item.get("applyUrl", hosted_url)

        categories = item.get("categories") or {}
        loc_raw = categories.get("location") if isinstance(categories, dict) else None
        workplace_type = item.get("workplaceType")
        is_remote_flag = (workplace_type == "remote") if workplace_type else None
        extracted_loc = parse_location(loc_raw, is_remote_flag=is_remote_flag)
        if workplace_type:
            extracted_loc.workplace_type = workplace_type

        dept = categories.get("department") if isinstance(categories, dict) else None
        commitment = categories.get("commitment") if isinstance(categories, dict) else None

        # Employment type
        emp_type: Optional[str] = None
        if commitment:
            c_low = commitment.lower()
            if "full" in c_low:
                emp_type = "full_time"
            elif "part" in c_low:
                emp_type = "part_time"
            elif "intern" in c_low:
                emp_type = "internship"
            elif "contract" in c_low:
                emp_type = "contract"

        desc_plain = item.get("descriptionPlain") or ""
        compensation = extract_compensation(desc_plain)

        created_ms = item.get("createdAt")
        posted_iso: Optional[str] = None
        if created_ms:
            try:
                posted_iso = datetime.fromtimestamp(created_ms / 1000.0, UTC).isoformat()
            except Exception:
                pass

        now_iso = datetime.now(UTC).isoformat()
        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=now_iso,
                raw_field_path="text",
                parser_method="json_key",
                original_raw_value=title,
            ),
        }

        return ExtractedPosting(
            native_posting_id=native_id,
            title=title,
            employer_name=config.employer_name or config.name,
            official_posting_url=hosted_url,
            application_url=apply_url,
            location=extracted_loc,
            employment_type=emp_type,
            compensation=compensation,
            posted_date=posted_iso,
            updated_date=None,
            department=dept,
            office=None,
            description_text=desc_plain,
            description_html=item.get("description"),
            raw_source_data=item,
            provenance=provenance,
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        site = config.site_id or config.board_token
        if not site:
            return []

        postings: list[ExtractedPosting] = []
        skip = 0
        limit = 100
        max_pages = 5  # Bounded pagination safety

        for _ in range(max_pages):
            url = self._get_site_url(site, limit=limit, skip=skip)
            resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
            if resp.status_code != 200:
                break

            data = resp.json()
            if not isinstance(data, list) or len(data) == 0:
                break

            for raw in data:
                if isinstance(raw, dict):
                    postings.append(self._parse_job_item(config, raw))

            if len(data) < limit:
                break
            skip += limit

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        site = config.site_id or config.board_token
        if not site:
            return None

        url = self._get_detail_url(site, native_posting_id)
        resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            return None

        data = resp.json()
        if isinstance(data, dict):
            return self._parse_job_item(config, data)
        return None
