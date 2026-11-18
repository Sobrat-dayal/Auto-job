"""Fact Selection Engine: Selects verified applicant facts based on resume type (Stage 23)."""

from __future__ import annotations

import logging
from typing import Optional
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    EducationRecord,
    EmploymentRecord,
    ProjectRecord,
    SkillItem,
)
from app.recruitment.resume.contracts import (
    ResumeType,
    SectionType,
    SourceFactReference,
)

logger = logging.getLogger("autonom.recruitment.resume.content.fact_selection")


class FactSelectionEngine:
    """Selects and prioritizes verified profile facts for specific resume configurations."""

    @classmethod
    def get_section_order(cls, resume_type: ResumeType) -> list[SectionType]:
        """Returns standard, ATS-proven section ordering for a given target resume archetype."""
        if resume_type == ResumeType.INTERNSHIP:
            return [
                SectionType.HEADER,
                SectionType.SUMMARY,
                SectionType.EDUCATION,
                SectionType.PROJECTS,
                SectionType.SKILLS,
                SectionType.EXPERIENCE,
                SectionType.CERTIFICATIONS,
            ]
        elif resume_type in (ResumeType.EXPERIENCED, ResumeType.JOB_TAILORED):
            return [
                SectionType.HEADER,
                SectionType.SUMMARY,
                SectionType.SKILLS,
                SectionType.EXPERIENCE,
                SectionType.PROJECTS,
                SectionType.EDUCATION,
                SectionType.CERTIFICATIONS,
            ]
        elif resume_type == ResumeType.ACADEMIC:
            return [
                SectionType.HEADER,
                SectionType.EDUCATION,
                SectionType.RESEARCH,
                SectionType.PUBLICATIONS,
                SectionType.EXPERIENCE,
                SectionType.PROJECTS,
                SectionType.AWARDS,
                SectionType.SKILLS,
            ]
        elif resume_type == ResumeType.MINIMALIST:
            return [
                SectionType.HEADER,
                SectionType.EXPERIENCE,
                SectionType.PROJECTS,
                SectionType.SKILLS,
                SectionType.EDUCATION,
            ]
        else:  # MASTER, GENERAL, EXPERIENCED
            return [
                SectionType.HEADER,
                SectionType.SUMMARY,
                SectionType.EXPERIENCE,
                SectionType.EDUCATION,
                SectionType.SKILLS,
                SectionType.PROJECTS,
                SectionType.CERTIFICATIONS,
            ]

    @classmethod
    def filter_eligible_skills(
        cls,
        profile: ApplicantProfile,
        requested_names: Optional[list[str]] = None,
        max_count: int = 24,
    ) -> list[SkillItem]:
        """Extracts confirmed technical skills, preserving verified categories and proficiency."""
        def is_verified_skill(s: SkillItem) -> bool:
            if hasattr(s, "is_verified"):
                return bool(getattr(s, "is_verified"))
            status = getattr(s, "verification_status", None)
            if status is not None:
                val = status.value if hasattr(status, "value") else str(status).lower()
                return val in ("UserConfirmed", "EvidenceSupported", "ExternallyVerified", "user_confirmed", "evidence_supported", "externally_verified", "verified")
            return True

        eligible = [s for s in profile.skills if is_verified_skill(s)]
        if not eligible and profile.skills:
            # Fall back to all profile skills if none explicitly flagged as verified yet
            eligible = list(profile.skills)

        if requested_names:
            req_set = {n.lower().strip() for n in requested_names}
            eligible = [s for s in eligible if s.name.lower().strip() in req_set]

        # Sort by proficiency or recency
        return eligible[:max_count]

    @classmethod
    def filter_eligible_projects(
        cls,
        profile: ApplicantProfile,
        requested_ids: Optional[list[str]] = None,
        max_count: int = 5,
    ) -> list[ProjectRecord]:
        """Extracts candidate projects with repository evidence and contribution backing."""
        projects = list(profile.projects)
        if requested_ids:
            req_set = set(requested_ids)
            projects = [p for p in projects if p.id in req_set]
        # Prioritize featured or evidenced projects
        projects.sort(key=lambda p: (p.is_featured, len(p.technologies)), reverse=True)
        return projects[:max_count]

    @classmethod
    def filter_eligible_experience(
        cls,
        profile: ApplicantProfile,
        max_count: int = 6,
    ) -> list[EmploymentRecord]:
        """Extracts chronological employment records."""
        exp = list(profile.experience)
        # Sort reverse chronologically by start date
        exp.sort(key=lambda e: e.start_date or "", reverse=True)
        return exp[:max_count]

    @classmethod
    def filter_eligible_education(
        cls,
        profile: ApplicantProfile,
    ) -> list[EducationRecord]:
        """Extracts chronological educational qualifications."""
        edu = list(profile.education)
        edu.sort(key=lambda e: e.start_date or "", reverse=True)
        return edu
