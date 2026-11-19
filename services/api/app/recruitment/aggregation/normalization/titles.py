"""Job Title Normalization and Seniority Preservation Engine (Stage 27)."""

import re
from typing import Optional


# Preserved seniority markers - differences here indicate distinct vacancies!
SENIORITY_LEVELS = {
    "intern": 0,
    "internship": 0,
    "apprentice": 0,
    "junior": 1,
    "associate": 1,
    "entry": 1,
    "mid": 2,
    "intermediate": 2,
    "senior": 3,
    "sr": 3,
    "staff": 4,
    "principal": 5,
    "distinguished": 6,
    "fellow": 7,
    "lead": 3,
    "manager": 4,
    "senior manager": 5,
    "director": 6,
    "senior director": 7,
    "vp": 8,
    "vice president": 8,
    "head": 6,
}


def normalize_title(title: str) -> str:
    """Produce a canonical normalized title string."""
    if not title:
        return ""
    cleaned = title.lower().strip()
    # Replace em-dashes, en-dashes, pipes, slashes with standard hyphens
    cleaned = re.sub(r"[\u2013\u2014|/\\]", " - ", cleaned)
    # Remove excessive punctuation
    cleaned = re.sub(r"[^\w\s\-+#]", " ", cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_seniority(title: str) -> Optional[str]:
    """Identify the explicit seniority tier from the title if present."""
    norm = normalize_title(title)
    tokens = norm.split()
    for s_term in sorted(SENIORITY_LEVELS.keys(), key=lambda x: -len(x)):
        if f" {s_term} " in f" {norm} ":
            return s_term
    return None


def are_seniorities_compatible(seniority_a: Optional[str], seniority_b: Optional[str]) -> bool:
    """Evaluate whether two seniority terms are compatible for vacancy merging.

    Senior vs Junior -> Incompatible!
    Senior vs Mid -> Incompatible!
    Intern vs Full-Time/Senior -> Incompatible!
    None vs Senior -> Soft compatible (one source might omit it).
    """
    if not seniority_a or not seniority_b:
        return True

    tier_a = SENIORITY_LEVELS.get(seniority_a.lower())
    tier_b = SENIORITY_LEVELS.get(seniority_b.lower())

    if tier_a is None or tier_b is None:
        return True

    # If both explicitly specify seniority and difference is > 0, they are incompatible
    # (e.g. Intern (0) vs Junior (1) is incompatible, Junior (1) vs Senior (3) is incompatible)
    return tier_a == tier_b
