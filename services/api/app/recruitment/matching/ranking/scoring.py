"""Deterministic relevance index and score component calculations for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    DimensionScore,
    RelevanceIndexBreakdown,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    RubricConfig,
)

logger = logging.getLogger("autonom.recruitment.matching.ranking.scoring")


def compute_relevance_index(
    atomic_results: list[RequirementEvaluationResult],
    job_metadata: dict[str, Any],
    career_strategy: CareerStrategySnapshotData,
    applicant_snapshot: ApplicantSnapshotData,
    compensation_factor: float,
    professional_years: float,
    rubric: RubricConfig,
    satisfied_alt_reqs: set[str] | None = None,
) -> tuple[RelevanceIndexBreakdown, float, float, float, float]:
    """Computes deterministic 0–100 internal relevance index across rubric dimensions (Sections 69-74).
    
    Returns (breakdown, relevance_index, mandatory_ratio, preferred_ratio, uncertainty_ratio).
    """
    weights = rubric.weights
    alt_covered = {s.lower() for s in (satisfied_alt_reqs or set())}

    # 1. Qualification Alignment (Mandatory requirements)
    mandatory_reqs = [
        r for r in atomic_results
        if r.category == "mandatory" and (r.is_satisfied or (r.requirement_id.lower() not in alt_covered and r.name.lower() not in alt_covered))
    ]
    if mandatory_reqs:
        sat_mandatory = sum(1 for r in mandatory_reqs if r.is_satisfied)
        mandatory_ratio = round(sat_mandatory / len(mandatory_reqs), 3)
    else:
        mandatory_ratio = 1.0

    score_dim_qual = DimensionScore(
        dimension_id="qualification_alignment",
        name="Mandatory Qualification Alignment",
        raw_score=mandatory_ratio,
        weight=weights.get("qualification_alignment", 0.25),
        weighted_score=round(mandatory_ratio * weights.get("qualification_alignment", 0.25), 4),
        max_possible_weighted_score=weights.get("qualification_alignment", 0.25),
        is_observed=True,
        explanation=f"{int(mandatory_ratio * 100)}% of mandatory requirements satisfied ({len(mandatory_reqs)} evaluated).",
    )

    # 2. Preferred Skills Coverage
    preferred_reqs = [r for r in atomic_results if r.category == "preferred"]
    if preferred_reqs:
        sat_preferred = sum(1 for r in preferred_reqs if r.is_satisfied)
        preferred_ratio = round(sat_preferred / len(preferred_reqs), 3)
        pref_observed = True
    else:
        preferred_ratio = 1.0
        pref_observed = False

    score_dim_pref = DimensionScore(
        dimension_id="preferred_skills",
        name="Preferred Skills Coverage",
        raw_score=preferred_ratio,
        weight=weights.get("preferred_skills", 0.15),
        weighted_score=round(preferred_ratio * weights.get("preferred_skills", 0.15), 4) if pref_observed else 0.0,
        max_possible_weighted_score=weights.get("preferred_skills", 0.15),
        is_observed=pref_observed,
        explanation=f"{int(preferred_ratio * 100)}% of preferred qualifications satisfied ({len(preferred_reqs)} evaluated)." if pref_observed else "No preferred skills requested in posting.",
    )

    # 3. Role Family Alignment
    job_role = (job_metadata.get("role_family") or job_metadata.get("title") or "").lower()
    target_roles = [rf.lower() for rf in career_strategy.role_families]
    if any(tr in job_role or job_role in tr for tr in target_roles) if target_roles else True:
        role_score = 1.0
        role_exp = f"Role '{job_metadata.get('title')}' directly matches career strategy target roles."
    else:
        role_score = 0.3
        role_exp = f"Role '{job_metadata.get('title')}' is outside primary target role families."

    score_dim_role = DimensionScore(
        dimension_id="role_family",
        name="Target Role Family Alignment",
        raw_score=role_score,
        weight=weights.get("role_family", 0.15),
        weighted_score=round(role_score * weights.get("role_family", 0.15), 4),
        max_possible_weighted_score=weights.get("role_family", 0.15),
        is_observed=True,
        explanation=role_exp,
    )

    # 4. Experience Duration
    req_years = job_metadata.get("min_years_experience")
    if req_years and req_years > 0:
        exp_score = min(1.0, round(professional_years / req_years, 2))
        exp_text = f"Applicant has {professional_years} yrs of required {req_years}+ yrs."
        exp_observed = True
    else:
        exp_score = 1.0
        exp_text = "No minimum professional tenure mandated."
        exp_observed = False

    score_dim_exp = DimensionScore(
        dimension_id="experience_duration",
        name="Experience Tenure Alignment",
        raw_score=exp_score,
        weight=weights.get("experience_duration", 0.10),
        weighted_score=round(exp_score * weights.get("experience_duration", 0.10), 4) if exp_observed else 0.0,
        max_possible_weighted_score=weights.get("experience_duration", 0.10),
        is_observed=exp_observed,
        explanation=exp_text,
    )

    # 5. Work Arrangement / Location Alignment
    job_wa = (job_metadata.get("work_arrangement") or "onsite").lower()
    pref_wa = [wa.lower() for wa in career_strategy.work_arrangements]
    if job_wa in pref_wa or "any" in pref_wa or not pref_wa:
        wa_score = 1.0
        wa_text = f"Work arrangement '{job_wa}' aligns with user preferences."
    elif "hybrid" in job_wa and "remote" in pref_wa:
        wa_score = 0.5
        wa_text = "Hybrid arrangement partially compatible with remote preference."
    else:
        wa_score = 0.2
        wa_text = f"Work arrangement '{job_wa}' differs from preferred arrangements ({pref_wa})."

    score_dim_wa = DimensionScore(
        dimension_id="work_arrangement",
        name="Work Arrangement Alignment",
        raw_score=wa_score,
        weight=weights.get("work_arrangement", 0.10),
        weighted_score=round(wa_score * weights.get("work_arrangement", 0.10), 4),
        max_possible_weighted_score=weights.get("work_arrangement", 0.10),
        is_observed=True,
        explanation=wa_text,
    )

    # 6. Compensation Preference
    has_comp = bool(job_metadata.get("has_disclosed_compensation", True))
    score_dim_comp = DimensionScore(
        dimension_id="compensation",
        name="Compensation Alignment",
        raw_score=round(compensation_factor, 2),
        weight=weights.get("compensation", 0.10),
        weighted_score=round(compensation_factor * weights.get("compensation", 0.10), 4) if has_comp else 0.0,
        max_possible_weighted_score=weights.get("compensation", 0.10),
        is_observed=has_comp,
        explanation=f"Compensation alignment factor: {int(compensation_factor * 100)}%." if has_comp else "Undisclosed compensation in posting.",
    )

    # 7. Employer Preference
    company = (job_metadata.get("company") or "").lower()
    pref_employers = [pe.lower() for pe in career_strategy.preferred_employers]
    if pref_employers and any(pe in company or company in pe for pe in pref_employers):
        emp_score = 1.0
        emp_text = f"Employer '{job_metadata.get('company')}' is in preferred employers list."
    else:
        emp_score = 0.5
        emp_text = f"Employer '{job_metadata.get('company')}' has neutral preference."

    score_dim_emp = DimensionScore(
        dimension_id="employer_preference",
        name="Employer Brand Preference",
        raw_score=emp_score,
        weight=weights.get("employer_preference", 0.05),
        weighted_score=round(emp_score * weights.get("employer_preference", 0.05), 4),
        max_possible_weighted_score=weights.get("employer_preference", 0.05),
        is_observed=True,
        explanation=emp_text,
    )

    # 8. Posting Freshness
    discovered_at_str = job_metadata.get("discovered_at")
    if discovered_at_str:
        try:
            disc_dt = datetime.fromisoformat(discovered_at_str.replace("Z", "+00:00"))
            days_old = max(0, (datetime.now(UTC) - disc_dt).days)
            freshness_score = max(0.2, round(1.0 - (days_old / 60.0), 2))
            freshness_text = f"Discovered {days_old} days ago (freshness factor: {freshness_score})."
        except Exception:
            freshness_score = 0.8
            freshness_text = "Recent posting."
    else:
        freshness_score = 0.8
        freshness_text = "Recent posting."

    score_dim_fresh = DimensionScore(
        dimension_id="posting_freshness",
        name="Posting Freshness",
        raw_score=freshness_score,
        weight=weights.get("posting_freshness", 0.10),
        weighted_score=round(freshness_score * weights.get("posting_freshness", 0.10), 4),
        max_possible_weighted_score=weights.get("posting_freshness", 0.10),
        is_observed=True,
        explanation=freshness_text,
    )

    dimensions = [
        score_dim_qual,
        score_dim_pref,
        score_dim_role,
        score_dim_exp,
        score_dim_wa,
        score_dim_comp,
        score_dim_emp,
        score_dim_fresh,
    ]

    total_weight = sum(d.weight for d in dimensions if d.is_observed)
    total_weighted_score = sum(d.weighted_score for d in dimensions if d.is_observed)

    relevance_index = round((total_weighted_score / total_weight) * 100.0, 1) if total_weight > 0 else 0.0
    relevance_index = max(0.0, min(100.0, relevance_index))

    # Evidence coverage & uncertainty
    total_reqs = len(atomic_results)
    unknown_reqs = sum(1 for r in atomic_results if r.match_category == RequirementMatchCategory.UNKNOWN)
    evidence_completeness = round((total_reqs - unknown_reqs) / total_reqs, 3) if total_reqs > 0 else 1.0
    total_dims = len(dimensions)
    unobserved_dims = sum(1 for d in dimensions if not d.is_observed)
    uncertainty_ratio = round((unknown_reqs + unobserved_dims) / (total_reqs + total_dims), 3) if (total_reqs + total_dims) > 0 else 0.0

    breakdown = RelevanceIndexBreakdown(
        relevance_index=relevance_index,
        total_weight_observed=round(total_weight, 3),
        dimensions=dimensions,
        missing_dimensions=[d.dimension_id for d in dimensions if not d.is_observed],
        formula_explanation="Transparent weighted sum normalized to 0–100 scale. Internal alignment metric only.",
    )

    return breakdown, relevance_index, mandatory_ratio, preferred_ratio, uncertainty_ratio
