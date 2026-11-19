"""Source span mapping, quotation hashing, and provenance tracking."""

import hashlib
import re

from app.recruitment.intelligence.contracts import ExtractionMethod, RequirementEvidence


def compute_quote_hash(quote: str) -> str:
    """Return SHA-256 hash of normalized quotation string."""
    normalized = " ".join(quote.lower().strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_source_span(full_text: str, target_quote: str) -> tuple[int, int, bool]:
    """Find the exact character start and end index of a target quote in full text.

    Returns (start_char, end_char, verified_in_source).
    """
    if not full_text or not target_quote:
        return 0, 0, False

    clean_quote = target_quote.strip()
    if not clean_quote:
        return 0, 0, False

    # 1. Exact match
    idx = full_text.find(clean_quote)
    if idx != -1:
        return idx, idx + len(clean_quote), True

    # 2. Case-insensitive match
    lower_full = full_text.lower()
    lower_quote = clean_quote.lower()
    idx = lower_full.find(lower_quote)
    if idx != -1:
        return idx, idx + len(clean_quote), True

    # 3. Normalized whitespace regex match
    escaped_tokens = [re.escape(token) for token in clean_quote.split()]
    if escaped_tokens:
        pattern = r"\s+".join(escaped_tokens)
        match = re.search(pattern, full_text, flags=re.IGNORECASE)
        if match:
            return match.start(), match.end(), True

    # 4. Fallback: quote was not found verbatim in the source description
    return 0, 0, False


def create_evidence(
    supporting_text: str,
    full_source_text: str,
    requirement_id: str | None = None,
    section_name: str = "MINIMUM_QUALIFICATIONS",
    extraction_method: ExtractionMethod = ExtractionMethod.DETERMINISTIC_RULES,
) -> RequirementEvidence:
    """Construct a verified RequirementEvidence record."""
    start_char, end_char, verified = find_source_span(full_source_text, supporting_text)
    quote_hash = compute_quote_hash(supporting_text)

    return RequirementEvidence(
        requirement_id=requirement_id,
        section_name=section_name,
        supporting_text=supporting_text.strip(),
        start_char=start_char,
        end_char=end_char,
        quote_hash=quote_hash,
        extraction_method=extraction_method,
        verified_in_source=verified,
    )
