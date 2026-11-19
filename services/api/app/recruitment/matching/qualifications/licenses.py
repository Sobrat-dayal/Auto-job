"""Professional licenses and security clearance evaluations for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.qualifications.licenses")


def evaluate_licensing_and_clearances(
    job_eligibility: dict[str, Any],
    applicant_snapshot: ApplicantSnapshotData,
) -> list[RequirementEvaluationResult]:
    """Cautiously evaluates professional licensing and security clearances without legal over-inference."""
    results: list[RequirementEvaluationResult] = []

    clearance_req = job_eligibility.get("security_clearance_required", False)
    clearance_level = job_eligibility.get("security_clearance_level")

    if clearance_req:
        # We NEVER infer security clearance from personal attributes
        results.append(RequirementEvaluationResult(
            requirement_id="req_security_clearance",
            name=f"Security Clearance ({clearance_level or 'Active'})",
            category="mandatory",
            match_category=RequirementMatchCategory.UNKNOWN,
            applicant_claim_ref=None,
            applicant_evidence_snippet=None,
            job_evidence_snippet=f"Security Clearance: {clearance_level or 'Required'}",
            confidence=0.5,
            explanation=(
                f"Role mandates security clearance ({clearance_level or 'active'}). "
                "Applicant clearance status is unrecorded in profile and requires human review."
            ),
            is_satisfied=False,
        ))

    return results
