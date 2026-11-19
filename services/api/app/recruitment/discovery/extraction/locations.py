"""Location and workplace arrangement extraction for job postings (Stage 26)."""

import re
from typing import Optional
from app.recruitment.discovery.contracts import ExtractedLocation


REMOTE_REGEX = re.compile(r"\b(remote|work from home|telecommute|distributed)\b", re.IGNORECASE)
HYBRID_REGEX = re.compile(r"\b(hybrid|flexible remote|partially remote)\b", re.IGNORECASE)
ONSITE_REGEX = re.compile(r"\b(on-site|onsite|in-office|in office)\b", re.IGNORECASE)


def parse_location(location_raw: Optional[str], is_remote_flag: Optional[bool] = None) -> ExtractedLocation:
    """Parse raw location string into structured ExtractedLocation model."""
    if not location_raw:
        is_remote = bool(is_remote_flag)
        return ExtractedLocation(
            is_remote=is_remote,
            workplace_type="remote" if is_remote else "unknown",
            raw_location_text="",
        )

    text = location_raw.strip()
    is_remote = bool(is_remote_flag) or bool(REMOTE_REGEX.search(text))
    is_hybrid = bool(HYBRID_REGEX.search(text))
    is_onsite = bool(ONSITE_REGEX.search(text))

    workplace_type = "hybrid" if is_hybrid else ("remote" if is_remote else ("onsite" if is_onsite else "unknown"))

    # Basic split for City, State / Country
    parts = [p.strip() for p in text.split(",") if p.strip()]
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    if len(parts) == 1:
        if not is_remote or ("remote" not in parts[0].lower()):
            city = parts[0]
    elif len(parts) == 2:
        city = parts[0]
        state_or_country = parts[1]
        if len(state_or_country) == 2 and state_or_country.isupper():
            state = state_or_country
            country = "United States"
        else:
            country = state_or_country
    elif len(parts) >= 3:
        city = parts[0]
        state = parts[1]
        country = parts[2]

    return ExtractedLocation(
        country=country,
        state_region=state,
        city=city,
        is_remote=is_remote,
        workplace_type=workplace_type,
        raw_location_text=text,
    )


# Alias
parse_location_string = parse_location
