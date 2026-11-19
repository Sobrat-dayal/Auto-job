"""Domain Verification and Hostname Parsing Engine (Stage 27)."""

import re
from urllib.parse import urlparse


# Common ATS and third-party hosting domains that DO NOT represent the employer's corporate domain
ATS_HOSTING_DOMAINS = {
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workday.com",
    "myworkdayjobs.com",
    "icims.com",
    "smartrecruiters.com",
    "jobvite.com",
    "bamboohr.com",
    "breezy.hr",
    "recruitee.com",
    "usajobs.gov",
}


def extract_domain_from_url(url: str) -> str:
    """Extract clean base domain from an arbitrary URL, handling subdomains correctly."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        netloc = parsed.netloc.lower() or parsed.path.lower()
        # Strip port
        netloc = re.sub(r":(80|443|[0-9]+)$", "", netloc)
        # Strip www, careers, jobs subdomains
        netloc = re.sub(r"^(?:www|careers|jobs|career|about|corp|work)\.", "", netloc)
        return netloc.strip()
    except Exception:
        return ""


def is_corporate_domain(domain: str) -> bool:
    """Verify whether a domain is a potential corporate domain rather than an ATS platform."""
    if not domain:
        return False
    domain_clean = domain.lower().strip()
    for ats in ATS_HOSTING_DOMAINS:
        if domain_clean == ats or domain_clean.endswith("." + ats):
            return False
    return True


def are_domains_matching(domain_a: str, domain_b: str) -> bool:
    """Check if two verified domains represent the same corporate identity."""
    clean_a = extract_domain_from_url(domain_a)
    clean_b = extract_domain_from_url(domain_b)

    if not clean_a or not clean_b:
        return False

    return clean_a == clean_b
