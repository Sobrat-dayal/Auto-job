"""Hallucination defense verifying every extracted requirement against source text."""

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    EvidenceConfidence,
    RequirementEvidence,
)
from app.recruitment.intelligence.preprocessing.source_offsets import find_source_span


def verify_requirement_provenance(
    requirement: AtomicRequirement,
    full_source_text: str,
) -> tuple[bool, str | None]:
    """Verify that every evidence span in the requirement exists verbatim in source text.

    Returns (is_valid, failure_reason).
    """
    if not requirement.evidence:
        # If there is no evidence provided, mark as unverified inference
        requirement.confidence = EvidenceConfidence.NO_EVIDENCE
        requirement.confidence_score = 0.2
        requirement.needs_review = True
        return False, "Missing supporting text evidence"

    for ev in requirement.evidence:
        start_c, end_c, verified = find_source_span(full_source_text, ev.supporting_text)
        ev.verified_in_source = verified
        ev.start_char = start_c
        ev.end_char = end_c

        if not verified:
            # Evidence cannot be found in the raw text -> Hallucination detected
            requirement.confidence = EvidenceConfidence.WEAK_INFERENCE
            requirement.confidence_score = 0.3
            requirement.needs_review = True
            requirement.review_notes = (
                f"Hallucination defense warning: Supporting quote '{ev.supporting_text[:40]}...' "
                f"was not found in source text."
            )
            return False, f"Supporting quote not found in source: {ev.supporting_text[:40]}"

    return True, None


def audit_job_evidence(
    requirements: list[AtomicRequirement],
    full_source_text: str,
) -> list[AtomicRequirement]:
    """Audit a list of requirements, updating provenance and flagging unverifiable claims."""
    verified_list: list[AtomicRequirement] = []

    for req in requirements:
        is_valid, reason = verify_requirement_provenance(req, full_source_text)
        if is_valid:
            req.confidence = EvidenceConfidence.EXPLICIT_VERIFIED_SOURCE
            req.confidence_score = 1.0
        verified_list.append(req)

    return verified_list
