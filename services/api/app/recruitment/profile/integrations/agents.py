"""Scoped profile query adapters for Stage 13 Specialist Recruitment Agents."""

from __future__ import annotations

import logging
from typing import Any

from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ProfileSnapshot,
    VerificationStatus,
)

logger = logging.getLogger("autonom.recruitment.profile.integrations.agents")


class AgentProfileAdapter:
    """Provides role-tailored, sanitized profile views preventing unrestricted data leakage."""

    @staticmethod
    def get_job_matching_snapshot(profile: ApplicantProfile) -> ProfileSnapshot:
        """Returns skills, education, experience, and projects for ATS match scoring (masks private contact)."""
        filtered = {
            "profile_id": profile.id,
            "version": profile.version,
            "headline": profile.headline,
            "summary": profile.summary,
            "location": {
                "country": profile.location.country,
                "city": profile.location.city,
                "remote_preference": profile.location.remote_preference,
            },
            "skills": [
                {
                    "name": s.name,
                    "canonical_name": s.canonical_name,
                    "category": s.category.value,
                    "proficiency": s.proficiency.value,
                    "years": s.years_experience,
                    "verified": s.verification_status in (VerificationStatus.USER_CONFIRMED, VerificationStatus.EVIDENCE_SUPPORTED),
                }
                for s in profile.skills
                if s.verification_status != VerificationStatus.REJECTED
            ],
            "education": [
                {
                    "institution": e.institution,
                    "degree": e.degree,
                    "field_of_study": e.field_of_study,
                    "end_date": e.end_date,
                    "status": e.academic_status.value,
                    "gpa": e.gpa,
                }
                for e in profile.education
            ],
            "experience": [
                {
                    "employer": exp.employer,
                    "job_title": exp.job_title,
                    "employment_type": exp.employment_type.value,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "is_current": exp.is_current,
                    "technologies": exp.technologies,
                }
                for exp in profile.experience
            ],
            "projects": [
                {
                    "title": p.title,
                    "category": p.category.value,
                    "technologies": p.technologies,
                    "contribution": p.applicant_contribution,
                    "repo_url": p.repo_url,
                }
                for p in profile.projects
            ],
        }
        return ProfileSnapshot(
            profile_id=profile.id,
            version=profile.version,
            target_agent="job_matching_agent",
            authorized_scopes=["skills", "education", "experience", "projects"],
            filtered_data=filtered,
        )

    @staticmethod
    def get_resume_snapshot(profile: ApplicantProfile) -> ProfileSnapshot:
        """Returns verified achievements, quantified metrics, and structured sections for ATS tailoring."""
        filtered = {
            "profile_id": profile.id,
            "version": profile.version,
            "legal_name": profile.contact.legal_name,
            "headline": profile.headline,
            "summary": profile.summary,
            "email": profile.contact.primary_email,
            "location": f"{profile.location.city or ''}, {profile.location.country or ''}".strip(", "),
            "links": [{"platform": l.platform, "url": l.url} for l in profile.professional_links],
            "experience": [
                {
                    "employer": exp.employer,
                    "job_title": exp.job_title,
                    "employment_type": exp.employment_type.value,
                    "dates": f"{exp.start_date} - {exp.end_date or 'Present'}",
                    "responsibilities": exp.responsibilities,
                    "technologies": exp.technologies,
                    "achievements": [
                        {
                            "statement": a.statement,
                            "metric": f"{a.metric_value or ''} {a.metric_unit or ''}".strip(),
                        }
                        for a in exp.achievements
                        if a.verification_status != VerificationStatus.REJECTED
                    ],
                }
                for exp in profile.experience
            ],
            "education": [
                {
                    "institution": e.institution,
                    "degree": f"{e.degree} in {e.field_of_study}",
                    "dates": f"{e.start_date or ''} - {e.end_date or 'Present'}".strip(" -"),
                    "gpa": f"{e.gpa}/{e.gpa_scale}" if e.gpa else None,
                    "distinctions": e.distinctions,
                }
                for e in profile.education
            ],
            "skills": [s.name for s in profile.skills if s.verification_status != VerificationStatus.REJECTED],
            "projects": [
                {
                    "title": p.title,
                    "description": p.description,
                    "contribution": p.applicant_contribution,
                    "technologies": p.technologies,
                    "links": [url for url in (p.repo_url, p.demo_url) if url],
                }
                for p in profile.projects
            ],
            "certifications": [
                {
                    "title": c.title,
                    "issuer": c.issuing_org,
                    "date": c.issue_date,
                    "active": not c.is_expired,
                }
                for c in profile.certifications
                if not c.is_expired
            ],
        }
        return ProfileSnapshot(
            profile_id=profile.id,
            version=profile.version,
            target_agent="resume_agent",
            authorized_scopes=["resume_content", "achievements", "verified_skills"],
            filtered_data=filtered,
        )

    @staticmethod
    def get_application_snapshot(profile: ApplicantProfile) -> ProfileSnapshot:
        """Returns verified fields for form completion and explicitly identifies missing fields."""
        missing_fields: list[str] = []
        if not profile.contact.legal_name:
            missing_fields.append("contact.legal_name")
        if not profile.contact.primary_email:
            missing_fields.append("contact.primary_email")
        if not profile.contact.phone:
            missing_fields.append("contact.phone")
        if not profile.location.country:
            missing_fields.append("location.country")
        if not profile.education:
            missing_fields.append("education")
        if profile.eligibility is None or not profile.eligibility.confirmed_by_user:
            missing_fields.append("eligibility.work_authorization")

        filtered = {
            "profile_id": profile.id,
            "version": profile.version,
            "contact": profile.contact.model_dump(),
            "location": profile.location.model_dump(),
            "eligibility": profile.eligibility.model_dump() if profile.eligibility else None,
            "missing_fields": missing_fields,
            "has_all_mandatory_fields": len(missing_fields) == 0,
        }
        return ProfileSnapshot(
            profile_id=profile.id,
            version=profile.version,
            target_agent="application_agent",
            authorized_scopes=["application_fields", "missing_fields_analysis"],
            filtered_data=filtered,
        )

    @staticmethod
    def get_interview_prep_snapshot(profile: ApplicantProfile) -> ProfileSnapshot:
        """Returns project contributions, technical challenges, and verified experience for interview dossiers."""
        filtered = {
            "profile_id": profile.id,
            "version": profile.version,
            "projects": [
                {
                    "title": p.title,
                    "description": p.description,
                    "contribution": p.applicant_contribution,
                    "team_context": p.team_context,
                    "technologies": p.technologies,
                    "responsibilities": p.responsibilities,
                    "results": p.results,
                }
                for p in profile.projects
            ],
            "experience": [
                {
                    "employer": exp.employer,
                    "role": exp.job_title,
                    "responsibilities": exp.responsibilities,
                    "technologies": exp.technologies,
                    "achievements": [a.statement for a in exp.achievements],
                }
                for exp in profile.experience
            ],
        }
        return ProfileSnapshot(
            profile_id=profile.id,
            version=profile.version,
            target_agent="interview_prep_agent",
            authorized_scopes=["projects", "responsibilities", "technical_contributions"],
            filtered_data=filtered,
        )
