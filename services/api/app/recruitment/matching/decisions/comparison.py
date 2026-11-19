"""Multi-job side-by-side comparison matrix for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import JobComparisonMatrix, JobMatchEvaluation

logger = logging.getLogger("autonom.recruitment.matching.decisions.comparison")


def build_comparison_matrix(evaluations: list[JobMatchEvaluation]) -> JobComparisonMatrix:
    """Builds an aligned attribute comparison matrix across multiple evaluated jobs (Section 92)."""
    items: list[dict[str, Any]] = []

    for ev in evaluations:
        items.append({
            "evaluation_id": ev.id,
            "canonical_job_id": ev.canonical_job_id,
            "title": ev.job_title,
            "company": ev.company_name,
            "location": ev.job_location or "Unspecified",
            "work_arrangement": ev.work_arrangement or "Unspecified",
            "employment_type": ev.employment_type or "Full-Time",
            "eligibility_outcome": ev.eligibility_outcome.value,
            "relevance_index": ev.relevance_index,
            "mandatory_coverage": f"{int(ev.mandatory_coverage_ratio * 100)}%",
            "preferred_coverage": f"{int(ev.preferred_coverage_ratio * 100)}%",
            "critical_gaps_count": sum(1 for g in ev.gaps if g.severity.value in ("blocking", "critical_review")),
            "compensation": ev.eligibility_detail.compensation_compatibility,
            "work_authorization": ev.eligibility_detail.work_authorization_status,
            "hard_policy_passed": ev.hard_policy_passed,
            "readiness": ev.application_readiness.value,
        })

    return JobComparisonMatrix(
        canonical_job_ids=[ev.canonical_job_id for ev in evaluations],
        items=items,
    )
