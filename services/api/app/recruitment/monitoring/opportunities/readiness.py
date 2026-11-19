"""Stage 31 Application Preparation Readiness Evaluator."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional
from app.recruitment.matching.contracts import JobMatchEvaluation, MatchingOutcome
from app.recruitment.monitoring.contracts import (
    OpportunityPreparationCandidate,
    OpportunityPriority,
)


def evaluate_preparation_readiness(
    canonical_job: dict[str, Any],
    evaluation: Optional[JobMatchEvaluation],
    priority: OpportunityPriority,
) -> tuple[bool, Optional[OpportunityPreparationCandidate]]:
    """Evaluates whether an opportunity is eligible and ready for Stage 31 Application Preparation."""
    if not canonical_job:
        return False, None

    status = (canonical_job.get("status") or "active").lower()
    if status in ("closed", "expired", "removed"):
        return False, None

    if not evaluation:
        return False, None

    # Must pass hard policies
    if not evaluation.hard_policy_passed:
        return False, None

    outcome = getattr(evaluation, "eligibility_outcome", None) or getattr(evaluation, "outcome", None)

    # Blocking outcomes prevent preparation
    blocking_outcomes = {
        MatchingOutcome.REJECTED_BY_HARD_POLICY,
        MatchingOutcome.BLOCKED_BY_AUTHORIZATION,
        MatchingOutcome.JOB_UNAVAILABLE,
        MatchingOutcome.MATCH_EVALUATION_FAILED,
        MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET,
    }
    if outcome in blocking_outcomes:
        return False, None

    # Check for blocking gaps
    gaps = getattr(evaluation, "gaps", None) or []
    has_blocking_gap = False
    for gap in gaps:
        sev = getattr(gap, "severity", None)
        sev_str = sev.value if hasattr(sev, "value") else str(sev)
        if str(sev_str).lower() == "blocking":
            has_blocking_gap = True
            break

    if has_blocking_gap:
        return False, None

    relevance_score = getattr(evaluation, "relevance_index", None)
    if relevance_score is None:
        relevance_score = getattr(evaluation, "overall_score", 0.0)

    profile_id = getattr(evaluation, "profile_id", None) or getattr(evaluation, "applicant_profile_id", "")
    outcome_str = outcome.value if hasattr(outcome, "value") else str(outcome)

    missing_items = getattr(evaluation, "missing_information", None) or getattr(evaluation, "uncertain_requirements", None) or []
    missing_names = [getattr(m, "requirement_name", str(m)) for m in missing_items]

    raw_reviews = getattr(evaluation, "review_requests", None) or getattr(evaluation, "review_items", None) or []
    formatted_reviews = []
    for r in raw_reviews:
        if hasattr(r, "model_dump"):
            formatted_reviews.append(r.model_dump(mode="json"))
        elif isinstance(r, dict):
            formatted_reviews.append(r)
        else:
            formatted_reviews.append({"detail": str(r)})

    # Build Stage 31 Handoff Candidate contract
    candidate = OpportunityPreparationCandidate(
        canonical_job_id=canonical_job["id"],
        canonical_job_version="v1",
        job_title=canonical_job.get("title") or canonical_job.get("job_title") or "Unknown Title",
        company_name=canonical_job.get("company") or canonical_job.get("company_name") or "Unknown Employer",
        application_url=canonical_job.get("application_url") or "",
        applicant_profile_id=profile_id,
        applicant_profile_version="v1",
        job_intelligence_version="v1",
        match_evaluation_id=evaluation.id,
        relevance_score=relevance_score,
        eligibility_outcome=outcome_str,
        career_strategy_id=getattr(evaluation, "career_strategy_id", None),
        policy_version=1,
        priority=priority,
        current_job_status=status,
        deadline=None,
        missing_information=missing_names,
        required_reviews=formatted_reviews,
        ready_for_preparation=True,
        generated_at=datetime.now(UTC),
    )

    return True, candidate
