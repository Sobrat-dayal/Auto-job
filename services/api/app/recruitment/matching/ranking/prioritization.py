"""Deterministic opportunity prioritization and tie-breaking for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    JobMatchEvaluation,
    MatchingOutcome,
    RankedOpportunityItem,
    RankingOverview,
)

logger = logging.getLogger("autonom.recruitment.matching.ranking.prioritization")

# Outcome priority tiers for queue separation
TIER_PRIORITY: dict[MatchingOutcome, int] = {
    MatchingOutcome.ELIGIBLE_AND_ALIGNED: 1,
    MatchingOutcome.CONDITIONALLY_ELIGIBLE: 2,
    MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY: 3,
    MatchingOutcome.REQUIRES_APPLICANT_REVIEW: 4,
    MatchingOutcome.MISSING_CRITICAL_INFORMATION: 5,
    MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET: 6,
    MatchingOutcome.REJECTED_BY_HARD_POLICY: 7,
    MatchingOutcome.BLOCKED_BY_AUTHORIZATION: 8,
    MatchingOutcome.JOB_UNAVAILABLE: 9,
    MatchingOutcome.MATCH_EVALUATION_FAILED: 10,
    MatchingOutcome.NOT_EVALUATED: 11,
}


def rank_opportunities(
    evaluations: list[JobMatchEvaluation],
) -> tuple[list[RankedOpportunityItem], RankingOverview]:
    """Ranks evaluations into prioritized candidate queues with deterministic tie-breaking (Sections 81, 82)."""
    # Deterministic sorting key:
    # 1. Tier Priority (Eligible first, Excluded last)
    # 2. Relevance Index (descending)
    # 3. Mandatory Coverage Ratio (descending)
    # 4. Preferred Coverage Ratio (descending)
    # 5. Canonical Job ID (stable ascending tie-breaker)
    sorted_evals = sorted(
        evaluations,
        key=lambda e: (
            TIER_PRIORITY.get(e.eligibility_outcome, 99),
            -e.relevance_index,
            -e.mandatory_coverage_ratio,
            -e.preferred_coverage_ratio,
            e.canonical_job_id,
        ),
    )

    ranked_items: list[RankedOpportunityItem] = []
    eligible_count = 0
    cond_count = 0
    review_count = 0
    unmet_count = 0
    hard_excluded_count = 0
    total_relevance = 0.0

    for idx, e in enumerate(sorted_evals, start=1):
        crit_gaps = sum(1 for g in e.gaps if g.severity.value in ("blocking", "critical_review"))
        unknowns = sum(1 for r in e.requirement_results if r.match_category.value == "unknown")

        item = RankedOpportunityItem(
            rank=idx,
            evaluation_id=e.id,
            canonical_job_id=e.canonical_job_id,
            job_title=e.job_title,
            company_name=e.company_name,
            location=e.job_location,
            work_arrangement=e.work_arrangement,
            employment_type=e.employment_type,
            eligibility_outcome=e.eligibility_outcome,
            relevance_index=e.relevance_index,
            mandatory_coverage_ratio=e.mandatory_coverage_ratio,
            preferred_coverage_ratio=e.preferred_coverage_ratio,
            critical_gaps_count=crit_gaps,
            unknowns_count=unknowns,
            application_readiness=e.application_readiness,
            posting_discovered_at=None,
            last_evaluated_at=e.evaluated_at.isoformat(),
        )
        ranked_items.append(item)

        # Overview statistics
        if e.eligibility_outcome in (MatchingOutcome.ELIGIBLE_AND_ALIGNED, MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY):
            eligible_count += 1
        elif e.eligibility_outcome == MatchingOutcome.CONDITIONALLY_ELIGIBLE:
            cond_count += 1
        elif e.eligibility_outcome in (MatchingOutcome.REQUIRES_APPLICANT_REVIEW, MatchingOutcome.MISSING_CRITICAL_INFORMATION):
            review_count += 1
        elif e.eligibility_outcome == MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET:
            unmet_count += 1
        elif e.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY:
            hard_excluded_count += 1

        total_relevance += e.relevance_index

    avg_relevance = round(total_relevance / len(evaluations), 1) if evaluations else 0.0
    latest_ts = max((e.evaluated_at.isoformat() for e in evaluations), default=None)

    overview = RankingOverview(
        total_evaluated=len(evaluations),
        eligible_and_aligned=eligible_count,
        conditionally_eligible=cond_count,
        requires_review=review_count,
        known_unmet=unmet_count,
        hard_policy_excluded=hard_excluded_count,
        average_relevance_index=avg_relevance,
        latest_evaluation_at=latest_ts,
    )

    return ranked_items, overview
