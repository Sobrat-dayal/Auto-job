"""Analysis versioning, content hashing, and reanalysis triggers."""

import hashlib
from typing import Any


def compute_description_hash(cleaned_description_text: str) -> str:
    """Compute SHA-256 hash of cleaned job description."""
    return hashlib.sha256(cleaned_description_text.strip().encode("utf-8")).hexdigest()


def is_reanalysis_needed(existing_hash: str | None, new_description_text: str) -> bool:
    """Determine whether a job description has changed materially, requiring reanalysis."""
    if not existing_hash:
        return True
    new_hash = compute_description_hash(new_description_text)
    return existing_hash != new_hash
