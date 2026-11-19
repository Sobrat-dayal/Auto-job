"""ATS Platform Detection (Stage 26).

Analyzes career URLs, hostnames, and HTML content to automatically identify ATS providers
(Greenhouse, Lever, Ashby, Workday, SmartRecruiters, USAJOBS) and extract board tokens.
"""

from dataclasses import dataclass
import re
from typing import Optional
from urllib.parse import urlparse

from app.recruitment.discovery.contracts import ConnectorId, ExtractionConfidence


@dataclass
class AtsDetectionResult:
    detected_connector: Optional[ConnectorId]
    platform_name: str
    board_token: Optional[str] = None
    site_id: Optional[str] = None
    job_id: Optional[str] = None
    confidence: ExtractionConfidence = ExtractionConfidence.LOW
    evidence: str = ""


# Hostname regex patterns
GREENHOUSE_HOST_PATTERN = re.compile(r"(?:boards|job-boards|api)\.greenhouse\.io", re.IGNORECASE)
LEVER_HOST_PATTERN = re.compile(r"(?:jobs|api)\.lever\.co", re.IGNORECASE)
ASHBY_HOST_PATTERN = re.compile(r"(?:jobs|api)\.ashbyhq\.com", re.IGNORECASE)
USAJOBS_HOST_PATTERN = re.compile(r"(?:data\.)?usajobs\.gov", re.IGNORECASE)
WORKDAY_HOST_PATTERN = re.compile(r"[\w-]+\.myworkdayjobs\.com", re.IGNORECASE)
SMARTRECRUITERS_HOST_PATTERN = re.compile(r"(?:jobs|careers)\.smartrecruiters\.com", re.IGNORECASE)


def detect_ats_from_url(url: str) -> AtsDetectionResult:
    """Analyze a URL to detect if it matches a known ATS platform."""
    if not url:
        return AtsDetectionResult(None, "Unknown", confidence=ExtractionConfidence.LOW, evidence="Empty URL")

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]

    # 1. Greenhouse
    if GREENHOUSE_HOST_PATTERN.search(domain):
        board_token = path_parts[0] if path_parts else None
        job_id = None
        if len(path_parts) >= 3 and path_parts[1] == "jobs":
            job_id = path_parts[2]
        elif len(path_parts) >= 2 and path_parts[0] == "embed":
            board_token = parsed.query.split("for=")[-1].split("&")[0] if "for=" in parsed.query else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.GREENHOUSE,
            platform_name="Greenhouse",
            board_token=board_token,
            job_id=job_id,
            confidence=ExtractionConfidence.HIGH,
            evidence=f"Matched Greenhouse domain: {domain}",
        )

    # 2. Lever
    if LEVER_HOST_PATTERN.search(domain):
        site_id = path_parts[0] if path_parts else None
        job_id = path_parts[1] if len(path_parts) >= 2 else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.LEVER,
            platform_name="Lever",
            board_token=site_id,
            site_id=site_id,
            job_id=job_id,
            confidence=ExtractionConfidence.HIGH,
            evidence=f"Matched Lever domain: {domain}",
        )

    # 3. Ashby
    if ASHBY_HOST_PATTERN.search(domain):
        board_token = path_parts[0] if path_parts else None
        job_id = path_parts[1] if len(path_parts) >= 2 else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.ASHBY,
            platform_name="Ashby",
            board_token=board_token,
            job_id=job_id,
            confidence=ExtractionConfidence.HIGH,
            evidence=f"Matched Ashby domain: {domain}",
        )

    # 4. USAJOBS
    if USAJOBS_HOST_PATTERN.search(domain):
        return AtsDetectionResult(
            detected_connector=ConnectorId.USAJOBS,
            platform_name="USAJOBS",
            confidence=ExtractionConfidence.HIGH,
            evidence=f"Matched USAJOBS domain: {domain}",
        )

    # 5. Workday (generic career page / schema.org)
    if WORKDAY_HOST_PATTERN.search(domain):
        return AtsDetectionResult(
            detected_connector=ConnectorId.CAREER_PAGE,
            platform_name="Workday",
            confidence=ExtractionConfidence.MEDIUM,
            evidence=f"Matched Workday domain: {domain}",
        )

    # 6. SmartRecruiters (generic career page / schema.org)
    if SMARTRECRUITERS_HOST_PATTERN.search(domain):
        return AtsDetectionResult(
            detected_connector=ConnectorId.CAREER_PAGE,
            platform_name="SmartRecruiters",
            confidence=ExtractionConfidence.MEDIUM,
            evidence=f"Matched SmartRecruiters domain: {domain}",
        )

    # Default to generic career page connector
    return AtsDetectionResult(
        detected_connector=ConnectorId.CAREER_PAGE,
        platform_name="Custom Career Portal",
        confidence=ExtractionConfidence.LOW,
        evidence=f"Generic career site on domain: {domain}",
    )


def detect_ats_from_html(html_content: str) -> Optional[AtsDetectionResult]:
    """Scan HTML page contents for embedded ATS markers."""
    if not html_content:
        return None

    lower_html = html_content.lower()

    if "greenhouse.io/embed" in lower_html or "boards.greenhouse.io" in lower_html:
        token_match = re.search(r'boards\.greenhouse\.io/(?:v1/boards/)?([a-zA-Z0-9_\-]+)', html_content)
        token = token_match.group(1) if token_match else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.GREENHOUSE,
            platform_name="Greenhouse Embedded",
            board_token=token,
            confidence=ExtractionConfidence.MEDIUM,
            evidence="Detected Greenhouse embed code in HTML",
        )

    if "jobs.lever.co" in lower_html:
        site_match = re.search(r'jobs\.lever\.co/([a-zA-Z0-9_\-]+)', html_content)
        site = site_match.group(1) if site_match else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.LEVER,
            platform_name="Lever Embedded",
            board_token=site,
            site_id=site,
            confidence=ExtractionConfidence.MEDIUM,
            evidence="Detected Lever links in HTML",
        )

    if "ashbyhq.com" in lower_html:
        token_match = re.search(r'ashbyhq\.com/([a-zA-Z0-9_\-]+)', html_content)
        token = token_match.group(1) if token_match else None
        return AtsDetectionResult(
            detected_connector=ConnectorId.ASHBY,
            platform_name="Ashby Embedded",
            board_token=token,
            confidence=ExtractionConfidence.MEDIUM,
            evidence="Detected Ashby iframe/embed in HTML",
        )

    return None
