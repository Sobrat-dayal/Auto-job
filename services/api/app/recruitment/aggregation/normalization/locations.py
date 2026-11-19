"""Location and Workplace Arrangement Normalization Engine (Stage 27)."""

import re
from typing import Optional


def normalize_workplace_type(raw_type: Optional[str], raw_text: Optional[str] = None) -> str:
    """Classify work arrangement into remote, hybrid, onsite, or flexible."""
    combined = f"{raw_type or ''} {raw_text or ''}".lower()
    if "remote" in combined or "anywhere" in combined or "virtual" in combined or "work from home" in combined:
        return "remote"
    if "hybrid" in combined or "flexible" in combined:
        return "hybrid"
    if "onsite" in combined or "on-site" in combined or "in-office" in combined:
        return "onsite"
    return "flexible"


def are_locations_compatible(
    loc_a: Optional[str],
    workplace_a: Optional[str],
    loc_b: Optional[str],
    workplace_b: Optional[str],
) -> tuple[bool, str]:
    """Determine whether two location records are compatible for the same vacancy.

    Returns (is_compatible, reason).
    """
    wp_a = normalize_workplace_type(workplace_a, loc_a)
    wp_b = normalize_workplace_type(workplace_b, loc_b)

    # Both remote -> highly compatible
    if wp_a == "remote" and wp_b == "remote":
        return True, "Both postings are remote"

    clean_a = re.sub(r"[^\w\s]", "", (loc_a or "").lower()).strip()
    clean_b = re.sub(r"[^\w\s]", "", (loc_b or "").lower()).strip()

    if not clean_a or not clean_b:
        return True, "Missing location data on one side"

    # Token overlap check (e.g. "San Francisco, CA" and "San Francisco")
    tokens_a = set(clean_a.split())
    tokens_b = set(clean_b.split())
    intersection = tokens_a.intersection(tokens_b)

    if intersection:
        return True, f"Shared location tokens: {', '.join(intersection)}"

    # If completely different cities/countries and neither is remote, incompatible!
    if wp_a != "remote" and wp_b != "remote":
        return False, f"Contradictory physical locations: '{loc_a}' vs '{loc_b}'"

    return True, "Location compatible under remote/hybrid variance"
