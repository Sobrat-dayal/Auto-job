"""User-Provided Job URL Import Connector (Stage 26).

Extracts job postings from single arbitrary job URLs provided by the user,
automatically detecting ATS providers (Greenhouse, Lever, Ashby) or parsing
Schema.org JobPosting structured metadata.
"""

from datetime import UTC, datetime
import logging
import re
from typing import Any, Optional
from urllib.parse import urlparse

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
    UrlImportRequest,
)
from app.recruitment.discovery.extraction.compensation import extract_compensation
from app.recruitment.discovery.extraction.html_text import extract_text_from_html
from app.recruitment.discovery.extraction.locations import parse_location_string
from app.recruitment.discovery.extraction.structured_data import extract_json_ld_job_postings
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient

logger = logging.getLogger("autonom.recruitment.discovery.connectors.url_import")


class UrlImportConnector(BaseSourceConnector):
    """Connector for importing and extracting postings from single user-provided URLs."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.URL_IMPORT

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=self.connector_id,
            version="1.0.0",
            provider_name="URL Job Importer",
            endpoint_category=SourceCategory.USER_SUPPLIED_URL,
            authentication_method="none",
            supported_capabilities=[
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.STRUCTURED_SCHEMA_ORG,
            ],
            provider_restrictions=[
                "User-supplied URL; validated against SSRF blocklists",
            ],
            last_verified_doc_url="https://autonom.local/docs/url-import",
        )

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """URL importer is always valid as a connector."""
        return SourceValidationResult(
            source_id=config.id,
            is_valid=True,
            detected_connector=self.connector_id,
            access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
            message="URL importer connector is ready.",
        )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        return []

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        return None

    def detect_ats_from_url(self, url: str) -> tuple[Optional[ConnectorId], Optional[str], Optional[str]]:
        """Detect ATS provider, board token/site, and job ID from URL structure.
        
        Returns (connector_id, board_token, native_job_id).
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.strip("/")
        parts = path.split("/")

        # Greenhouse: boards.greenhouse.io/{board_token}/jobs/{job_id}
        if "greenhouse.io" in domain:
            if len(parts) >= 3 and parts[1] == "jobs":
                return ConnectorId.GREENHOUSE, parts[0], parts[2]
            if len(parts) >= 1:
                return ConnectorId.GREENHOUSE, parts[0], parts[-1] if len(parts) > 1 else None

        # Lever: jobs.lever.co/{site}/{job_id}
        if "lever.co" in domain:
            if len(parts) >= 2:
                return ConnectorId.LEVER, parts[0], parts[1]
            if len(parts) == 1:
                return ConnectorId.LEVER, parts[0], None

        # Ashby: jobs.ashbyhq.com/{board_token}/{job_id}
        if "ashbyhq.com" in domain:
            if len(parts) >= 2:
                return ConnectorId.ASHBY, parts[0], parts[1]
            if len(parts) == 1:
                return ConnectorId.ASHBY, parts[0], None

        return None, None, None

    async def import_from_url(
        self,
        req: UrlImportRequest,
        client: DiscoveryHttpClient,
        source_id: str = "url_user_import",
    ) -> ExtractedPosting:
        """Fetch and extract job posting information from arbitrary URL."""
        retrieved_at = datetime.now(UTC).isoformat()
        ats_id, board_token, job_id = self.detect_ats_from_url(req.url)

        # 1. Fetch the page
        resp = await client.get(req.url)
        if resp.status_code != 200:
            raise ValueError(f"Target URL returned HTTP {resp.status_code}")

        html_text = resp.text

        # 2. Check JSON-LD schema
        json_ld_items = extract_json_ld_job_postings(html_text)
        if json_ld_items:
            item = json_ld_items[0]
            title = str(item.get("title") or item.get("name") or req.target_role or "Untitled Position").strip()
            employer = req.employer_name or str(
                item.get("hiringOrganization", {}).get("name") if isinstance(item.get("hiringOrganization"), dict) else "Employer"
            )
            raw_desc = str(item.get("description") or "")
            plain_desc = extract_text_from_html(raw_desc)
            posting_id = str(item.get("identifier") or job_id or hash(req.url))

            # Location
            loc = ExtractedLocation()
            job_loc = item.get("jobLocation")
            if isinstance(job_loc, dict):
                address = job_loc.get("address")
                if isinstance(address, dict):
                    loc.city = address.get("addressLocality")
                    loc.state_region = address.get("addressRegion")
                    loc.country = address.get("addressCountry")
                    loc.raw_location_text = f"{loc.city or ''}, {loc.state_region or ''} {loc.country or ''}".strip(", ")

            comp = None
            base_sal = item.get("baseSalary")
            if isinstance(base_sal, dict):
                val = base_sal.get("value")
                currency = base_sal.get("currency") or "USD"
                if isinstance(val, dict):
                    comp = extract_compensation(f"{val.get('minValue', '')} - {val.get('maxValue', '')} {currency}")
            if not comp and plain_desc:
                comp = extract_compensation(plain_desc)

            return ExtractedPosting(
                native_posting_id=posting_id,
                title=title,
                employer_name=employer,
                official_posting_url=req.url,
                application_url=req.url,
                location=loc,
                compensation=comp,
                posted_date=str(item.get("datePosted") or retrieved_at),
                description_text=plain_desc,
                description_html=raw_desc,
                raw_source_data=item,
                provenance={
                    "title": FieldProvenance(
                        source_id=source_id,
                        retrieved_at=retrieved_at,
                        raw_field_path="schema.org.title",
                        parser_method="json_ld",
                        confidence=ExtractionConfidence.HIGH,
                    )
                },
            )

        # 3. Fallback to HTML title & body text extraction
        title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        raw_title = title_match.group(1).strip() if title_match else "Job Opportunity"
        # Clean title (e.g. "Senior Engineer at Stripe - Careers" -> "Senior Engineer")
        clean_title = re.sub(r"\s*[-|–—]\s*(?:Careers|Jobs|Lever|Greenhouse).*$", "", raw_title, flags=re.IGNORECASE).strip()
        if req.target_role:
            clean_title = req.target_role

        plain_text = extract_text_from_html(html_text)
        comp = extract_compensation(plain_text)
        loc = parse_location_string(plain_text[:400])

        employer = req.employer_name or (board_token.capitalize() if board_token else "Employer")
        posting_id = job_id or f"url_{abs(hash(req.url))}"

        return ExtractedPosting(
            native_posting_id=posting_id,
            title=clean_title,
            employer_name=employer,
            official_posting_url=req.url,
            application_url=req.url,
            location=loc,
            compensation=comp,
            posted_date=retrieved_at,
            description_text=plain_text,
            provenance={
                "title": FieldProvenance(
                    source_id=source_id,
                    retrieved_at=retrieved_at,
                    raw_field_path="html.title",
                    parser_method="html_heuristic",
                    confidence=ExtractionConfidence.MEDIUM,
                )
            },
        )
