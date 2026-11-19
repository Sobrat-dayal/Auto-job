"""Work authorization evaluation safeguards for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.conditions.work_authorization")


def evaluate_work_authorization(
    job_eligibility: dict[str, Any],
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[RequirementEvaluationResult | None, bool, str | None]:
    """Evaluates country-specific work authorization strictly without demographic inference.
    
    Returns (result, is_hard_conflict, conflict_reason).
    """
    auth_required = job_eligibility.get("work_authorization_required", False)
    req_countries = job_eligibility.get("citizenship_restrictions", [])

    if not auth_required and not req_countries:
        return None, False, None

    target_country = req_countries[0].upper() if req_countries else "US"
    applicant_auth_countries = [c.upper() for c in applicant_snapshot.authorized_countries]

    # Required test 139: Never infer work authorization from applicant's location or details!
    if not applicant_auth_countries:
        # Status is UNKNOWN, requires applicant review
        res = RequirementEvaluationResult(
            requirement_id="req_work_authorization",
            name=f"Work Authorization ({target_country})",
            category="mandatory",
            match_category=RequirementMatchCategory.UNKNOWN,
            applicant_claim_ref=None,
            applicant_evidence_snippet=None,
            job_evidence_snippet=f"Requires {target_country} work authorization",
            confidence=0.5,
            explanation=(
                f"Job mandates legal {target_country} work authorization. "
                "Applicant profile does not have verified work authorization on file; review required."
            ),
            is_satisfied=False,
        )
        return res, False, None

    # Check explicit list
    if any(target_country in c or c in target_country for c in applicant_auth_countries) or "GLOBAL" in applicant_auth_countries:
        res = RequirementEvaluationResult(
            requirement_id="req_work_authorization",
            name=f"Work Authorization ({target_country})",
            category="mandatory",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet=f"Authorized: {', '.join(applicant_auth_countries)}",
            job_evidence_snippet=f"Requires {target_country} work authorization",
            confidence=1.0,
            explanation=f"Applicant explicitly holds verified work authorization for {target_country}.",
            is_satisfied=True,
        )
        return res, False, None
    else:
        # Known conflict
        res = RequirementEvaluationResult(
            requirement_id="req_work_authorization",
            name=f"Work Authorization ({target_country})",
            category="mandatory",
            match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet=f"Authorized: {', '.join(applicant_auth_countries)}",
            job_evidence_snippet=f"Requires {target_country} work authorization",
            confidence=1.0,
            explanation=f"Applicant authorized in {applicant_auth_countries}, which does not cover required {target_country}.",
            is_satisfied=False,
        )
        return res, True, f"Missing required {target_country} work authorization."
