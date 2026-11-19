"""Evidence resolver for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import ApplicantSnapshotData

logger = logging.getLogger("autonom.recruitment.matching.inputs.evidence")


def resolve_evidence_map(snapshot: ApplicantSnapshotData) -> dict[str, list[dict[str, Any]]]:
    """Indexes verified applicant evidence by technology and claim for rapid retrieval."""
    evidence_by_tech: dict[str, list[dict[str, Any]]] = {}

    # Index project technologies
    for proj in snapshot.projects:
        techs = proj.get("technologies", [])
        for t in techs:
            key = str(t).lower().strip()
            if key not in evidence_by_tech:
                evidence_by_tech[key] = []
            evidence_by_tech[key].append({
                "type": "project",
                "title": proj.get("title"),
                "category": proj.get("category"),
                "contribution": proj.get("applicant_contribution"),
                "repo_url": proj.get("repo_url"),
                "verification_status": proj.get("verification_status"),
            })

    # Index employment experiences
    for exp in snapshot.experience:
        techs = exp.get("technologies", [])
        for t in techs:
            key = str(t).lower().strip()
            if key not in evidence_by_tech:
                evidence_by_tech[key] = []
            evidence_by_tech[key].append({
                "type": "professional_experience",
                "employer": exp.get("employer"),
                "job_title": exp.get("job_title"),
                "employment_type": exp.get("employment_type"),
                "dates": f"{exp.get('start_date')} to {exp.get('end_date') or 'Present'}",
                "verification_status": exp.get("verification_status"),
            })

    return evidence_by_tech
