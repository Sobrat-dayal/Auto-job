"""Confidence scoring and quality auditing for job intelligence records."""

from app.recruitment.intelligence.contracts import (
    AnalysisStatus,
    AtomicRequirement,
    EvidenceConfidence,
    JobIntelligenceRecord,
    ReviewStatus,
)


def calculate_overall_confidence(
    requirements: list[AtomicRequirement],
    has_compensation: bool,
    has_education: bool,
    has_experience: bool,
    warnings: list[str],
) -> tuple[float, AnalysisStatus, ReviewStatus]:
    """Calculate aggregate intelligence confidence, analysis status, and review status."""
    if not requirements and not has_compensation:
        return 0.2, AnalysisStatus.PARTIALLY_ANALYZED, ReviewStatus.PENDING

    # Calculate average confidence score of requirements
    if requirements:
        req_avg = sum(r.confidence_score for r in requirements) / len(requirements)
    else:
        req_avg = 0.5

    # Check for unverified or ambiguous requirements
    needs_review = any(r.needs_review for r in requirements) or len(warnings) > 0

    penalty = 0.0
    if not has_compensation:
        penalty += 0.05
    if not has_education:
        penalty += 0.05
    if not has_experience:
        penalty += 0.05
    if warnings:
        penalty += min(0.2, len(warnings) * 0.05)

    final_score = max(0.1, min(1.0, req_avg - penalty))

    if needs_review:
        status = AnalysisStatus.NEEDS_REVIEW
        rev_status = ReviewStatus.PENDING
    else:
        status = AnalysisStatus.COMPLETED
        rev_status = ReviewStatus.NOT_NEEDED

    return round(final_score, 2), status, rev_status
