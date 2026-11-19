"""Ashby Public Job Postings API connector (Stage 26).

Official Documentation: https://developers.ashbyhq.com/docs/public-job-posting-api
"""

from datetime import UTC, datetime
import logging
from typing import Any, Optional

from app.recruitment.discovery.connectors.base import BaseSourceConnector
from app.recruitment.discovery.contracts import (
    ConnectorCapability,
    ConnectorId,
    ConnectorManifest,
    ExtractedCompensation,
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

logger = logging.getLogger("autonom.recruitment.discovery.connectors.ashby")


class AshbyConnector(BaseSourceConnector):
    """Connector for official Ashby public Job Postings API."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.ASHBY

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=ConnectorId.ASHBY,
            version="1.0.0",
            provider_name="Ashby Public Job Postings API",
            endpoint_category=SourceCategory.EMPLOYER_ATS_BOARD,
            authentication_method="none",
            required_permissions=["network:read:ashby_boards"],
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Read-only public job board listings",
                "Does not permit unauthorized applicant form submission",
                "Organization public board identifier required per company",
            ],
            last_verified_doc_url="https://developers.ashbyhq.com/docs/public-job-posting-api",
        )

    def _get_board_url(self, board_token: str) -> str:
        return f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"

    def _get_detail_url(self, board_token: str, job_id: str) -> str:
        return f"https://api.ashbyhq.com/posting-api/job-board/{board_token}/job/{job_id}"

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        token = config.board_token or config.site_id
        if not token:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNVERIFIED,
                message="Ashby board identifier is missing in configuration.",
            )

        url = self._get_board_url(token)
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
                    message=f"Ashby board '{token}' is valid with {len(jobs)} active postings.",
                )
            elif resp.status_code == 404:
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.UNAVAILABLE,
                    message=f"Ashby board token '{token}' was not found (HTTP 404).",
                )
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNAVAILABLE,
                message=f"Ashby returned HTTP {resp.status_code}.",
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
        job_url = item.get("jobUrl", f"https://jobs.ashbyhq.com/{config.board_token or config.site_id}/{native_id}")
        apply_url = item.get("applyUrl", job_url)

        loc_raw = item.get("location")
        is_remote_flag = item.get("isRemote")
        extracted_loc = parse_location(loc_raw, is_remote_flag=is_remote_flag)

        dept = item.get("department") or item.get("team")
        published_at = item.get("publishedAt")

        emp_raw = item.get("employmentType")
        emp_type: Optional[str] = None
        if emp_raw:
            er_low = str(emp_raw).lower()
            if "full" in er_low:
                emp_type = "full_time"
            elif "part" in er_low:
                emp_type = "part_time"
            elif "intern" in er_low:
                emp_type = "internship"
            elif "contract" in er_low:
                emp_type = "contract"

        # Compensation parsing
        comp_obj = item.get("compensation")
        extracted_comp: Optional[ExtractedCompensation] = None
        if isinstance(comp_obj, dict):
            tier_summary = comp_obj.get("compensationTierSummary")
            if tier_summary:
                extracted_comp = extract_compensation(str(tier_summary))

        desc_raw = item.get("descriptionHtml") or item.get("descriptionPlain") or ""
        clean_desc = extract_clean_text_from_html(desc_raw) if "<" in desc_raw else desc_raw
        if not extracted_comp and clean_desc:
            extracted_comp = extract_compensation(clean_desc)

        now_iso = datetime.now(UTC).isoformat()
        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=now_iso,
                raw_field_path="title",
                parser_method="json_key",
                original_raw_value=title,
            ),
        }

        return ExtractedPosting(
            native_posting_id=native_id,
            title=title,
            employer_name=config.employer_name or config.name,
            official_posting_url=job_url,
            application_url=apply_url,
            location=extracted_loc,
            employment_type=emp_type,
            compensation=extracted_comp,
            posted_date=published_at,
            department=dept,
            description_text=clean_desc,
            description_html=item.get("descriptionHtml"),
            raw_source_data=item,
            provenance=provenance,
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        token = config.board_token or config.site_id
        if not token:
            return []

        url = self._get_board_url(token)
        resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            logger.warning(f"Ashby fetch failed for '{token}' with HTTP {resp.status_code}")
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
        token = config.board_token or config.site_id
        if not token:
            return None

        url = self._get_detail_url(token, native_posting_id)
        resp = await client.fetch(url, source_id=config.id, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            return None

        data = resp.json()
        job_data = data.get("job") or data
        if isinstance(job_data, dict):
            return self._parse_job_item(config, job_data)
        return None
