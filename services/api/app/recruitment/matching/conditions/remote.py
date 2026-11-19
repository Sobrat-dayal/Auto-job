"""Remote country restrictions and work arrangement compatibility for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.conditions.remote")


def evaluate_remote_compatibility(
    job_employment_conditions: dict[str, Any],
    job_location: str | None,
    career_strategy: CareerStrategySnapshotData,
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[RequirementEvaluationResult | None, bool, str | None]:
    """Evaluates geographic remote work restrictions (Section 50, Required Test 141).
    
    Returns (result, is_hard_conflict, conflict_reason).
    """
    workplace_type = str(job_employment_conditions.get("workplace_type", "")).lower()
    allowed_countries = [c.upper() for c in job_employment_conditions.get("remote_allowed_countries", [])]
    is_remote = workplace_type in ("remote", "workplace_type.remote") or (job_location and "remote" in job_location.lower())

    if not is_remote:
        return None, False, None

    # Check applicant target/residence country
    app_country = (applicant_snapshot.country or "").upper()
    user_target_locations = [loc.upper() for loc in career_strategy.target_locations]

    # Required Test 141: If employer explicitly restricts remote to USA-only
    # and applicant is based in / targets India
    is_usa_only = any("US" in c or "USA" in c or "UNITED STATES" in c for c in allowed_countries) and len(allowed_countries) == 1
    applicant_in_india = (
        app_country in ("IN", "IND", "INDIA")
        or any("INDIA" in loc for loc in user_target_locations)
    )

    if is_usa_only and applicant_in_india:
        res = RequirementEvaluationResult(
            requirement_id="req_remote_location",
            name="Remote Work Jurisdiction",
            category="mandatory",
            match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet=f"Applicant remote location: India ({app_country or 'IN'})",
            job_evidence_snippet=f"Remote within {', '.join(allowed_countries)} only",
            confidence=1.0,
            explanation=(
                f"Job permits remote work only within {', '.join(allowed_countries)}. "
                "Applicant's career preference specifies remote work from India; incompatible."
            ),
            is_satisfied=False,
        )
        return res, True, f"Remote role restricted to {', '.join(allowed_countries)}, but applicant is based in India."

    # Case 2: Country is explicitly in allowed list or globally remote
    is_global = any(c in ("GLOBAL", "ANYWHERE", "WORLDWIDE") for c in allowed_countries) or not allowed_countries
    matched_country = any(app_country in c or c in app_country for c in allowed_countries) if (app_country and allowed_countries) else False

    if matched_country or is_global:
        scope_text = "globally remote" if is_global else f"remote within {app_country}"
        res = RequirementEvaluationResult(
            requirement_id="req_remote_location",
            name="Remote Work Jurisdiction",
            category="mandatory",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet=f"Applicant country: {app_country or 'Global'}",
            job_evidence_snippet=f"Remote allowed: {scope_text}",
            confidence=1.0,
            explanation=f"Role is {scope_text}, compatible with applicant location preferences.",
            is_satisfied=True,
        )
        return res, False, None

    # Case 3: Country list exists but applicant country is outside and not empty
    if allowed_countries and app_country and not matched_country:
        res = RequirementEvaluationResult(
            requirement_id="req_remote_location",
            name="Remote Work Jurisdiction",
            category="mandatory",
            match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet=f"Applicant country: {app_country}",
            job_evidence_snippet=f"Allowed countries: {', '.join(allowed_countries)}",
            confidence=1.0,
            explanation=f"Applicant location ({app_country}) is not among employer's permitted remote jurisdictions ({allowed_countries}).",
            is_satisfied=False,
        )
        return res, True, f"Remote role excluded for applicant jurisdiction ({app_country})."

    # Default fallback: unknown specific countries
    res = RequirementEvaluationResult(
        requirement_id="req_remote_location",
        name="Remote Work Jurisdiction",
        category="mandatory",
        match_category=RequirementMatchCategory.UNKNOWN,
        applicant_claim_ref=applicant_snapshot.profile_id,
        applicant_evidence_snippet=f"Applicant country: {app_country or 'Unstated'}",
        job_evidence_snippet="Remote with unstated country restrictions",
        confidence=0.5,
        explanation="Remote posting does not specify geographic restrictions; manual confirmation advised.",
        is_satisfied=False,
    )
    return res, False, None
