"""Employer Alias Normalization & Matching Engine (Stage 27)."""

import re


LEGAL_SUFFIXES = [
    r"inc",
    r"incorporated",
    r"llc",
    r"l\.l\.c",
    r"ltd",
    r"limited",
    r"corp",
    r"corporation",
    r"co",
    r"company",
    r"gmbh",
    r"ag",
    r"pvt\.?\s*ltd",
    r"private\s*limited",
    r"holdings",
    r"group",
    r"technologies",
    r"technology",
    r"solutions",
    r"services",
]

# Strips legal suffixes preceded by comma or whitespace, with optional trailing period
LEGAL_SUFFIX_REGEX = re.compile(
    r"[\s,]+(?:" + "|".join(LEGAL_SUFFIXES) + r")\.?$",
    re.IGNORECASE,
)


def normalize_employer_name(raw_name: str) -> str:
    """Normalize employer name: lowercase, strip punctuation and corporate legal suffixes."""
    if not raw_name:
        return ""
    cleaned = raw_name.strip()
    # Strip legal suffix
    cleaned = LEGAL_SUFFIX_REGEX.sub("", cleaned).strip()
    # Remove special characters
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).lower().strip()
    return cleaned


def are_employer_names_equivalent(name_a: str, name_b: str) -> bool:
    """Determine if two raw employer names normalize to the same identity."""
    norm_a = normalize_employer_name(name_a)
    norm_b = normalize_employer_name(name_b)

    if not norm_a or not norm_b:
        return False

    if norm_a == norm_b:
        return True

    # Check prefix if sufficiently long (e.g. "Google" vs "Google LLC")
    if len(norm_a) >= 5 and len(norm_b) >= 5:
        if norm_a.startswith(norm_b) or norm_b.startswith(norm_a):
            return True

    return False
