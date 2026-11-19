"""USAJOBS Search API connector with registered credential gating (Stage 26).

Official Documentation: https://developer.usajobs.gov/api-reference/job-apis
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
from app.recruitment.discovery.extraction.locations import parse_location
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient

logger = logging.getLogger("autonom.recruitment.discovery.connectors.usajobs")


class USAJobsConnector(BaseSourceConnector):
    """Connector for official USAJOBS Search API."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.USAJOBS

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=ConnectorId.USAJOBS,
            version="1.0.0",
            provider_name="USAJOBS Search API",
            endpoint_category=SourceCategory.OFFICIAL_PUBLIC_API,
            authentication_method="api_key",
            required_permissions=["network:read:usajobs_api"],
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.SERVER_SEARCH,
                ConnectorCapability.CREDENTIAL_GATED,
            ],
            provider_restrictions=[
                "Requires registered developer Authorization-Key and User-Agent email",
                "Discovered federal vacancies have strict citizenship and security clearance conditions",
                "Does not grant automated application submission rights",
            ],
            last_verified_doc_url="https://developer.usajobs.gov/api-reference/job-apis",
        )

    def _get_api_headers(self, config: JobSourceConfig) -> dict[str, str]:
        auth_key = config.custom_headers.get("Authorization-Key") or config.credential_alias
        user_agent_email = config.custom_headers.get("User-Agent-Email") or "autonom-agent@desktop.local"

        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": user_agent_email,
        }
        if auth_key:
            headers["Authorization-Key"] = auth_key
        return headers

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        headers = self._get_api_headers(config)
        if "Authorization-Key" not in headers:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.REQUIRES_CREDENTIALS,
                message="USAJOBS requires registered developer 'Authorization-Key' and email in custom_headers.",
            )

        url = "https://data.usajobs.gov/api/search?ResultsPerPage=1"
        try:
            resp = await client.fetch(
                url,
                source_id=config.id,
                headers=headers,
                rate_limit_rpm=config.rate_limit_rpm,
            )
            if resp.status_code == 200:
                data = resp.json()
                sr = data.get("SearchResult", {})
                count = sr.get("SearchResultCount", 0)
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=True,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.AVAILABLE_AUTHORIZED,
                    available_postings_count=count,
                    response_latency_ms=resp.latency_ms,
                    message=f"USAJOBS API credentials verified. Connected with {count} search results.",
                )
            elif resp.status_code in (401, 403):
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=False,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.ACCESS_DENIED,
                    message=f"USAJOBS authentication failed (HTTP {resp.status_code}). Invalid Authorization-Key.",
                )
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNAVAILABLE,
                message=f"USAJOBS returned HTTP {resp.status_code}.",
            )
        except Exception as exc:
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                detected_connector=self.connector_id,
                access_status=SourceAccessStatus.UNAVAILABLE,
                message=f"USAJOBS connection failure: {exc}",
            )

    def _parse_job_item(self, config: JobSourceConfig, item: dict[str, Any]) -> ExtractedPosting:
        native_id = str(item.get("MatchedObjectId", ""))
        desc_obj = item.get("MatchedObjectDescriptor", {})

        title = desc_obj.get("PositionTitle", "Untitled Federal Role")
        pos_uri = desc_obj.get("PositionURI", f"https://www.usajobs.gov/job/{native_id}")
        apply_uris = desc_obj.get("ApplyURI", [pos_uri])
        apply_url = apply_uris[0] if apply_uris else pos_uri

        employer = desc_obj.get("OrganizationName") or desc_obj.get("DepartmentName") or "Federal Government"
        loc_display = desc_obj.get("PositionLocationDisplay", "")
        extracted_loc = parse_location(loc_display)

        # Compensation
        remun = desc_obj.get("PositionRemuneration", [])
        extracted_comp: Optional[ExtractedCompensation] = None
        if remun and isinstance(remun[0], dict):
            r = remun[0]
            try:
                min_a = float(r.get("MinimumRange", 0))
                max_a = float(r.get("MaximumRange", 0))
                interval = r.get("RateIntervalCode", "Per Year")
                unit = "annual" if "year" in interval.lower() else ("hourly" if "hour" in interval.lower() else "annual")
                extracted_comp = ExtractedCompensation(
                    min_amount=min_a,
                    max_amount=max_a,
                    currency="USD",
                    unit=unit,
                    pay_period=interval,
                    raw_text=f"${min_a:,.2f} - ${max_a:,.2f} {interval}",
                )
            except Exception:
                pass

        posted_date = desc_obj.get("PositionStartDate")
        closing_date = desc_obj.get("PositionEndDate")

        user_area = desc_obj.get("UserArea", {}).get("Details", {})
        summary = user_area.get("JobSummary", "")
        duties = user_area.get("MajorDuties", [])
        if isinstance(duties, list) and duties:
            summary = summary + "\n\nMajor Duties:\n• " + "\n• ".join(duties)

        now_iso = datetime.now(UTC).isoformat()
        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=now_iso,
                raw_field_path="MatchedObjectDescriptor.PositionTitle",
                parser_method="json_key",
                original_raw_value=title,
            ),
        }

        return ExtractedPosting(
            native_posting_id=native_id,
            title=title,
            employer_name=employer,
            official_posting_url=pos_uri,
            application_url=apply_url,
            location=extracted_loc,
            employment_type="full_time",
            compensation=extracted_comp,
            posted_date=posted_date,
            closing_date=closing_date,
            department=desc_obj.get("DepartmentName"),
            description_text=summary,
            raw_source_data=item,
            provenance=provenance,
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        headers = self._get_api_headers(config)
        if "Authorization-Key" not in headers:
            logger.warning("USAJOBS fetch skipped: Authorization-Key missing in configuration.")
            return []

        keyword = (params or {}).get("keyword") or "Software"
        url = f"https://data.usajobs.gov/api/search?Keyword={keyword}&ResultsPerPage=25"

        resp = await client.fetch(url, source_id=config.id, headers=headers, rate_limit_rpm=config.rate_limit_rpm)
        if resp.status_code != 200:
            return []

        data = resp.json()
        items = data.get("SearchResult", {}).get("SearchResultItems", [])
        postings = []
        for raw in items:
            if isinstance(raw, dict):
                postings.append(self._parse_job_item(config, raw))

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        return None
