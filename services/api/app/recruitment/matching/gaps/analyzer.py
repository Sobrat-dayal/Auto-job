"""Skill gap detection, severity assessment, and actionable remediation for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from app.recruitment.matching.contracts import (
    GapSeverity,
    GapType,
    MissingInformationRequest,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    SkillGapItem,
)

logger = logging.getLogger("autonom.recruitment.matching.gaps.analyzer")


def analyze_qualification_gaps(
    requirement_results: list[RequirementEvaluationResult],
    satisfied_alt_reqs: set[str] | None = None,
) -> tuple[list[SkillGapItem], list[MissingInformationRequest]]:
    """Analyzes requirements to identify qualification gaps and missing profile information (Sections 76-79)."""
    gaps: list[SkillGapItem] = []
    missing_info: list[MissingInformationRequest] = []
    alt_covered = {s.lower() for s in (satisfied_alt_reqs or set())}

    for r in requirement_results:
        if r.is_satisfied:
            continue
        if r.requirement_id.lower() in alt_covered or r.name.lower() in alt_covered:
            continue

        cat = r.category.lower()
        match_cat = r.match_category

        # 1. Determine Gap Type
        if match_cat == RequirementMatchCategory.PARTIALLY_SUPPORTED:
            gap_type = GapType.DURATION_DEFICIT
        elif match_cat == RequirementMatchCategory.RELATED_EXPERIENCE_ONLY:
            gap_type = GapType.RELATED_ONLY
        elif match_cat == RequirementMatchCategory.UNKNOWN:
            gap_type = GapType.MISSING_EVIDENCE
        elif cat == "mandatory":
            gap_type = GapType.MISSING_MANDATORY_SKILL
        else:
            gap_type = GapType.MISSING_PREFERRED_SKILL

        # 2. Determine Severity
        if cat == "mandatory":
            if match_cat == RequirementMatchCategory.UNKNOWN:
                severity = GapSeverity.CRITICAL_REVIEW
            else:
                severity = GapSeverity.BLOCKING
        elif cat == "preferred":
            severity = GapSeverity.MODERATE
        else:
            severity = GapSeverity.MINOR

        # 3. Formulate Actionable Remediation Suggestion
        if gap_type == GapType.RELATED_ONLY:
            remediation = (
                f"Applicant has related experience ({r.applicant_evidence_snippet or 'similar technologies'}). "
                f"Consider highlighting transferable architectural concepts or acquiring direct practical exposure to {r.name}."
            )
        elif gap_type == GapType.DURATION_DEFICIT:
            remediation = (
                f"Expand portfolio or project contributions demonstrating deep technical tenure with {r.name} "
                "to bridge the duration deficit."
            )
        elif gap_type == GapType.MISSING_EVIDENCE or match_cat == RequirementMatchCategory.UNKNOWN:
            remediation = f"Update your applicant profile to explicitly confirm and verify {r.name}."
            missing_info.append(MissingInformationRequest(
                requirement_name=r.name,
                missing_fact=f"Confirmation of {r.name}",
                importance="High (Mandatory Requirement)" if cat == "mandatory" else "Medium",
                suggested_profile_field="skills" if "skill" in r.name.lower() else "eligibility",
            ))
        elif cat == "mandatory":
            remediation = (
                f"{r.name} is a required mandatory qualification. "
                "Verify whether you have completed equivalent coursework, projects, or certifications that can be added to your profile."
            )
        else:
            remediation = f"Preferred qualification: acquiring familiarity with {r.name} will improve relevance."

        gap_item = SkillGapItem(
            requirement_id=r.requirement_id,
            skill_or_qualification=r.name,
            gap_type=gap_type,
            severity=severity,
            description=r.explanation,
            remediation_suggestion=remediation,
        )
        gaps.append(gap_item)

    return gaps, missing_info
