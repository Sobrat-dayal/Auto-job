"""Location, relocation, and availability evaluators for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.conditions.locations")


def evaluate_location(
    job_location: str | None,
    career_strategy: CareerStrategySnapshotData,
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[RequirementEvaluationResult | None, bool, str | None]:
    """Evaluates location against preferred and excluded regions."""
    if not job_location:
        return None, False, None

    loc_clean = job_location.strip().lower()

    # Check excluded locations (hard restriction)
    for excl in career_strategy.excluded_locations:
        if excl.lower() in loc_clean or loc_clean in excl.lower():
            res = RequirementEvaluationResult(
                requirement_id="req_location_exclusion",
                name="Location Policy",
                category="mandatory",
                match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
                confidence=1.0,
                explanation=f"Location '{job_location}' matches excluded location '{excl}'.",
                is_satisfied=False,
            )
            return res, True, f"Location '{job_location}' is in user's excluded locations list."

    # Check target locations
    matched_target = False
    for target in career_strategy.target_locations:
        if target.lower() in loc_clean or loc_clean in target.lower():
            matched_target = True
            break

    res = RequirementEvaluationResult(
        requirement_id="req_location_target",
        name="Location Alignment",
        category="preferred",
        match_category=RequirementMatchCategory.DIRECTLY_SATISFIED if matched_target else RequirementMatchCategory.PARTIALLY_SUPPORTED,
        confidence=1.0,
        explanation=f"Role located in '{job_location}' (target match: {matched_target}).",
        is_satisfied=True,
    )
    return res, False, None


def evaluate_relocation(
    job_location: str | None,
    career_strategy: CareerStrategySnapshotData,
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[bool, str]:
    """Evaluates applicant willingness to relocate for on-site or hybrid roles."""
    pref = career_strategy.relocation_preference.lower()
    app_city = (applicant_snapshot.city or "").lower()

    if not job_location or not app_city:
        return True, "Location undetermined; relocation neutral."

    if app_city in job_location.lower():
        return True, "Role is local to applicant city; no relocation required."

    if pref in ("willing", "yes", "conditionally_willing"):
        return True, f"Applicant is open to relocation ({pref})."
    else:
        return False, f"Role requires relocation outside '{applicant_snapshot.city}', but applicant preference is '{pref}'."
