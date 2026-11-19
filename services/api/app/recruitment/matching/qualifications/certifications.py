"""Certifications and licensing evaluation for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.qualifications.certifications")


def evaluate_certifications(
    job_requirements: list[dict[str, Any]],
    applicant_snapshot: ApplicantSnapshotData,
) -> list[RequirementEvaluationResult]:
    """Evaluates explicit professional certifications and credentials."""
    results: list[RequirementEvaluationResult] = []

    for req in job_requirements:
        name = req.get("name", "")
        # Filter: only evaluate items that are certifications or licenses
        q_type = str(req.get("qualification_type") or req.get("type") or "").upper()
        if q_type and q_type not in ("CERTIFICATION", "LICENSE"):
            continue
        if not q_type:
            cat = str(req.get("category", "")).lower()
            if cat not in ("certification", "license", "credential") and not any(
                kw in name.lower() for kw in ["certif", "pmp", "cissp", "cpa", "aws certified", "license"]
            ):
                continue

        cat = req.get("category", "mandatory").lower()
        req_id = req.get("id", f"req_cert_{name}")

        # Check if applicant has matching certification
        matched_cert: dict[str, Any] | None = None
        for cert in applicant_snapshot.certifications:
            c_title = cert.get("title", "").lower()
            if name.lower() in c_title or c_title in name.lower():
                matched_cert = cert
                break

        if matched_cert:
            is_expired = matched_cert.get("is_expired", False)
            if is_expired:
                match_cat = RequirementMatchCategory.PARTIALLY_SUPPORTED
                is_sat = False
                exp = f"Applicant holds {name}, but credential expired on {matched_cert.get('expiration_date')}."
            else:
                match_cat = RequirementMatchCategory.DIRECTLY_SATISFIED
                is_sat = True
                exp = f"Verified active certification {name} issued by {matched_cert.get('issuing_org')}."
            snippet = f"{name} (Active: {not is_expired})"
            claim_ref = matched_cert.get("id")
        else:
            match_cat = RequirementMatchCategory.NOT_EVIDENCED
            is_sat = False
            exp = f"No profile record found for required certification '{name}'."
            snippet = None
            claim_ref = None

        results.append(RequirementEvaluationResult(
            requirement_id=req_id,
            name=name,
            category=cat,
            match_category=match_cat,
            applicant_claim_ref=claim_ref,
            applicant_evidence_snippet=snippet,
            job_evidence_snippet=name,
            confidence=1.0,
            explanation=exp,
            is_satisfied=is_sat,
        ))

    return results
