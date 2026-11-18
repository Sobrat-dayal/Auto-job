"""Applicant Fact Resolver & Evidence Anchoring Engine (Stage 24)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
    VerificationStatus,
)
from app.recruitment.writing.contracts import (
    ApplicationQuestionRecord,
    QuestionCategory,
    WritingSourceReference,
)

logger = logging.getLogger("autonom.recruitment.writing.answers.fact_resolver")


class FactResolver:
    """Resolves verified profile facts and evidence references for a specific question."""

    @classmethod
    def resolve_question_facts(
        cls,
        question: ApplicationQuestionRecord,
        profile: ApplicantProfile,
    ) -> dict[str, Any]:
        """Returns structured dictionary of matching facts and source references."""
        cat = question.category
        q_text_lower = question.exact_question_text.lower()

        facts: dict[str, Any] = {}
        source_refs: list[WritingSourceReference] = []

        if cat == QuestionCategory.EDUCATION or any(t in q_text_lower for t in ["degree", "graduation", "university", "gpa"]):
            if profile.education:
                top_edu = profile.education[0]
                status = getattr(top_edu, "academic_status", getattr(top_edu, "status", None))
                is_completed = status in (AcademicStatus.COMPLETED, "completed", "graduated")
                facts["education"] = {
                    "degree": top_edu.degree,
                    "field_of_study": top_edu.field_of_study,
                    "institution": top_edu.institution,
                    "end_date": top_edu.end_date,
                    "expected_completion": getattr(top_edu, "expected_completion", None),
                    "gpa": top_edu.gpa,
                    "is_completed": is_completed,
                }
                source_refs.append(WritingSourceReference(source_entity_id=top_edu.id, source_type="education"))

        elif cat == QuestionCategory.PROJECTS or "project" in q_text_lower:
            if profile.projects:
                top_proj = profile.projects[0]
                facts["project"] = {
                    "title": top_proj.title,
                    "description": top_proj.description,
                    "technologies": top_proj.technologies,
                    "contribution": top_proj.applicant_contribution,
                    "repo_url": top_proj.repo_url,
                }
                source_refs.append(WritingSourceReference(source_entity_id=top_proj.id, source_type="project"))

        elif cat == QuestionCategory.EXPERIENCE or "experience" in q_text_lower or "role" in q_text_lower:
            if profile.experience:
                top_exp = profile.experience[0]
                facts["experience"] = {
                    "job_title": top_exp.job_title,
                    "employer": top_exp.employer,
                    "start_date": top_exp.start_date,
                    "end_date": top_exp.end_date,
                    "is_current": top_exp.is_current,
                    "technologies": top_exp.technologies,
                    "achievements": [a.statement for a in top_exp.achievements if getattr(a, "statement", None)],
                }
                source_refs.append(WritingSourceReference(source_entity_id=top_exp.id, source_type="experience"))

        elif cat == QuestionCategory.SKILLS or "technolog" in q_text_lower:
            confirmed_skills = [
                s.name for s in profile.skills
                if getattr(s, "verification_status", None) in (
                    VerificationStatus.USER_CONFIRMED,
                    VerificationStatus.EVIDENCE_SUPPORTED,
                    VerificationStatus.EXTERNALLY_VERIFIED,
                    "user_confirmed",
                    "evidence_supported",
                    "externally_verified",
                )
            ]
            facts["skills"] = confirmed_skills or [s.name for s in profile.skills]
            for s in profile.skills[:5]:
                source_refs.append(WritingSourceReference(source_entity_id=s.id, source_type="skill"))

        elif cat == QuestionCategory.WORK_ELIGIBILITY:
            if profile.eligibility:
                facts["eligibility"] = {
                    "work_authorization": profile.eligibility.work_authorization,
                    "requires_sponsorship": profile.eligibility.requires_sponsorship,
                    "confirmed_by_user": profile.eligibility.confirmed_by_user,
                }
                source_refs.append(WritingSourceReference(source_entity_id=profile.id, source_type="claim"))

        elif cat == QuestionCategory.CONTACT:
            facts["contact"] = {
                "legal_name": profile.contact.legal_name,
                "email": profile.contact.primary_email,
                "phone": profile.contact.phone,
                "location": f"{getattr(profile.location, 'city', '')}, {getattr(profile.location, 'country', '')}".strip(", "),
            }
            source_refs.append(WritingSourceReference(source_entity_id=profile.id, source_type="claim"))

        return {
            "facts": facts,
            "source_refs": source_refs,
            "has_matching_facts": len(facts) > 0,
        }
