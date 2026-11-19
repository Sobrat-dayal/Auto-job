"""Compensation compatibility and pay period normalization for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    CareerStrategySnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.conditions.compensation")

# Standard working hours per year for annualizing hourly rates
HOURS_PER_WORK_YEAR = 2080


def annualize_salary(amount: float | None, period: str | None) -> float | None:
    """Normalizes compensation amounts to an annualized basis."""
    if amount is None or amount <= 0:
        return None

    p = (period or "annual").lower()
    if p in ("hourly", "hour", "hr"):
        return round(amount * HOURS_PER_WORK_YEAR, 2)
    elif p in ("monthly", "month", "mo"):
        return round(amount * 12, 2)
    elif p in ("weekly", "week"):
        return round(amount * 52, 2)
    elif p in ("daily", "day"):
        return round(amount * 260, 2)
    return float(amount)


def evaluate_compensation(
    job_compensation: dict[str, Any],
    career_strategy: CareerStrategySnapshotData,
) -> tuple[RequirementEvaluationResult | None, float, bool, str | None]:
    """Evaluates salary against user career policy (Section 56, Required Test 142).
    
    Returns (result, score_factor, is_hard_violation, violation_reason).
    """
    user_min = career_strategy.min_annual_salary
    user_target = career_strategy.target_annual_salary or user_min
    user_curr = (career_strategy.salary_currency or "USD").upper()
    undisclosed_policy = career_strategy.undisclosed_salary_handling.lower()

    job_min = job_compensation.get("salary_min")
    job_max = job_compensation.get("salary_max")
    job_curr = (job_compensation.get("currency") or "USD").upper()
    job_period = job_compensation.get("pay_period", "annual")

    # Check for undisclosed compensation (Scenario 4)
    if job_min is None and job_max is None:
        if undisclosed_policy == "exclude":
            res = RequirementEvaluationResult(
                requirement_id="req_compensation",
                name="Compensation Policy",
                category="mandatory",
                match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
                confidence=1.0,
                explanation="Employer did not disclose compensation, and user policy specifies 'exclude'.",
                is_satisfied=False,
            )
            return res, 0.0, True, "Undisclosed compensation excluded by policy."
        elif undisclosed_policy == "review":
            res = RequirementEvaluationResult(
                requirement_id="req_compensation",
                name="Compensation Policy",
                category="preferred",
                match_category=RequirementMatchCategory.UNKNOWN,
                confidence=0.5,
                explanation="Employer compensation is undisclosed; review required.",
                is_satisfied=True,
            )
            return res, 0.5, False, None
        else:  # include
            res = RequirementEvaluationResult(
                requirement_id="req_compensation",
                name="Compensation Policy",
                category="preferred",
                match_category=RequirementMatchCategory.UNKNOWN,
                confidence=0.7,
                explanation="Employer compensation is undisclosed; included per user preference.",
                is_satisfied=True,
            )
            return res, 0.6, False, None

    # Currency compatibility check (Scenarios 6 & 7)
    if job_curr != user_curr:
        # Without a verified live conversion API, preserve uncertainty without inventing exchange rates
        res = RequirementEvaluationResult(
            requirement_id="req_compensation",
            name="Compensation Policy",
            category="preferred",
            match_category=RequirementMatchCategory.UNKNOWN,
            confidence=0.5,
            explanation=f"Advertised currency ({job_curr}) differs from applicant currency ({user_curr}); unverified conversion.",
            is_satisfied=True,
        )
        return res, 0.5, False, None

    # Annualize values (Scenario 5)
    annual_min = annualize_salary(job_min, job_period)
    annual_max = annualize_salary(job_max, job_period) or annual_min

    if user_min is None:
        # No minimum specified by user
        res = RequirementEvaluationResult(
            requirement_id="req_compensation",
            name="Compensation Policy",
            category="preferred",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            confidence=1.0,
            explanation=f"Advertised range: {job_curr} {annual_min:,.0f} - {annual_max:,.0f}/yr.",
            is_satisfied=True,
        )
        return res, 1.0, False, None

    # Scenario 1: Entire range meets or exceeds minimum
    if annual_min >= user_min:
        score = min(1.0, (annual_min / user_target)) if user_target else 1.0
        res = RequirementEvaluationResult(
            requirement_id="req_compensation",
            name="Compensation Policy",
            category="mandatory",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            confidence=1.0,
            explanation=f"Advertised minimum ({job_curr} {annual_min:,.0f}) meets applicant minimum ({user_min:,.0f}).",
            is_satisfied=True,
        )
        return res, max(0.9, score), False, None

    # Scenario 3: Range partially overlaps minimum
    if annual_min < user_min <= annual_max:
        overlap_ratio = (annual_max - user_min) / (annual_max - annual_min) if annual_max > annual_min else 0.5
        res = RequirementEvaluationResult(
            requirement_id="req_compensation",
            name="Compensation Policy",
            category="preferred",
            match_category=RequirementMatchCategory.PARTIALLY_SUPPORTED,
            confidence=0.8,
            explanation=(
                f"Advertised salary partially overlaps ({job_curr} {annual_min:,.0f} - {annual_max:,.0f}). "
                f"Upper end satisfies applicant minimum ({user_min:,.0f})."
            ),
            is_satisfied=True,
        )
        return res, 0.5 + 0.4 * overlap_ratio, False, None

    # Scenario 2: Entire range is below minimum
    if annual_max < user_min:
        res = RequirementEvaluationResult(
            requirement_id="req_compensation",
            name="Compensation Policy",
            category="mandatory",
            match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
            confidence=1.0,
            explanation=f"Advertised maximum ({job_curr} {annual_max:,.0f}) is below applicant minimum ({user_min:,.0f}).",
            is_satisfied=False,
        )
        return res, 0.0, True, f"Advertised maximum ({job_curr} {annual_max:,.0f}) below minimum ({user_min:,.0f})."

    return None, 1.0, False, None
