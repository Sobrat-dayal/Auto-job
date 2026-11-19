"""Matching outcome classification and hard constraint precedence for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from app.recruitment.matching.contracts import (
    ApplicationReadiness,
    GroupEvaluationResult,
    MatchingOutcome,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.eligibility.decisions")


def determine_matching_outcome(
    job_status: str,
    hard_policy_passed: bool,
    hard_policy_reason: str | None,
    atomic_results: list[RequirementEvaluationResult],
    group_results: list[GroupEvaluationResult],
    relevance_index: float,
    satisfied_alt_reqs: set[str] | None = None,
) -> tuple[MatchingOutcome, ApplicationReadiness, str]:
    """Determines structured eligibility outcome and application readiness (Sections 8, 9, 67).
    
    Enforces strict hard constraint precedence: soft scores NEVER override hard rejections.
    """
    alt_covered = {s.lower() for s in (satisfied_alt_reqs or set())}

    # 1. Job Availability Check
    if job_status.lower() in ("closed", "expired", "inactive"):
        return (
            MatchingOutcome.JOB_UNAVAILABLE,
            ApplicationReadiness.UNAVAILABLE,
            f"Job is no longer active (status: {job_status}).",
        )

    # 2. Hard Policy Restrictions (Employer blocklists, prohibited regions, compensation floors)
    if not hard_policy_passed:
        reason = hard_policy_reason or "Job violates explicit career policy restriction."
        return (
            MatchingOutcome.REJECTED_BY_HARD_POLICY,
            ApplicationReadiness.HARD_POLICY_EXCLUDED,
            f"Excluded by hard policy: {reason}",
        )

    # 3. Check for failed logical groups (e.g. AND group with missing mandatory skill)
    for g in group_results:
        if not g.is_satisfied and not g.is_unknown:
            return (
                MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET,
                ApplicationReadiness.INELIGIBLE,
                f"Mandatory requirement group failed: {g.explanation}",
            )

    # 4. Check atomic mandatory requirements (excluding alternatives covered by satisfied OR groups)
    mandatory_reqs = [
        r for r in atomic_results
        if r.category == "mandatory" and r.requirement_id.lower() not in alt_covered and r.name.lower() not in alt_covered
    ]
    known_unmet = [
        r for r in mandatory_reqs
        if not r.is_satisfied and r.match_category != RequirementMatchCategory.UNKNOWN
    ]
    unknowns = [r for r in mandatory_reqs if r.match_category == RequirementMatchCategory.UNKNOWN]
    conditional_alts = [r for r in mandatory_reqs if r.match_category == RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE]

    # If any mandatory requirement is known not satisfied
    if known_unmet:
        unmet_names = [r.name for r in known_unmet]
        return (
            MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET,
            ApplicationReadiness.INELIGIBLE,
            f"Mandatory requirements not met: {', '.join(unmet_names)}.",
        )

    # If any mandatory requirement is unknown (e.g. work authorization unknown)
    if unknowns:
        unknown_names = [r.name for r in unknowns]
        return (
            MatchingOutcome.REQUIRES_APPLICANT_REVIEW,
            ApplicationReadiness.REQUIRES_REVIEW,
            f"Mandatory requirements require review: {', '.join(unknown_names)}.",
        )

    # Check for conditional eligibility
    if conditional_alts:
        return (
            MatchingOutcome.CONDITIONALLY_ELIGIBLE,
            ApplicationReadiness.READY_FOR_PREPARATION,
            "All mandatory requirements met, including accepted practical/alternative routes.",
        )

    # All mandatory requirements satisfied directly
    if relevance_index >= 60.0:
        return (
            MatchingOutcome.ELIGIBLE_AND_ALIGNED,
            ApplicationReadiness.READY_FOR_PREPARATION,
            f"Fully satisfies mandatory requirements and aligns with preferences (Relevance: {relevance_index:.1f}/100).",
        )
    else:
        return (
            MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
            ApplicationReadiness.READY_FOR_PREPARATION,
            f"Meets mandatory requirements but has lower preference alignment (Relevance: {relevance_index:.1f}/100).",
        )
