"""RSS and Atom Feed Connector (Stage 26).

Extracts job postings from standard RSS 2.0 and Atom feeds safely without XML entity expansion.
"""

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import html
from typing import Any, Optional
import xml.etree.ElementTree as ET

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


class RssAtomConnector(BaseSourceConnector):
    """Connector for discovering jobs from RSS 2.0 and Atom syndication feeds."""

    @property
    def connector_id(self) -> ConnectorId:
        return ConnectorId.RSS_ATOM

    @property
    def manifest(self) -> ConnectorManifest:
        return ConnectorManifest(
            connector_id=self.connector_id,
            version="1.0.0",
            provider_name="RSS / Atom Job Feed",
            endpoint_category=SourceCategory.RSS_ATOM_FEED,
            authentication_method="none",
            supported_capabilities=[
                ConnectorCapability.LIST_POSTINGS,
                ConnectorCapability.CONDITIONAL_FETCH,
            ],
            provider_restrictions=[
                "Requires well-formed XML feed",
                "Entities expanded are strictly disabled for security",
            ],
            last_verified_doc_url="https://www.rssboard.org/rss-specification",
        )

    async def validate_source(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
    ) -> SourceValidationResult:
        """Validate feed endpoint reachability and XML structure."""
        feed_url = config.feed_url or f"https://{config.official_domain}"
        start_time = datetime.now(UTC)
        try:
            resp = await client.get(
                feed_url,
                rate_limit_rpm=config.rate_limit_rpm,
                headers={"Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
            )
            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            if resp.status_code == 200:
                root = ET.fromstring(resp.text)
                is_rss = root.tag.lower().endswith("rss") or root.find("channel") is not None
                is_atom = "feed" in root.tag.lower()
                
                if not (is_rss or is_atom):
                    return SourceValidationResult(
                        source_id=config.id,
                        is_valid=False,
                        access_status=SourceAccessStatus.UNAVAILABLE,
                        message="XML document root is neither an RSS channel nor an Atom feed.",
                    )
                
                # Count items
                count = len(root.findall(".//item")) or len(root.findall(".//{http://www.w3.org/2005/Atom}entry")) or len(root.findall(".//entry"))
                return SourceValidationResult(
                    source_id=config.id,
                    is_valid=True,
                    detected_connector=self.connector_id,
                    access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                    available_postings_count=count,
                    response_latency_ms=latency,
                    message=f"Successfully parsed feed ({count} entries detected)",
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
                message=f"Feed validation failed: {str(exc)}",
            )

    async def fetch_postings(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        params: Optional[dict[str, Any]] = None,
    ) -> list[ExtractedPosting]:
        """Fetch and parse all postings in the RSS/Atom feed."""
        feed_url = config.feed_url or f"https://{config.official_domain}"
        resp = await client.get(
            feed_url,
            rate_limit_rpm=config.rate_limit_rpm,
            headers={"Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
        )
        if resp.status_code != 200:
            return []

        retrieved_at = datetime.now(UTC).isoformat()
        root = ET.fromstring(resp.text)
        
        postings: list[ExtractedPosting] = []

        # Check RSS items
        rss_items = root.findall(".//item")
        if rss_items:
            for item in rss_items:
                posting = self._parse_rss_item(item, config, retrieved_at)
                if posting:
                    postings.append(posting)
            return postings

        # Check Atom entries
        atom_entries = root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//entry")
        for entry in atom_entries:
            posting = self._parse_atom_entry(entry, config, retrieved_at)
            if posting:
                postings.append(posting)

        return postings

    async def fetch_posting_detail(
        self,
        config: JobSourceConfig,
        client: DiscoveryHttpClient,
        native_posting_id: str,
    ) -> Optional[ExtractedPosting]:
        """Detail fetch scans current feed items for matching ID."""
        postings = await self.fetch_postings(config, client)
        for p in postings:
            if p.native_posting_id == native_posting_id:
                return p
        return None

    def _parse_rss_item(
        self,
        item: ET.Element,
        config: JobSourceConfig,
        retrieved_at: str,
    ) -> Optional[ExtractedPosting]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link or title).strip()
        desc = item.findtext("description") or ""
        pub_date_raw = item.findtext("pubDate")

        if not title or not (guid or link):
            return None

        posted_date = None
        if pub_date_raw:
            try:
                posted_date = parsedate_to_datetime(pub_date_raw).isoformat()
            except Exception:
                posted_date = pub_date_raw

        plain_text = extract_text_from_html(desc)
        comp = extract_compensation(plain_text)
        loc = parse_location_string(title + " " + plain_text[:200])

        employer = config.employer_name or config.name or "Employer"

        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=retrieved_at,
                raw_field_path="item.title",
                parser_method="rss_parser",
                confidence=ExtractionConfidence.HIGH,
            ),
            "description": FieldProvenance(
                source_id=config.id,
                retrieved_at=retrieved_at,
                raw_field_path="item.description",
                parser_method="html_sanitizer",
                confidence=ExtractionConfidence.MEDIUM,
            ),
        }

        return ExtractedPosting(
            native_posting_id=guid,
            title=title,
            employer_name=employer,
            official_posting_url=link or f"https://{config.official_domain}",
            application_url=link,
            location=loc,
            compensation=comp,
            posted_date=posted_date,
            description_text=plain_text,
            description_html=desc,
            provenance=provenance,
        )

    def _parse_atom_entry(
        self,
        entry: ET.Element,
        config: JobSourceConfig,
        retrieved_at: str,
    ) -> Optional[ExtractedPosting]:
        title_el = entry.find("{http://www.w3.org/2005/Atom}title") or entry.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""

        id_el = entry.find("{http://www.w3.org/2005/Atom}id") or entry.find("id")
        entry_id = (id_el.text or "").strip() if id_el is not None else ""

        link_el = entry.find("{http://www.w3.org/2005/Atom}link") or entry.find("link")
        link = ""
        if link_el is not None:
            link = link_el.attrib.get("href", "") or (link_el.text or "").strip()

        content_el = entry.find("{http://www.w3.org/2005/Atom}content") or entry.find("content") or entry.find("{http://www.w3.org/2005/Atom}summary") or entry.find("summary")
        desc = (content_el.text or "") if content_el is not None else ""

        updated_el = entry.find("{http://www.w3.org/2005/Atom}updated") or entry.find("updated") or entry.find("{http://www.w3.org/2005/Atom}published") or entry.find("published")
        posted_date = (updated_el.text or "").strip() if updated_el is not None else None

        if not title or not (entry_id or link):
            return None

        plain_text = extract_text_from_html(desc)
        comp = extract_compensation(plain_text)
        loc = parse_location_string(title + " " + plain_text[:200])

        employer = config.employer_name or config.name or "Employer"

        provenance = {
            "title": FieldProvenance(
                source_id=config.id,
                retrieved_at=retrieved_at,
                raw_field_path="entry.title",
                parser_method="atom_parser",
                confidence=ExtractionConfidence.HIGH,
            ),
        }

        return ExtractedPosting(
            native_posting_id=entry_id or link,
            title=title,
            employer_name=employer,
            official_posting_url=link or f"https://{config.official_domain}",
            application_url=link,
            location=loc,
            compensation=comp,
            posted_date=posted_date,
            description_text=plain_text,
            description_html=desc,
            provenance=provenance,
        )
