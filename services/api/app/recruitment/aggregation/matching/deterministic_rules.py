"""Deterministic Exact Duplicate Evaluation Rules (Stage 27)."""

from typing import Any, Optional
from app.db.models import CanonicalJobModel


def evaluate_deterministic_match(
    job_a: CanonicalJobModel,
    job_b: CanonicalJobModel,
) -> tuple[bool, float, list[dict[str, Any]]]:
    """Evaluate whether two canonical jobs represent a deterministic duplicate.

    Returns (is_exact_match, confidence, positive_signals).
    """
    signals: list[dict[str, Any]] = []

    # 1. Exact Requisition Match under same verified employer
    if (
        job_a.employer_id
        and job_b.employer_id
        and job_a.employer_id == job_b.employer_id
        and job_a.requisition_id
        and job_b.requisition_id
        and job_a.requisition_id == job_b.requisition_id
    ):
        signals.append({
            "rule": "exact_employer_and_requisition",
            "weight": 1.0,
            "evidence": f"Same employer ({job_a.employer_id}) and same requisition ID ({job_a.requisition_id})",
        })
        return True, 1.0, signals

    # 2. Exact Title + Same Employer + Same Primary URL
    if (
        job_a.employer_id
        and job_b.employer_id
        and job_a.employer_id == job_b.employer_id
        and job_a.normalized_title == job_b.normalized_title
        and job_a.primary_url
        and job_b.primary_url
        and job_a.primary_url == job_b.primary_url
    ):
        signals.append({
            "rule": "exact_employer_title_and_url",
            "weight": 0.95,
            "evidence": f"Same employer, title ({job_a.display_title}), and canonical URL",
        })
        return True, 0.95, signals

    return False, 0.0, signals
