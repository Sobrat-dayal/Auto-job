"""Applicant snapshot loader for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import ApplicantSnapshotData
from app.recruitment.matching.errors import ApplicantProfileNotFoundError
from app.recruitment.profile.service import get_profile_service

logger = logging.getLogger("autonom.recruitment.matching.inputs.applicant_snapshot")


def resolve_applicant_snapshot(profile_id: str | None = None) -> ApplicantSnapshotData:
    """Loads authoritative applicant facts from Stage 21 Profile Intelligence."""
    service = get_profile_service()
    try:
        if profile_id:
            profile = service.get_profile(profile_id)
        else:
            profile = service.get_primary_profile()
    except Exception as exc:
        logger.warning(f"Failed to fetch profile '{profile_id}': {exc}")
        raise ApplicantProfileNotFoundError(f"Applicant profile '{profile_id}' could not be resolved.") from exc

    # Extract explicit eligibility facts safely
    eligibility = profile.eligibility
    auth_countries = list(eligibility.authorized_countries) if eligibility and eligibility.confirmed_by_user else []
    requires_sponsorship = eligibility.requires_sponsorship if eligibility and eligibility.confirmed_by_user else False
    is_internship = eligibility.is_internship_eligible if eligibility else True
    start_date = eligibility.available_start_date if eligibility else None
    notice_days = eligibility.notice_period_days if eligibility else 0

    skills_data = [
        {
            "id": s.id,
            "name": s.name,
            "canonical_name": s.canonical_name.lower().strip(),
            "category": s.category.value,
            "proficiency": s.proficiency.value,
            "years_experience": s.years_experience or 0.0,
            "verification_status": s.verification_status.value,
            "is_verified": s.verification_status.value in ("user_confirmed", "evidence_supported"),
            "evidence_refs": s.evidence_refs,
        }
        for s in profile.skills
        if s.verification_status.value != "rejected"
    ]

    education_data = [
        {
            "id": e.id,
            "institution": e.institution,
            "degree": e.degree,
            "field_of_study": e.field_of_study,
            "specialization": e.specialization,
            "academic_status": e.academic_status.value,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "expected_completion": e.expected_completion,
            "gpa": e.gpa,
            "verification_status": e.verification_status.value,
        }
        for e in profile.education
    ]

    experience_data = [
        {
            "id": exp.id,
            "employer": exp.employer,
            "job_title": exp.job_title,
            "employment_type": exp.employment_type.value,
            "start_date": exp.start_date,
            "end_date": exp.end_date,
            "is_current": exp.is_current,
            "location": exp.location,
            "work_arrangement": exp.work_arrangement.value,
            "technologies": exp.technologies,
            "responsibilities": exp.responsibilities,
            "verification_status": exp.verification_status.value,
        }
        for exp in profile.experience
    ]

    projects_data = [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category.value,
            "technologies": p.technologies,
            "applicant_contribution": p.applicant_contribution,
            "repo_url": str(p.repo_url) if p.repo_url else None,
            "verification_status": p.verification_status.value,
        }
        for p in profile.projects
    ]

    certs_data = [
        {
            "id": c.id,
            "title": c.title,
            "issuing_org": c.issuing_org,
            "issue_date": c.issue_date,
            "expiration_date": c.expiration_date,
            "is_expired": c.is_expired,
            "credential_id": c.credential_id,
        }
        for c in profile.certifications
    ]

    return ApplicantSnapshotData(
        profile_id=profile.id,
        version=profile.version,
        headline=profile.headline,
        summary=profile.summary,
        country=profile.location.country,
        city=profile.location.city,
        remote_preference=profile.location.remote_preference,
        authorized_countries=auth_countries,
        requires_sponsorship=requires_sponsorship,
        is_internship_eligible=is_internship,
        available_start_date=start_date,
        notice_period_days=notice_days,
        skills=skills_data,
        education=education_data,
        experience=experience_data,
        projects=projects_data,
        certifications=certs_data,
    )
