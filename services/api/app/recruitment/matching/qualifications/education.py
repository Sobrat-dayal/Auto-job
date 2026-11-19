"""Education requirements, degree status, and practical equivalency for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    EducationMatchDetail,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.qualifications.education")

DEGREE_HIERARCHY: dict[str, int] = {
    "none": 0,
    "high_school": 1,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "doctorate": 5,
}

STEM_RELATED_FIELDS: set[str] = {
    "computer science",
    "software engineering",
    "computer engineering",
    "information technology",
    "data science",
    "electrical engineering",
    "mathematics",
    "applied mathematics",
    "statistics",
    "cybersecurity",
}


def normalize_degree(degree_str: str | None) -> str:
    """Maps degree strings to standardized levels."""
    if not degree_str:
        return "none"
    d = degree_str.lower()
    if "phd" in d or "doctor" in d:
        return "doctorate"
    if "master" in d or "msc" in d or "ms " in d or d.endswith(" ms"):
        return "master"
    if "bachelor" in d or "bsc" in d or "bs " in d or d.endswith(" bs") or "b.e." in d or "b.tech" in d:
        return "bachelor"
    if "associate" in d or "diploma" in d:
        return "associate"
    return "bachelor"  # default assumption if college degree


def evaluate_education(
    job_education_reqs: list[dict[str, Any]],
    applicant_snapshot: ApplicantSnapshotData,
    professional_years: float = 0.0,
) -> tuple[EducationMatchDetail | None, list[RequirementEvaluationResult]]:
    """Evaluates applicant educational history, graduation status, and practical equivalency."""
    if not job_education_reqs:
        return None, []

    req = job_education_reqs[0]
    req_id = req.get("id", "req_education")
    req_degree_raw = req.get("degree_level", "bachelor")
    req_degree_norm = normalize_degree(req_degree_raw)
    req_field = req.get("field_of_study", "Computer Science")
    req_status = req.get("status", "completed").lower()
    practical_waiver = req.get("practical_experience_waiver", False)
    req_years_equiv = req.get("years_experience_equivalent", 4.0)

    # 1. Find highest applicant degree
    best_degree_level = "none"
    best_edu: dict[str, Any] | None = None

    for edu in applicant_snapshot.education:
        d_norm = normalize_degree(edu.get("degree"))
        if DEGREE_HIERARCHY.get(d_norm, 0) > DEGREE_HIERARCHY.get(best_degree_level, 0):
            best_degree_level = d_norm
            best_edu = edu

    req_results: list[RequirementEvaluationResult] = []

    # If applicant has no education records at all
    if not best_edu:
        # Check if practical experience equivalency waiver applies! (Required test 134)
        if practical_waiver and professional_years >= req_years_equiv:
            match_status = RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE
            is_sat = True
            exp = (
                f"Applicant has no completed degree, but meets employer's stated practical equivalency "
                f"via {professional_years} years of verified professional experience (>= {req_years_equiv} yrs)."
            )
        else:
            match_status = RequirementMatchCategory.NOT_EVIDENCED
            is_sat = False
            exp = f"No educational history in profile to satisfy {req_degree_raw} degree requirement."

        detail = EducationMatchDetail(
            degree_level=req_degree_raw,
            field_of_study=req_field,
            applicant_degree=None,
            applicant_field=None,
            applicant_status=None,
            status_compatible=is_sat,
            field_compatible=is_sat,
            match_status=match_status,
            explanation=exp,
        )
        req_results.append(RequirementEvaluationResult(
            requirement_id=req_id,
            name=f"Degree: {req_degree_raw} in {req_field}",
            category="mandatory",
            match_category=match_status,
            applicant_claim_ref=None,
            applicant_evidence_snippet=f"{professional_years} yrs exp waiver" if is_sat else None,
            job_evidence_snippet=f"{req_degree_raw} in {req_field}",
            confidence=1.0,
            explanation=exp,
            is_satisfied=is_sat,
        ))
        return detail, req_results

    # Applicant has an educational record
    app_status = best_edu.get("academic_status", "completed").lower()
    app_field = best_edu.get("field_of_study", "").lower()
    app_degree = best_edu.get("degree", "")

    # Check status compatibility (Required test 135)
    is_graduated = app_status in ("completed", "graduated")
    is_enrolled = app_status in ("currently_enrolled", "in_progress")

    status_compatible = False
    if req_status in ("currently_enrolled", "student", "internship"):
        # Role accepts current students
        status_compatible = is_enrolled or is_graduated
    elif req_status in ("completed", "graduated"):
        # Role requires completed degree immediately
        status_compatible = is_graduated
    else:
        status_compatible = is_graduated

    # Check degree level
    level_ok = DEGREE_HIERARCHY.get(best_degree_level, 0) >= DEGREE_HIERARCHY.get(req_degree_norm, 0)

    # Check field compatibility
    field_compatible = (
        req_field.lower() in app_field
        or app_field in req_field.lower()
        or (app_field in STEM_RELATED_FIELDS and any(f in req_field.lower() for f in ("computer", "software", "stem", "technical")))
    )

    if level_ok and status_compatible and field_compatible:
        match_status = RequirementMatchCategory.DIRECTLY_SATISFIED
        is_sat = True
        explanation = f"Confirmed {best_degree_level.title()} in {best_edu.get('field_of_study')} (status: {app_status}) directly satisfies requirement."
    elif not status_compatible:
        # Enrolled student applying for role requiring completed degree
        if is_enrolled and not is_graduated:
            # Check if practical experience equivalency applies
            if practical_waiver and professional_years >= req_years_equiv:
                match_status = RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE
                is_sat = True
                explanation = (
                    f"Applicant is currently enrolled (not graduated), but satisfies practical experience "
                    f"equivalency ({professional_years} yrs >= {req_years_equiv} yrs)."
                )
            else:
                match_status = RequirementMatchCategory.KNOWN_NOT_SATISFIED
                is_sat = False
                explanation = (
                    f"Job requires completed {req_degree_raw} degree, but applicant profile confirms "
                    f"currently enrolled status with expected graduation in {best_edu.get('expected_completion', 'future')}."
                )
        else:
            match_status = RequirementMatchCategory.PARTIALLY_SUPPORTED
            is_sat = False
            explanation = f"Academic status '{app_status}' is not compatible with required status '{req_status}'."
    elif not level_ok:
        # Degree level is lower than required (e.g. Associate vs Bachelor)
        if practical_waiver and professional_years >= req_years_equiv:
            match_status = RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE
            is_sat = True
            explanation = (
                f"Applicant degree level ({best_degree_level}) is below {req_degree_norm}, but qualifies "
                f"via employer-stated practical equivalency ({professional_years} yrs >= {req_years_equiv} yrs)."
            )
        else:
            match_status = RequirementMatchCategory.KNOWN_NOT_SATISFIED
            is_sat = False
            explanation = f"Applicant holds {best_degree_level}, which does not meet required {req_degree_raw} level."
    else:
        # Field mismatch
        match_status = RequirementMatchCategory.PARTIALLY_SUPPORTED
        is_sat = False
        explanation = f"Applicant degree field '{best_edu.get('field_of_study')}' is not directly aligned with '{req_field}'."

    detail = EducationMatchDetail(
        degree_level=req_degree_raw,
        field_of_study=req_field,
        applicant_degree=app_degree,
        applicant_field=best_edu.get("field_of_study"),
        applicant_status=app_status,
        status_compatible=status_compatible,
        field_compatible=field_compatible,
        match_status=match_status,
        explanation=explanation,
    )

    req_results.append(RequirementEvaluationResult(
        requirement_id=req_id,
        name=f"{req_degree_raw.title()} in {req_field}",
        category="mandatory",
        match_category=match_status,
        applicant_claim_ref=best_edu.get("id"),
        applicant_evidence_snippet=f"{app_degree} ({app_status})",
        job_evidence_snippet=f"{req_degree_raw} in {req_field} ({req_status})",
        confidence=1.0,
        explanation=explanation,
        is_satisfied=is_sat,
    ))

    return detail, req_results
