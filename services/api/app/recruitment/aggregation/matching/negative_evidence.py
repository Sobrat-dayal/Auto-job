"""Negative Evidence and False-Merge Prevention Engine (Stage 27)."""

from typing import Any
from app.db.models import CanonicalJobModel
from app.recruitment.aggregation.normalization.employment import are_employment_types_compatible
from app.recruitment.aggregation.normalization.locations import are_locations_compatible
from app.recruitment.aggregation.normalization.titles import (
    are_seniorities_compatible,
    extract_seniority,
)


def evaluate_negative_evidence(
    job_a: CanonicalJobModel,
    job_b: CanonicalJobModel,
) -> tuple[bool, list[dict[str, Any]]]:
    """Inspect contradictory evidence that forbids merging.

    Returns (has_hard_contradiction, negative_signals).
    """
    signals: list[dict[str, Any]] = []

    # 1. Contradictory Requisition Identifiers under the SAME employer!
    # (e.g. Employer X has Backend Engineer Req-101 and Backend Engineer Req-102)
    # They MUST remain separate vacancies!
    if (
        job_a.employer_id
        and job_b.employer_id
        and job_a.employer_id == job_b.employer_id
        and job_a.requisition_id
        and job_b.requisition_id
        and job_a.requisition_id != job_b.requisition_id
    ):
        signals.append({
            "rule": "contradictory_requisition_ids",
            "severity": "fatal",
            "message": f"Distinct requisitions under same employer: '{job_a.requisition_id}' vs '{job_b.requisition_id}'",
        })
        return True, signals

    # 2. Contradictory Employer Identifiers
    if (
        job_a.employer_id
        and job_b.employer_id
        and job_a.employer_id != job_b.employer_id
    ):
        signals.append({
            "rule": "contradictory_employers",
            "severity": "fatal",
            "message": f"Different employers: '{job_a.employer_id}' vs '{job_b.employer_id}'",
        })
        return True, signals

    # 3. Incompatible Seniority Levels (Senior vs Junior / Intern vs Principal)
    sen_a = extract_seniority(job_a.display_title)
    sen_b = extract_seniority(job_b.display_title)
    if not are_seniorities_compatible(sen_a, sen_b):
        signals.append({
            "rule": "incompatible_seniority",
            "severity": "fatal",
            "message": f"Seniority contradiction: '{sen_a}' vs '{sen_b}'",
        })
        return True, signals

    # 4. Incompatible Employment Types (Internship vs Full-Time)
    if not are_employment_types_compatible(job_a.employment_type, job_b.employment_type):
        signals.append({
            "rule": "incompatible_employment_type",
            "severity": "fatal",
            "message": f"Employment type contradiction: '{job_a.employment_type}' vs '{job_b.employment_type}'",
        })
        return True, signals

    # 5. Incompatible Physical Locations (London vs San Francisco on-site)
    # Exception: If requisition ID is verified identical under the same employer,
    # this is a confirmed multi-location posting for the same requisition (Section 110 Case A).
    has_same_requisition = bool(
        job_a.employer_id
        and job_b.employer_id
        and job_a.employer_id == job_b.employer_id
        and job_a.requisition_id
        and job_b.requisition_id
        and job_a.requisition_id == job_b.requisition_id
    )

    if not has_same_requisition:
        loc_compat, loc_reason = are_locations_compatible(
            job_a.location_summary,
            job_a.work_arrangement,
            job_b.location_summary,
            job_b.work_arrangement,
        )
        if not loc_compat:
            signals.append({
                "rule": "incompatible_locations",
                "severity": "fatal",
                "message": loc_reason,
            })
            return True, signals

    return False, signals
