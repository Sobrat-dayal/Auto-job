"""Visa sponsorship compatibility evaluation for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.conditions.sponsorship")


def evaluate_sponsorship(
    job_eligibility: dict[str, Any],
    applicant_snapshot: ApplicantSnapshotData,
) -> tuple[RequirementEvaluationResult | None, bool, str | None]:
    """Evaluates visa sponsorship requirements and conflicts (Section 48, Required Test 140).
    
    Returns (result, is_hard_conflict, conflict_reason).
    """
    sponsorship_offered = job_eligibility.get("sponsorship_offered", False)
    sponsorship_refused = job_eligibility.get("sponsorship_refused", False)
    applicant_needs_sponsorship = applicant_snapshot.requires_sponsorship

    # Case 1: Hard Conflict - Applicant requires sponsorship, employer explicitly refuses
    if applicant_needs_sponsorship and sponsorship_refused:
        res = RequirementEvaluationResult(
            requirement_id="req_visa_sponsorship",
            name="Visa Sponsorship",
            category="mandatory",
            match_category=RequirementMatchCategory.KNOWN_NOT_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet="Applicant requires visa sponsorship",
            job_evidence_snippet="Employer explicitly states: No sponsorship available",
            confidence=1.0,
            explanation=(
                "Hard eligibility conflict: Applicant explicitly requires visa sponsorship, "
                "but employer policy states sponsorship is not available."
            ),
            is_satisfied=False,
        )
        return res, True, "Employer does not offer visa sponsorship, but applicant requires it."

    # Case 2: Applicant needs sponsorship, employer explicitly offers it
    if applicant_needs_sponsorship and sponsorship_offered:
        res = RequirementEvaluationResult(
            requirement_id="req_visa_sponsorship",
            name="Visa Sponsorship",
            category="mandatory",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet="Applicant requires visa sponsorship",
            job_evidence_snippet="Employer provides visa sponsorship",
            confidence=1.0,
            explanation="Employer explicitly provides visa sponsorship requested by applicant.",
            is_satisfied=True,
        )
        return res, False, None

    # Case 3: Applicant needs sponsorship, employer is silent
    if applicant_needs_sponsorship and not sponsorship_offered and not sponsorship_refused:
        res = RequirementEvaluationResult(
            requirement_id="req_visa_sponsorship",
            name="Visa Sponsorship",
            category="mandatory",
            match_category=RequirementMatchCategory.UNKNOWN,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet="Applicant requires visa sponsorship",
            job_evidence_snippet="Sponsorship terms unstated",
            confidence=0.5,
            explanation=(
                "Applicant requires visa sponsorship, but employer posting does not state sponsorship policy. "
                "Silence cannot be treated as a denial; review recommended."
            ),
            is_satisfied=False,
        )
        return res, False, None

    # Case 4: Applicant does not need sponsorship
    if not applicant_needs_sponsorship:
        res = RequirementEvaluationResult(
            requirement_id="req_visa_sponsorship",
            name="Visa Sponsorship",
            category="mandatory",
            match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
            applicant_claim_ref=applicant_snapshot.profile_id,
            applicant_evidence_snippet="No sponsorship needed",
            job_evidence_snippet=None,
            confidence=1.0,
            explanation="Applicant does not require visa sponsorship.",
            is_satisfied=True,
        )
        return res, False, None

    return None, False, None
