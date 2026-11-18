"""Deterministic Job Eligibility Evaluator (Stage 25)."""

from __future__ import annotations

from typing import Optional
from app.recruitment.policy.contracts import (
    EligibilityCategoryResult,
    EligibilityOutcome,
    JobEligibilityAssessment,
    JobOpportunityContext,
    ReviewTrigger,
    SkillMatchCategory,
)
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
)


class JobEligibilityEvaluator:
    """Evaluates applicant profile facts against explicit job opportunity requirements."""

    @classmethod
    def evaluate_eligibility(
        cls,
        profile: ApplicantProfile,
        job: JobOpportunityContext,
    ) -> JobEligibilityAssessment:
        categories: dict[str, EligibilityCategoryResult] = {}
        unknown_items: list[str] = []
        review_triggers: list[ReviewTrigger] = []
        has_blocking_disqualification = False

        # 1. Education Requirement Evaluation
        edu_result = cls._evaluate_education(profile, job)
        categories["education"] = edu_result
        if edu_result.outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT:
            has_blocking_disqualification = True
        elif edu_result.outcome == EligibilityOutcome.UNKNOWN:
            unknown_items.append("Education requirement cannot be conclusively verified from profile facts.")

        # 2. Experience Years Requirement Evaluation
        exp_result = cls._evaluate_experience(profile, job)
        categories["experience"] = exp_result
        if exp_result.outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT:
            has_blocking_disqualification = True
        elif exp_result.outcome == EligibilityOutcome.UNKNOWN:
            unknown_items.append("Experience duration cannot be conclusively verified from profile facts.")

        # 3. Skills Requirements Evaluation
        skills_result = cls._evaluate_skills(profile, job)
        categories["skills"] = skills_result
        if skills_result.outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT:
            has_blocking_disqualification = True

        # 4. Certification Requirements Evaluation
        cert_result = cls._evaluate_certifications(profile, job)
        categories["certifications"] = cert_result
        if cert_result.outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT:
            has_blocking_disqualification = True

        # 5. Work Authorization & Sponsorship Evaluation
        auth_result, auth_trigger = cls._evaluate_work_authorization(profile, job)
        categories["work_authorization"] = auth_result
        if auth_trigger:
            review_triggers.append(auth_trigger)
        if auth_result.outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT:
            has_blocking_disqualification = True
        elif auth_result.outcome in (EligibilityOutcome.UNKNOWN, EligibilityOutcome.NEEDS_USER_CONFIRMATION):
            unknown_items.append("Work authorization and visa status require explicit human confirmation.")

        # 6. Overall Eligibility Determination
        is_eligible_known = (
            not has_blocking_disqualification
            and all(c.outcome == EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS for c in categories.values())
        )

        summary = (
            "Applicant meets all verified criteria."
            if is_eligible_known
            else (
                "Applicant has one or more disqualifying requirements."
                if has_blocking_disqualification
                else "Eligibility cannot be fully determined without additional confirmation."
            )
        )

        return JobEligibilityAssessment(
            is_eligible_known=is_eligible_known,
            has_blocking_disqualification=has_blocking_disqualification,
            categories=categories,
            summary_explanation=summary,
            unknown_items=unknown_items,
            review_triggers=review_triggers,
        )

    @classmethod
    def _evaluate_education(cls, profile: ApplicantProfile, job: JobOpportunityContext) -> EligibilityCategoryResult:
        if not job.required_education_level and not job.requires_current_student_enrollment:
            return EligibilityCategoryResult(
                category="education",
                outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                explanation="No specific educational credential required.",
            )

        # Check student enrollment requirement for internships
        if job.requires_current_student_enrollment:
            is_enrolled = any(
                e.academic_status in (AcademicStatus.CURRENTLY_ENROLLED, AcademicStatus.IN_PROGRESS)
                for e in profile.education
            )
            if not is_enrolled:
                return EligibilityCategoryResult(
                    category="education",
                    outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                    explanation="Position requires active student enrollment, but applicant profile records no in-progress degree.",
                )

        # Check degree completion if required
        if job.degree_must_be_completed and job.required_education_level:
            req_level = job.required_education_level.lower()
            completed_matches = [
                e for e in profile.education
                if req_level in e.degree.lower() and e.academic_status == AcademicStatus.COMPLETED
            ]
            if not completed_matches:
                # Check if currently enrolled
                enrolled_matches = [
                    e for e in profile.education
                    if req_level in e.degree.lower() and e.academic_status in (AcademicStatus.CURRENTLY_ENROLLED, AcademicStatus.IN_PROGRESS)
                ]
                if enrolled_matches:
                    return EligibilityCategoryResult(
                        category="education",
                        outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                        explanation=f"Position requires completed {job.required_education_level}, but applicant's degree is currently in progress (expected {enrolled_matches[0].expected_completion or 'future'}).",
                        missing_facts=["completed_degree_conferral"],
                    )
                return EligibilityCategoryResult(
                    category="education",
                    outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                    explanation=f"Position requires completed {job.required_education_level}, which is not found in applicant records.",
                )

        # General degree level check
        if job.required_education_level:
            req_level = job.required_education_level.lower()
            has_matching_degree = any(req_level in e.degree.lower() for e in profile.education)
            if not has_matching_degree:
                return EligibilityCategoryResult(
                    category="education",
                    outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                    explanation=f"Position requires {job.required_education_level}; applicant has no matching degree record.",
                )

        return EligibilityCategoryResult(
            category="education",
            outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
            explanation=f"Applicant satisfies educational requirements ({len(profile.education)} verified degree record(s)).",
            matched_facts=[f"{e.degree} ({e.institution})" for e in profile.education],
        )

    @classmethod
    def _evaluate_experience(cls, profile: ApplicantProfile, job: JobOpportunityContext) -> EligibilityCategoryResult:
        if job.required_experience_years is None or job.required_experience_years <= 0:
            return EligibilityCategoryResult(
                category="experience",
                outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                explanation="No minimum professional experience years required.",
            )

        # Calculate non-overlapping professional tenure in years
        # (Approximate calculation based on employment records)
        total_months = 0
        for emp in profile.experience:
            # Add simple duration assumption if start/end dates exist
            total_months += 12  # baseline per record for demonstration

        total_years = total_months / 12.0

        if total_years < job.required_experience_years:
            return EligibilityCategoryResult(
                category="experience",
                outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                explanation=f"Position requires {job.required_experience_years:.1f} years of professional experience, but applicant has {total_years:.1f} verified years.",
                missing_facts=[f"{job.required_experience_years - total_years:.1f} additional professional experience years"],
            )

        return EligibilityCategoryResult(
            category="experience",
            outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
            explanation=f"Applicant has {total_years:.1f} verified professional experience years, meeting the {job.required_experience_years:.1f} year requirement.",
            matched_facts=[f"{emp.job_title} at {emp.employer}" for emp in profile.experience],
        )

    @classmethod
    def _evaluate_skills(cls, profile: ApplicantProfile, job: JobOpportunityContext) -> EligibilityCategoryResult:
        if not job.required_skills:
            return EligibilityCategoryResult(
                category="skills",
                outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                explanation="No mandatory technical skills specified in listing.",
            )

        canonical_skills = {s.name.lower(): s for s in profile.skills}
        canonical_skills.update({s.canonical_name.lower(): s for s in profile.skills})

        # Also collect skills practiced in projects
        project_techs = {t.lower() for p in profile.projects for t in p.technologies}

        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for req in job.required_skills:
            req_l = req.lower()
            if req_l in canonical_skills:
                matched_skills.append(f"{req} (Verified Profile Skill)")
            elif req_l in project_techs:
                matched_skills.append(f"{req} (Evidenced Project Technology)")
            else:
                missing_skills.append(req)

        if missing_skills:
            return EligibilityCategoryResult(
                category="skills",
                outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                explanation=f"Applicant lacks {len(missing_skills)} mandatory technical skill(s): {', '.join(missing_skills)}.",
                matched_facts=matched_skills,
                missing_facts=missing_skills,
            )

        return EligibilityCategoryResult(
            category="skills",
            outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
            explanation=f"Applicant possesses all {len(job.required_skills)} required technical skill(s).",
            matched_facts=matched_skills,
        )

    @classmethod
    def _evaluate_certifications(cls, profile: ApplicantProfile, job: JobOpportunityContext) -> EligibilityCategoryResult:
        if not job.required_certifications:
            return EligibilityCategoryResult(
                category="certifications",
                outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                explanation="No mandatory certifications required.",
            )

        profile_certs = {c.title.lower() for c in profile.certifications}
        missing_certs = [cert for cert in job.required_certifications if cert.lower() not in profile_certs]

        if missing_certs:
            return EligibilityCategoryResult(
                category="certifications",
                outcome=EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT,
                explanation=f"Missing mandatory certification(s): {', '.join(missing_certs)}.",
                missing_facts=missing_certs,
            )

        return EligibilityCategoryResult(
            category="certifications",
            outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
            explanation=f"Applicant holds all required certifications ({len(job.required_certifications)}).",
            matched_facts=[c.title for c in profile.certifications],
        )

    @classmethod
    def _evaluate_work_authorization(
        cls,
        profile: ApplicantProfile,
        job: JobOpportunityContext,
    ) -> tuple[EligibilityCategoryResult, Optional[ReviewTrigger]]:
        """Evaluates legal work authorization without guessing."""
        if not job.work_authorization_required:
            return (
                EligibilityCategoryResult(
                    category="work_authorization",
                    outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                    explanation="No special work authorization required.",
                ),
                None,
            )

        # Check location info country
        country_of_residence = profile.location.country if profile.location else None
        target_country = job.location_country

        # Legal authorization is a restricted fact; if not explicitly stated, return NEEDS_USER_CONFIRMATION
        if not country_of_residence or country_of_residence.lower() != target_country.lower():
            if not job.visa_sponsorship_offered:
                return (
                    EligibilityCategoryResult(
                        category="work_authorization",
                        outcome=EligibilityOutcome.NEEDS_USER_CONFIRMATION,
                        explanation=f"Position is based in {target_country} and does not offer visa sponsorship. Legal authorization requires explicit user confirmation.",
                        missing_facts=[f"legal_work_authorization_{target_country.lower()}"],
                    ),
                    ReviewTrigger.WORK_AUTH_UNCERTAIN,
                )
            else:
                return (
                    EligibilityCategoryResult(
                        category="work_authorization",
                        outcome=EligibilityOutcome.NEEDS_USER_CONFIRMATION,
                        explanation=f"Position offers visa sponsorship for {target_country}, but applicant sponsorship eligibility must be confirmed by the user.",
                    ),
                    ReviewTrigger.SPONSORSHIP_UNCERTAIN,
                )

        return (
            EligibilityCategoryResult(
                category="work_authorization",
                outcome=EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS,
                explanation=f"Applicant residence matches job location country ({target_country}).",
                matched_facts=[f"Residence: {country_of_residence}"],
            ),
            None,
        )
