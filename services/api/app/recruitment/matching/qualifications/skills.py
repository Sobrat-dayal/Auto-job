"""Skill matching engine for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    SkillMatchDetail,
)
from app.recruitment.matching.qualifications.aliases import are_aliases, normalize_skill
from app.recruitment.matching.qualifications.skill_relationships import are_related_technologies

logger = logging.getLogger("autonom.recruitment.matching.qualifications.skills")


def evaluate_skills(
    job_skills: list[dict[str, Any]],
    applicant_snapshot: ApplicantSnapshotData,
    evidence_map: dict[str, list[dict[str, Any]]],
) -> tuple[list[SkillMatchDetail], list[RequirementEvaluationResult]]:
    """Evaluates job skill requirements against applicant verified skills, projects, and roles."""
    skill_details: list[SkillMatchDetail] = []
    requirement_results: list[RequirementEvaluationResult] = []

    # Map applicant confirmed skills by normalized canonical name
    applicant_skills_map: dict[str, dict[str, Any]] = {}
    for s in applicant_snapshot.skills:
        c_name = normalize_skill(s.get("canonical_name", s.get("name", "")))
        if c_name:
            applicant_skills_map[c_name] = s

    for js in job_skills:
        raw_name = js.get("name", "")
        norm_name = normalize_skill(raw_name)
        priority = js.get("priority", "MANDATORY").upper()
        req_category = "mandatory" if priority == "MANDATORY" else "preferred"
        req_id = js.get("id", f"req_skill_{norm_name}")
        min_years = js.get("min_years")

        # 1. Check exact match or alias in applicant confirmed skills
        matched_skill_entry: dict[str, Any] | None = None
        is_alias = False

        if norm_name in applicant_skills_map:
            matched_skill_entry = applicant_skills_map[norm_name]
        else:
            for app_cname, app_skill in applicant_skills_map.items():
                if are_aliases(norm_name, app_cname):
                    matched_skill_entry = app_skill
                    is_alias = True
                    break

        # 2. Check project or employment evidence if not in confirmed skills list
        if not matched_skill_entry and norm_name in evidence_map:
            ev_list = evidence_map[norm_name]
            matched_skill_entry = {
                "name": raw_name,
                "canonical_name": norm_name,
                "years_experience": 1.0,
                "proficiency": "intermediate",
                "is_verified": True,
                "evidence_snippet": f"Used in {len(ev_list)} project/experience records",
            }

        # 3. Check related technologies if still not matched
        related_skill_name: str | None = None
        related_family: str | None = None
        if not matched_skill_entry:
            for app_cname in applicant_skills_map.keys():
                is_rel, fam = are_related_technologies(norm_name, app_cname)
                if is_rel:
                    related_skill_name = app_cname
                    related_family = fam
                    break

        # 4. Formulate outcome and details
        if matched_skill_entry:
            app_years = matched_skill_entry.get("years_experience", 0.0)
            app_prof = matched_skill_entry.get("proficiency")

            if min_years and app_years < min_years:
                match_status = RequirementMatchCategory.PARTIALLY_SUPPORTED
                is_sat = False if priority == "MANDATORY" else True
                exp_text = f"Applicant has confirmed {raw_name} experience ({app_years} yrs), but job requires {min_years}+ yrs."
            else:
                match_status = RequirementMatchCategory.DIRECTLY_SATISFIED
                is_sat = True
                alias_note = f" (via alias '{matched_skill_entry.get('name')}')" if is_alias else ""
                exp_text = f"Confirmed evidence for {raw_name}{alias_note} in profile."

            snippet = f"{raw_name}: {app_years} yrs ({app_prof})"
            claim_ref = matched_skill_entry.get("id")
            confidence = 1.0 if matched_skill_entry.get("is_verified") else 0.8

        elif related_skill_name:
            match_status = RequirementMatchCategory.RELATED_EXPERIENCE_ONLY
            is_sat = False
            exp_text = (
                f"Applicant has confirmed {related_skill_name} experience from related family '{related_family}', "
                f"but no direct evidence for {raw_name}."
            )
            snippet = f"Related: {related_skill_name}"
            claim_ref = None
            confidence = 0.7

        else:
            match_status = RequirementMatchCategory.NOT_EVIDENCED
            is_sat = False
            exp_text = f"No profile claims or verified project evidence found for {raw_name}."
            snippet = None
            claim_ref = None
            confidence = 1.0

        detail = SkillMatchDetail(
            skill_name=raw_name,
            canonical_name=norm_name,
            category=js.get("category", "technical"),
            priority=priority,
            required_years=min_years,
            applicant_years=matched_skill_entry.get("years_experience") if matched_skill_entry else None,
            applicant_proficiency=matched_skill_entry.get("proficiency") if matched_skill_entry else None,
            match_status=match_status,
            is_alias_match=is_alias,
            is_related_match=bool(related_skill_name),
            explanation=exp_text,
        )
        skill_details.append(detail)

        req_res = RequirementEvaluationResult(
            requirement_id=req_id,
            name=raw_name,
            category=req_category,
            match_category=match_status,
            applicant_claim_ref=claim_ref,
            applicant_evidence_snippet=snippet,
            job_evidence_snippet=f"{raw_name} ({priority})",
            confidence=confidence,
            explanation=exp_text,
            is_satisfied=is_sat,
        )
        requirement_results.append(req_res)

    return skill_details, requirement_results
