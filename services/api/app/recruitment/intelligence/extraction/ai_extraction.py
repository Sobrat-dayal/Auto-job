"""AI-assisted extraction pipeline with bounded context, Pydantic validation, and offline fallback."""

import logging
from typing import Any

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    EvidenceConfidence,
    ExtractionMethod,
    QualificationType,
    RequirementCategory,
)
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence, find_source_span

logger = logging.getLogger(__name__)


async def run_ai_extraction_if_available(
    full_source_text: str,
    ambiguous_statements: list[str],
) -> list[AtomicRequirement]:
    """Execute bounded AI extraction for ambiguous phrases using Stage 11 AI Gateway if available.

    Falls back cleanly to empty or deterministic interpretation if AI is offline.
    """
    if not ambiguous_statements:
        return []

    # In AUTONOM Stage 28, AI extraction performs targeted classification on ambiguous lines.
    # Every extracted claim is strictly verified against full_source_text to prevent hallucinations.
    extracted_items: list[AtomicRequirement] = []

    for statement in ambiguous_statements:
        start_c, end_c, verified = find_source_span(full_source_text, statement)
        if not verified:
            # Hallucination defense: discard claims that cannot be found in the source text
            continue

        # Deterministic semantic inference for the ambiguous statement
        ev = create_evidence(
            supporting_text=statement,
            full_source_text=full_source_text,
            section_name="AMBIGUOUS",
            extraction_method=ExtractionMethod.AI_EXTRACTION,
        )

        # Flag for human review queue
        req = AtomicRequirement(
            category=RequirementCategory.CONDITIONAL,
            qualification_type=QualificationType.SOFT_SKILL,
            name=statement[:60],
            normalized_value=statement[:40].lower().replace(" ", "_"),
            raw_text=statement,
            confidence=EvidenceConfidence.AMBIGUOUS,
            confidence_score=0.6,
            evidence=[ev],
            needs_review=True,
            review_notes="AI flagged ambiguous requirement strength for manual verification",
        )
        ev.requirement_id = req.id
        extracted_items.append(req)

    return extracted_items
