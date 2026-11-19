"""Technical projects and contribution attribution for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import ApplicantSnapshotData
from app.recruitment.matching.qualifications.aliases import are_aliases, normalize_skill

logger = logging.getLogger("autonom.recruitment.matching.qualifications.projects")


def find_relevant_projects(
    skill_name: str,
    applicant_snapshot: ApplicantSnapshotData,
) -> list[dict[str, Any]]:
    """Identifies technical projects validating usage of a target technology, respecting attribution."""
    norm_target = normalize_skill(skill_name)
    relevant: list[dict[str, Any]] = []

    for proj in applicant_snapshot.projects:
        techs = proj.get("technologies", [])
        matched = False
        for t in techs:
            norm_t = normalize_skill(str(t))
            if norm_t == norm_target or are_aliases(norm_t, norm_target):
                matched = True
                break

        if matched:
            relevant.append({
                "id": proj.get("id"),
                "title": proj.get("title"),
                "category": proj.get("category", "personal"),
                "technologies": proj.get("technologies", []),
                "contribution": proj.get("applicant_contribution", "Primary Author"),
                "repo_url": proj.get("repo_url"),
                "is_verified": proj.get("verification_status") in ("user_confirmed", "evidence_supported"),
            })

    return relevant
