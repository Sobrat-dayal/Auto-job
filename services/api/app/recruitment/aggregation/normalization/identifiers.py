"""Job Requisition & Identifier Normalization Engine (Stage 27)."""

import re
from typing import Optional


# Patterns for extracting requisition identifiers from text, titles, or descriptions
REQ_EXPLICIT_PATTERNS = [
    re.compile(r"\b(?:REQUISITION|REQID|JOBID|REQ|JR)\b[\s\-:#]*([A-Z0-9_\-]{3,20})\b", re.IGNORECASE),
    re.compile(r"\b(?:R)[\s\-:#]*([0-9]{4,10})\b", re.IGNORECASE),
    re.compile(r"\b#[\s]*([A-Z0-9_\-]{3,15})\b", re.IGNORECASE),
]

PROVIDER_PREFIX_REGEX = re.compile(r"^(?:gh_|lever_|ashby_|usajobs_|job_|req_|req-)", re.IGNORECASE)


def normalize_requisition_id(raw_id: str) -> str:
    """Normalize requisition ID: uppercase, strip whitespace, remove redundant prefixes."""
    cleaned = raw_id.strip().upper()
    # Strip provider prefixes like "GH_", "LEVER_"
    cleaned = PROVIDER_PREFIX_REGEX.sub("", cleaned)
    # Strip leading prefixes like "REQ-", "REQ#", "JOB-"
    cleaned = re.sub(r"^(?:[A-Z0-9]+-)?(?:REQUISITION|REQ|JOB|ID|JR)[\s\-:#]*", "", cleaned)
    # Strip leading hashes
    cleaned = cleaned.lstrip("#").strip()
    return cleaned


def extract_requisition_id(
    title: str,
    description: Optional[str] = None,
    raw_id: Optional[str] = None,
) -> Optional[str]:
    """Extract a likely requisition ID from title, description, or explicit raw id."""
    # Check title first for explicit REQ patterns
    for pattern in REQ_EXPLICIT_PATTERNS:
        match = pattern.search(title)
        if match:
            extracted = match.group(1).strip()
            if len(extracted) >= 3 and not extracted.lower() in {"engineer", "developer", "manager"}:
                return normalize_requisition_id(extracted)

    # Check first 500 characters of description for explicit REQ patterns
    if description:
        intro = description[:500]
        for pattern in REQ_EXPLICIT_PATTERNS:
            match = pattern.search(intro)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) >= 3 and not extracted.lower() in {"engineer", "developer", "manager"}:
                    return normalize_requisition_id(extracted)

    # Fall back to raw_id if provided
    if raw_id and len(raw_id.strip()) >= 3:
        clean_raw = raw_id.strip()
        norm = normalize_requisition_id(clean_raw)
        if norm and len(norm) >= 3:
            return norm

    return None


def create_namespaced_identifier(provider: str, native_id: str) -> str:
    """Format a globally safe namespaced identifier (e.g. 'greenhouse:12345')."""
    return f"{provider.lower().strip()}:{native_id.strip()}"
