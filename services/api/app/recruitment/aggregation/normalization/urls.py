"""Conservative Job URL Normalization Engine (Stage 27)."""

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


# Tracking parameters that are safe to discard
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "reference",
    "source",
    "gh_src",
    "lever-source",
    "ashby_jid",  # sometimes tracking referrer
    "fbclid",
    "gclid",
    "msclkid",
    "mc_cid",
    "mc_eid",
    "trk",
    "s",
}

# Parameters that often carry posting identity and MUST NEVER be stripped
IDENTITY_PARAMS = {
    "id",
    "job_id",
    "jobid",
    "jid",
    "gh_jid",
    "req",
    "req_id",
    "requisition",
    "posting_id",
    "code",
    "p",
}


def normalize_job_url(raw_url: str) -> str:
    """Normalize a job posting URL conservatively.

    - Downcases scheme and netloc.
    - Strips common marketing/campaign tracking parameters.
    - Preserves parameters that define the job identity.
    - Strips fragment identifiers unless they appear to be client-side route posting IDs.
    """
    if not raw_url:
        return ""

    try:
        parsed = urlparse(raw_url.strip())
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()

        # Remove trailing port 80/443
        netloc = re.sub(r":(80|443)$", "", netloc)
        # Remove redundant www. prefix for consistent comparison
        cleaned_netloc = re.sub(r"^www\.", "", netloc)

        # Clean query parameters
        query_dict = parse_qs(parsed.query, keep_blank_values=False)
        cleaned_params = {}
        for key, vals in query_dict.items():
            key_lower = key.lower()
            # If it's a known identity param or not a tracking param, preserve it
            if key_lower in IDENTITY_PARAMS or key_lower not in TRACKING_PARAMS:
                cleaned_params[key] = vals

        # Re-encode query params sorted for canonical consistency
        cleaned_query = urlencode(cleaned_params, doseq=True)

        # Normalize path: collapse duplicate slashes and strip trailing slash
        path = re.sub(r"/+", "/", parsed.path)
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]

        # Check fragment: preserve if it has a route or ID like #/jobs/123
        fragment = ""
        if parsed.fragment and ("/" in parsed.fragment or any(c.isdigit() for c in parsed.fragment)):
            fragment = parsed.fragment

        return urlunparse((scheme, cleaned_netloc, path, parsed.params, cleaned_query, fragment))
    except Exception:
        return raw_url.strip()
