"""Employer Organizational Relationships & Staffing Agency Detection (Stage 27)."""

from typing import Optional
from app.recruitment.aggregation.contracts import OrganizationType


# Well-known staffing, recruiting, and employer-of-record intermediaries
KNOWN_STAFFING_AGENCIES = {
    "robert half",
    "teksystems",
    "randstad",
    "kelly services",
    "adecco",
    "aerotek",
    "kforce",
    "insight global",
    "hays",
    "manpower",
    "beacon hill",
    "modis",
    "cybercoders",
    "apex systems",
    "motion recruitment",
    "dice",
    "allegis",
}


def classify_organization_type(employer_name: str, description: Optional[str] = None) -> OrganizationType:
    """Classify whether an organization is a direct employer or recruiting intermediary."""
    clean_name = employer_name.lower().strip()
    for agency in KNOWN_STAFFING_AGENCIES:
        if agency in clean_name:
            return OrganizationType.STAFFING_AGENCY

    if description:
        desc_lower = description.lower()
        if "our client" in desc_lower or "on behalf of our client" in desc_lower or "staffing partner" in desc_lower:
            return OrganizationType.STAFFING_AGENCY

    return OrganizationType.DIRECT_EMPLOYER
