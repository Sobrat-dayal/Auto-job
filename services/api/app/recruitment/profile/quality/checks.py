"""Deterministic data quality and completeness assessment rules for Applicant Profiles."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Optional

from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantClaim,
    ApplicantProfile,
    DataQualityIssue,
    DataQualityReport,
    QualitySeverity,
    VerificationStatus,
)


class DataQualityEngine:
    """Evaluates applicant profile completeness, date consistency, and evidence coverage."""

    @classmethod
    def evaluate(
        cls,
        profile: ApplicantProfile,
        claims: Optional[list[ApplicantClaim]] = None,
    ) -> DataQualityReport:
        issues: list[DataQualityIssue] = []
        breakdown: dict[str, float] = {
            "identity": 0.0,
            "contact": 0.0,
            "education": 0.0,
            "skills": 0.0,
            "experience_and_projects": 0.0,
            "evidence": 0.0,
        }

        # 1. Identity & Contact Checks
        has_legal_name = bool(profile.contact.legal_name and profile.contact.legal_name.strip())
        has_headline = bool(profile.headline and profile.headline.strip())
        has_summary = bool(profile.summary and len(profile.summary.strip()) > 20)

        id_score = 0.0
        if has_legal_name:
            id_score += 60.0
        else:
            issues.append(
                DataQualityIssue(
                    code="MISSING_LEGAL_NAME",
                    severity=QualitySeverity.ERROR,
                    category="identity",
                    message="Legal name is required for recruitment applications.",
                    field_ref="contact.legal_name",
                    suggested_fix="Provide your legal full name in Identity settings.",
                )
            )
        if has_headline:
            id_score += 20.0
        if has_summary:
            id_score += 20.0
        breakdown["identity"] = id_score

        # Contact
        contact_score = 0.0
        has_email = bool(profile.contact.primary_email and "@" in profile.contact.primary_email)
        has_phone = bool(profile.contact.phone and len(profile.contact.phone.strip()) >= 7)
        has_location = bool(profile.location.city and profile.location.country)

        if has_email:
            contact_score += 50.0
        else:
            issues.append(
                DataQualityIssue(
                    code="MISSING_PRIMARY_EMAIL",
                    severity=QualitySeverity.ERROR,
                    category="contact",
                    message="Primary email address is missing or invalid.",
                    field_ref="contact.primary_email",
                    suggested_fix="Enter a verified personal or academic email.",
                )
            )
        if has_phone:
            contact_score += 30.0
        if has_location:
            contact_score += 20.0
        breakdown["contact"] = contact_score

        # 2. Education Checks
        edu_score = 0.0
        if profile.education:
            edu_score = 70.0
            for idx, edu in enumerate(profile.education):
                if edu.gpa is not None and edu.gpa_scale:
                    edu_score = min(100.0, edu_score + 10.0)

                # Check future graduation logic
                current_year = datetime.now(UTC).year
                if edu.end_date:
                    match = re.search(r"\b(19\d{2}|20\d{2})\b", str(edu.end_date))
                    if match:
                        end_yr = int(match.group(1))
                        if end_yr > current_year and edu.academic_status in (AcademicStatus.COMPLETED, AcademicStatus.GRADUATED):
                            issues.append(
                                DataQualityIssue(
                                    code="FUTURE_GRADUATION_INVALID_STATUS",
                                    severity=QualitySeverity.WARNING,
                                    category="education",
                                    message=f"Education '{edu.institution}' has future completion year ({end_yr}) but status is '{edu.academic_status}'.",
                                    field_ref=f"education[{idx}].academic_status",
                                    suggested_fix="Set status to 'currently_enrolled'.",
                                )
                            )
                if edu.start_date and edu.end_date:
                    if str(edu.end_date) < str(edu.start_date):
                        issues.append(
                            DataQualityIssue(
                                code="EDUCATION_DATE_INVERTED",
                                severity=QualitySeverity.ERROR,
                                category="education",
                                message=f"End date ({edu.end_date}) precedes start date ({edu.start_date}) for {edu.institution}.",
                                field_ref=f"education[{idx}].end_date",
                            )
                        )
        else:
            issues.append(
                DataQualityIssue(
                    code="MISSING_EDUCATION",
                    severity=QualitySeverity.WARNING,
                    category="education",
                    message="No education records declared.",
                    suggested_fix="Add at least one degree, diploma, or secondary education record.",
                )
            )
        breakdown["education"] = min(100.0, edu_score)

        # 3. Skills Checks
        skill_score = 0.0
        skill_count = len(profile.skills)
        if skill_count >= 5:
            skill_score = 100.0
        elif skill_count >= 3:
            skill_score = 70.0
        elif skill_count >= 1:
            skill_score = 40.0
        else:
            issues.append(
                DataQualityIssue(
                    code="INSUFFICIENT_SKILLS",
                    severity=QualitySeverity.ERROR,
                    category="skills",
                    message="At least 3 technical or professional skills are required for ATS matching.",
                    field_ref="skills",
                    suggested_fix="Add your core languages, frameworks, or database skills.",
                )
            )
        breakdown["skills"] = skill_score

        # 4. Experience & Projects Checks
        exp_proj_score = 0.0
        has_experience = len(profile.experience) > 0
        has_projects = len(profile.projects) > 0

        if has_experience and has_projects:
            exp_proj_score = 100.0
        elif has_experience or has_projects:
            exp_proj_score = 75.0
        else:
            issues.append(
                DataQualityIssue(
                    code="NO_PRACTICAL_EXPERIENCE_OR_PROJECTS",
                    severity=QualitySeverity.WARNING,
                    category="experience",
                    message="Neither work experience nor practical projects are recorded.",
                    suggested_fix="Add past internships, student projects, or open-source repositories.",
                )
            )

        # Validate experience date ranges
        for idx, exp in enumerate(profile.experience):
            if exp.start_date and exp.end_date and not exp.is_current:
                if str(exp.end_date) < str(exp.start_date):
                    issues.append(
                        DataQualityIssue(
                            code="EXPERIENCE_DATE_INVERTED",
                            severity=QualitySeverity.ERROR,
                            category="experience",
                            message=f"End date ({exp.end_date}) precedes start date ({exp.start_date}) at {exp.employer}.",
                            field_ref=f"experience[{idx}].end_date",
                        )
                    )
        breakdown["experience_and_projects"] = exp_proj_score

        # 5. Evidence & Claims Checks
        evidence_score = 0.0
        all_ev_refs = set()
        for edu in profile.education:
            all_ev_refs.update(edu.evidence_refs)
        for exp in profile.experience:
            all_ev_refs.update(exp.evidence_refs)
        for prj in profile.projects:
            all_ev_refs.update(prj.evidence_refs)
        for cert in profile.certifications:
            if cert.evidence_ref:
                all_ev_refs.add(cert.evidence_ref)

        if len(all_ev_refs) >= 3:
            evidence_score = 100.0
        elif len(all_ev_refs) >= 1:
            evidence_score = 60.0
        else:
            issues.append(
                DataQualityIssue(
                    code="NO_SUPPORTING_EVIDENCE",
                    severity=QualitySeverity.INFO,
                    category="evidence",
                    message="No claims currently reference uploaded evidence documents or links.",
                    suggested_fix="Upload resume PDF or certificates to the Evidence Library and link them.",
                )
            )
        breakdown["evidence"] = evidence_score

        # Overall Completeness Score (Weighted Average)
        weights = {
            "identity": 0.20,
            "contact": 0.15,
            "education": 0.20,
            "skills": 0.20,
            "experience_and_projects": 0.15,
            "evidence": 0.10,
        }
        completeness = sum(breakdown[k] * weights[k] for k in weights)

        # Recruitment readiness requires: no ERROR severity issues and completeness >= 65.0
        has_errors = any(i.severity == QualitySeverity.ERROR for i in issues)
        is_ready = (not has_errors) and (completeness >= 65.0)

        return DataQualityReport(
            profile_id=profile.id,
            completeness_score=round(completeness, 1),
            is_recruitment_ready=is_ready,
            issues=issues,
            category_breakdown={k: round(v, 1) for k, v in breakdown.items()},
        )
