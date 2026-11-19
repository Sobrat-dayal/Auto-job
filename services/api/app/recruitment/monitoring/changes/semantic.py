"""Semantic content normalization and hashing to filter out superficial changes."""

from __future__ import annotations

import hashlib
import re


def normalize_content(text: str) -> str:
    """Strips HTML tags, collapses whitespace, and lowercases text for stable semantic comparison."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Collapse multiple whitespaces/newlines
    clean = re.sub(r"\s+", " ", clean).strip().lower()
    return clean


def compute_content_hash(text: str) -> str:
    """Computes SHA-256 hash of normalized text."""
    normalized = normalize_content(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_material_description_change(old_text: str, new_text: str) -> bool:
    """Determines whether a description update constitutes a material semantic change.
    Whitespace, indentation, HTML class or formatting differences return False.
    """
    old_hash = compute_content_hash(old_text or "")
    new_hash = compute_content_hash(new_text or "")
    return old_hash != new_hash
