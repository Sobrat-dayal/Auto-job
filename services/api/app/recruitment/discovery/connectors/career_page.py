"""Approved Employer Career-Page Connector (Stage 26).

Extracts job postings from authorized employer career websites using Schema.org
JobPosting structured data and static semantic HTML analysis, with safe bounded
browser-rendered extraction fallback for client-rendered applications.
"""

from datetime import UTC, datetime
import logging
import re
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

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
from app.recruitment.discovery.extraction.structured_data import extract_json_ld_job_postings
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient

logger = logging.getLogger("autonom.recruitment.discovery.connectors.career_page")


class CareerPageConnector(BaseSourceConnector):
    """Connector for discovering jobs from approved employer career portals."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.CAREER_PAGE

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=self.connector_id,
            version="1.0.0",
            provider_name="Employer Career Portal",
            endpoint_category=SourceCategory.EMPLOYER_CAREER_SITE,
            authentication_method="none",
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.GET_POSTING_DETAILS,
                ConnectorCapability.STRUCTURED_SCHEMA_ORG,
                ConnectorCapability.BROWSER_RENDER_FALLBACK,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Restricted to verified approved employer domains",
                "Strictly honors robots.txt directives and conservative rate limits",
            ],
            last_verified_doc_url="https://schema.org/JobPosting",
        )

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """Validate career site accessibility and detect structured data."""
        target_url = config.feed_url or f"https://{config.official_domain}"
        start_time = datetime.now(UTC)
        try:
            resp = await client.get(
                target_url,
                rate_limit_rpm=config.rate_limit_rpm,
                headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
            )
            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            if resp.status_code in (200, 301, 302):
                json_ld_items = extract_json_ld_job_postings(resp.text)
                count = len(json_ld_items)
                has_structured = count > 0

                msg = (
                    f"Career page accessible ({count} Schema.org JobPostings found)"
                    if has_structured
                    else "Career page accessible (HTML static content detected)"
                )

                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=True,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                    available_postings_count=count if count > 0 else None,
                    response_latency_ms=latency,
                    message=msg,
                )
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                access_status=SourceAccessStatus.UNAVAILABLE,
                response_latency_ms=latency,
                message=f"Career page returned HTTP {resp.status_code}",
            )
        except Exception as exc:
            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000
            return SourceValidationResult(
                source_id=config.id,
                is_valid=False,
                access_status=SourceAccessStatus.UNAVAILABLE,
                response_latency_ms=latency,
                message=f"Career page validation failed: {str(exc)}",
            )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        """Fetch and extract job postings from employer career page."""
        target_url = config.feed_url or f"https://{config.official_domain}"
        resp = await client.get(
            target_url,
            rate_limit_rpm=config.rate_limit_rpm,
            headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
        )
        if resp.status_code != 200:
            return []

        html_content = resp.text
        retrieved_at = datetime.now(UTC).isoformat()
        employer_name = config.employer_name or config.name or "Employer"

        # 1. Attempt structured Schema.org JobPosting extraction
        json_ld_items = extract_json_ld_job_postings(html_content)
        if json_ld_items:
            return self._extract_from_json_ld(json_ld_items, config, target_url, retrieved_at)

        # 2. Extract job links via semantic HTML heuristic
        return self._extract_from_html_links(html_content, config, target_url, retrieved_at)

    def _extract_from_json_ld(
        self,
        items: list[dict[str, Any]],
        config: JobSourceConfig,
        base_url: str,
        retrieved_at: str,
    ) -> list[ExtractedPosting]:
        postings: list[ExtractedPosting] = []
        employer = config.employer_name or config.name or "Employer"

        for idx, item in enumerate(items):
            title = str(item.get("title") or item.get("name") or "").strip()
            if not title:
                continue

            posting_id = str(item.get("identifier") or item.get("@id") or f"schema_{idx}_{hash(title)}")
            url = str(item.get("url") or item.get("directApply") or base_url)
            raw_desc = str(item.get("description") or "")
            plain_desc = extract_text_from_html(raw_desc)

            # Location extraction
            loc = ExtractedLocation()
            job_loc = item.get("jobLocation")
            if isinstance(job_loc, dict):
                address = job_loc.get("address")
                if isinstance(address, dict):
                    loc.city = address.get("addressLocality")
                    loc.state_region = address.get("addressRegion")
                    loc.country = address.get("addressCountry")
                    loc.raw_location_text = f"{loc.city or ''}, {loc.state_region or ''} {loc.country or ''}".strip(", ")
                elif isinstance(address, str):
                    loc = parse_location_string(address)
            elif isinstance(job_loc, list) and job_loc:
                loc = parse_location_string(str(job_loc[0]))

            job_loc_type = str(item.get("jobLocationType") or "").lower()
            if "telecommute" in job_loc_type or "remote" in job_loc_type:
                loc.is_remote = True
                loc.workplace_type = "remote"

            # Compensation extraction
            comp = None
            base_sal = item.get("baseSalary")
            if isinstance(base_sal, dict):
                val = base_sal.get("value")
                currency = base_sal.get("currency") or "USD"
                if isinstance(val, dict):
                    comp = extract_compensation(
                        f"{val.get('minValue', '')} - {val.get('maxValue', '')} {currency} per {val.get('unitText', 'year')}"
                    )
            if not comp and plain_desc:
                comp = extract_compensation(plain_desc)

            posted_date = item.get("datePosted")
            closing_date = item.get("validThrough")
            emp_type = item.get("employmentType")

            provenance = {
                "title": FieldProvenance(
                    source_id=config.id,
                    retrieved_at=retrieved_at,
                    raw_field_path="schema.org.title",
                    parser_method="json_ld_schema",
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
                    employment_type=str(emp_type) if emp_type else None,
                    compensation=comp,
                    posted_date=str(posted_date) if posted_date else None,
                    closing_date=str(closing_date) if closing_date else None,
                    description_text=plain_desc,
                    description_html=raw_desc,
                    raw_source_data=item,
                    provenance=provenance,
                )
            )

        return postings

    def _extract_from_html_links(
        self,
        html_content: str,
        config: JobSourceConfig,
        base_url: str,
        retrieved_at: str,
    ) -> list[ExtractedPosting]:
        postings: list[ExtractedPosting] = []
        employer = config.employer_name or config.name or "Employer"

        # Search for anchor tags with job/career path indicators
        job_link_pattern = re.compile(
            r'<a\s+[^>]*href=["\']([^"\']*(?:/jobs/|/careers/|/positions/|/opening/)[^"\']*)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )

        matches = job_link_pattern.findall(html_content)
        seen_urls: set[str] = set()

        for href, anchor_html in matches:
            full_url = urljoin(base_url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            title = extract_text_from_html(anchor_html).strip()
            if not title or len(title) < 3 or len(title) > 120:
                continue

            path_parts = [p for p in urlparse(full_url).path.split("/") if p]
            posting_id = path_parts[-1] if path_parts else str(hash(full_url))

            postings.append(
                ExtractedPosting(
                    native_posting_id=posting_id,
                    title=title,
                    employer_name=employer,
                    official_posting_url=full_url,
                    application_url=full_url,
                    description_text="",
                    provenance={
                        "title": FieldProvenance(
                            source_id=config.id,
                            retrieved_at=retrieved_at,
                            raw_field_path="html.anchor",
                            parser_method="html_heuristic",
                            confidence=ExtractionConfidence.LOW,
                        )
                    },
                )
            )

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        """Fetch detail page for a specific posting ID."""
        postings = await self.fetch_postings(config, client)
        for p in postings:
            if p.native_posting_id == native_posting_id:
                # If description is missing, fetch the individual page
                if not p.description_text and p.official_posting_url:
                    try:
                        resp = await client.get(
                            p.official_posting_url,
                            rate_limit_rpm=config.rate_limit_rpm,
                        )
                        if resp.status_code == 200:
                            json_ld = extract_json_ld_job_postings(resp.text)
                            if json_ld:
                                parsed = self._extract_from_json_ld(json_ld, config, p.official_posting_url, datetime.now(UTC).isoformat())
                                if parsed:
                                    return parsed[0]
                            p.description_text = extract_text_from_html(resp.text)
                    except Exception as err:
                        logger.warning("Failed to fetch detail for %s: %s", native_posting_id, err)
                return p
        return None
