"""Professional experience duration and category evaluation for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    ExperienceMatchDetail,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.qualifications.experience")


def parse_date(date_str: str | None, is_end: bool = False) -> datetime:
    """Parses date string supporting YYYY, YYYY-MM, YYYY-MM-DD, or current."""
    if not date_str or date_str.lower() in ("present", "current", "now"):
        return datetime.now(UTC)

    parts = date_str.strip().split("-")
    try:
        if len(parts) == 1:
            year = int(parts[0])
            month = 12 if is_end else 1
            day = 31 if is_end else 1
            return datetime(year, month, day, tzinfo=UTC)
        elif len(parts) == 2:
            year = int(parts[0])
            month = int(parts[1])
            day = 28 if is_end else 1
            return datetime(year, month, day, tzinfo=UTC)
        elif len(parts) >= 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return datetime(year, month, day, tzinfo=UTC)
    except Exception:
        pass
    return datetime.now(UTC)


def calculate_non_overlapping_duration(roles: list[dict[str, Any]]) -> tuple[float, int, bool]:
    """Calculates total elapsed professional years without double-counting overlapping positions.
    
    Returns (years, total_months, has_overlap).
    """
    intervals: list[tuple[datetime, datetime]] = []

    for r in roles:
        emp_type = r.get("employment_type", "full_time").lower()
        # Only full_time and contract count towards formal professional employment
        if emp_type in ("full_time", "contract", "permanent"):
            start = parse_date(r.get("start_date"), is_end=False)
            end = parse_date(r.get("end_date"), is_end=True)
            if end >= start:
                intervals.append((start, end))

    if not intervals:
        return 0.0, 0, False

    # Sort intervals by start date
    intervals.sort(key=lambda x: x[0])

    merged: list[tuple[datetime, datetime]] = []
    has_overlap = False

    current_start, current_end = intervals[0]
    for start, end in intervals[1:]:
        if start <= current_end:
            # Overlapping intervals detected
            has_overlap = True
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))

    total_days = sum((end - start).days for start, end in merged)
    years = round(total_days / 365.25, 2)
    months = int(round(total_days / 30.44))

    return years, months, has_overlap


def evaluate_experience(
    job_experience_reqs: list[dict[str, Any]],
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[ExperienceMatchDetail | None, list[RequirementEvaluationResult]]:
    """Evaluates applicant experience duration against job requirements, strictly separating academic projects."""
    if not job_experience_reqs:
        return None, []

    req = job_experience_reqs[0]
    req_id = req.get("id", "req_experience_duration")
    min_years = req.get("min_years")
    max_years = req.get("max_years")
    domain = req.get("domain")
    entry_level_waiver = req.get("entry_level_waiver", False)

    # 1. Calculate professional employment duration
    prof_years, prof_months, has_overlap = calculate_non_overlapping_duration(applicant_snapshot.experience)

    # 2. Count internships and academic projects
    internship_months = 0
    for exp in applicant_snapshot.experience:
        if exp.get("employment_type", "").lower() == "internship":
            s = parse_date(exp.get("start_date"), is_end=False)
            e = parse_date(exp.get("end_date"), is_end=True)
            internship_months += max(1, int((e - s).days / 30.44))

    academic_projects = [p for p in applicant_snapshot.projects if p.get("category", "").lower() == "academic"]
    academic_project_count = len(academic_projects)

    # 3. Determine match category
    req_results: list[RequirementEvaluationResult] = []

    if entry_level_waiver or (min_years is None or min_years <= 0):
        match_status = RequirementMatchCategory.DIRECTLY_SATISFIED
        is_sat = True
        explanation = f"Entry-level role or no minimum professional experience required ({prof_years} yrs recorded)."
    elif prof_years >= min_years:
        match_status = RequirementMatchCategory.DIRECTLY_SATISFIED
        is_sat = True
        overlap_note = " (non-overlapping elapsed time verified)" if has_overlap else ""
        explanation = f"Applicant has {prof_years} years of verified professional experience, satisfying {min_years}+ yrs requirement{overlap_note}."
    elif prof_years > 0 or internship_months > 0:
        match_status = RequirementMatchCategory.PARTIALLY_SUPPORTED
        is_sat = False
        intern_note = f" plus {internship_months} months internship" if internship_months > 0 else ""
        explanation = (
            f"Applicant has {prof_years} years professional experience{intern_note}, "
            f"which is less than the required {min_years} years."
        )
    elif academic_project_count > 0:
        # Crucial: Academic projects must NOT be equated to professional employment!
        match_status = RequirementMatchCategory.RELATED_EXPERIENCE_ONLY
        is_sat = False
        explanation = (
            f"Applicant has {academic_project_count} academic project(s), but lacks verified "
            f"full-time professional employment required for this role ({min_years}+ yrs)."
        )
    else:
        match_status = RequirementMatchCategory.NOT_EVIDENCED
        is_sat = False
        explanation = f"No verified professional employment history found in profile to satisfy {min_years}+ yrs requirement."

    detail = ExperienceMatchDetail(
        required_min_years=min_years,
        required_max_years=max_years,
        required_domain=domain,
        calculated_professional_years=prof_years,
        total_calendar_months_non_overlapping=prof_months,
        has_overlapping_roles=has_overlap,
        internship_months=internship_months,
        academic_project_count=academic_project_count,
        match_status=match_status,
        explanation=explanation,
    )

    req_result = RequirementEvaluationResult(
        requirement_id=req_id,
        name=f"Professional Experience ({min_years}+ years)" if min_years else "Experience",
        category="mandatory",
        match_category=match_status,
        applicant_claim_ref=applicant_snapshot.experience[0].get("id") if applicant_snapshot.experience else None,
        applicant_evidence_snippet=f"{prof_years} yrs professional, {internship_months} mo internship",
        job_evidence_snippet=f"{min_years}+ yrs experience",
        confidence=1.0,
        explanation=explanation,
        is_satisfied=is_sat,
    )
    req_results.append(req_result)

    return detail, req_results
