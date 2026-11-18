"""Requirement-to-Evidence Matching Engine (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.resume.contracts import (
    JobDescriptionSnapshot,
    RequirementEvidenceMapping,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.resume.tailoring.evidence_matching")


class EvidenceMatchingEngine:
    """Evaluates job requirements against verified applicant profile facts without hallucinating qualifications."""

    @classmethod
    def match_requirements(
        cls,
        job: JobDescriptionSnapshot,
        profile: ApplicantProfile,
    ) -> list[RequirementEvidenceMapping]:
        mappings: list[RequirementEvidenceMapping] = []

        # Index applicant facts
        profile_skills = {s.name.lower().strip(): s for s in profile.skills}
        project_techs = {t.lower().strip(): p for p in profile.projects for t in p.technologies}
        experience_techs = {t.lower().strip(): e for e in profile.experience for t in e.technologies}

        # 1. Match tech stack items
        for tech in job.tech_stack:
            tech_lower = tech.lower().strip()
            if tech_lower in profile_skills:
                skill_obj = profile_skills[tech_lower]
                prof_val = getattr(skill_obj, "proficiency", getattr(skill_obj, "proficiency_level", "verified"))
                prof_str = prof_val.value if hasattr(prof_val, "value") else str(prof_val)
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=f"Experience with {tech}",
                        is_required=True,
                        claim_id=skill_obj.id,
                        claim_text=f"Verified skill: {skill_obj.name} (Proficiency: {prof_str})",
                        match_category=RequirementMatchCategory.DIRECTLY_SUPPORTED,
                        explanation=f"Direct match with verified technical skill '{skill_obj.name}'.",
                        uncertainty=0.0,
                    )
                )
            elif tech_lower in project_techs:
                prj = project_techs[tech_lower]
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=f"Experience with {tech}",
                        is_required=True,
                        claim_id=prj.id,
                        claim_text=f"Project implementation: {prj.name}",
                        match_category=RequirementMatchCategory.DIRECTLY_SUPPORTED,
                        explanation=f"Direct match evidenced in project '{prj.name}'.",
                        uncertainty=0.1,
                    )
                )
            elif tech_lower in experience_techs:
                exp = experience_techs[tech_lower]
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=f"Experience with {tech}",
                        is_required=True,
                        claim_id=exp.id,
                        claim_text=f"Employment experience at {exp.company}",
                        match_category=RequirementMatchCategory.DIRECTLY_SUPPORTED,
                        explanation=f"Direct match utilized at '{exp.company}'.",
                        uncertainty=0.05,
                    )
                )
            else:
                # Skill is missing from profile
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=f"Experience with {tech}",
                        is_required=True,
                        claim_id=None,
                        claim_text=None,
                        match_category=RequirementMatchCategory.NOT_EVIDENCED,
                        explanation=f"No verified skills, projects, or employment records in the profile evidence '{tech}'.",
                        uncertainty=0.0,
                    )
                )

        # 2. Match required prose bullets if available
        for req_bullet in job.required_skills:
            # If already covered by exact tech matching, skip
            if any(m.requirement_text.lower() in req_bullet.lower() for m in mappings):
                continue

            # Check for keyword matches in profile skills
            matched_skill = None
            for s_name, s_obj in profile_skills.items():
                if s_name in req_bullet.lower():
                    matched_skill = s_obj
                    break

            if matched_skill:
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=req_bullet,
                        is_required=True,
                        claim_id=matched_skill.id,
                        claim_text=f"Skill: {matched_skill.name}",
                        match_category=RequirementMatchCategory.DIRECTLY_SUPPORTED,
                        explanation=f"Requirement mentions skill '{matched_skill.name}' verified in applicant profile.",
                        uncertainty=0.15,
                    )
                )
            else:
                mappings.append(
                    RequirementEvidenceMapping(
                        requirement_text=req_bullet,
                        is_required=True,
                        claim_id=None,
                        claim_text=None,
                        match_category=RequirementMatchCategory.REQUIRES_REVIEW,
                        explanation="Generic or complex qualification requirement requiring applicant review.",
                        uncertainty=0.6,
                    )
                )

        return mappings
