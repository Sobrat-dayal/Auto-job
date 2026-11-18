"""Unit tests for Section 108: Job Eligibility Evaluator with Student Applicant Fixture."""

import pytest
from app.recruitment.policy.contracts import (
    EligibilityOutcome,
    JobOpportunityContext,
    ReviewTrigger,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
    EducationRecord,
    LocationInfo,
    ProjectRecord,
    SkillCategory,
    SkillItem,
)


@pytest.fixture
def student_applicant() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_student_01",
        owner_id="usr_student",
        display_label="Student Developer",
        education=[
            EducationRecord(
                id="edu_curr_01",
                institution="University of California, Berkeley",
                degree="Bachelor of Science in Computer Science",
                field_of_study="Computer Science",
                academic_status=AcademicStatus.CURRENTLY_ENROLLED,
                start_date="2023-09",
                expected_completion="2027-05",
            )
        ],
        experience=[],  # 0 professional experience years
        projects=[
            ProjectRecord(
                id="proj_acad_01",
                title="Distributed Key-Value Store",
                description="Class project implementing Raft consensus in Python",
                technologies=["Python", "gRPC"],
            )
        ],
        skills=[
            SkillItem(
                id="skl_py",
                name="Python",
                canonical_name="python",
                category=SkillCategory.PROGRAMMING_LANGUAGES,
            )
        ],
        certifications=[],
        location=LocationInfo(),  # Work authorization country unspecified
    )


def test_student_internship_eligibility(student_applicant: ApplicantProfile):
    # 1. Internship requiring current enrollment -> MEETS
    job_intern = JobOpportunityContext(
        title="Software Engineering Summer Intern",
        employer_name="Stripe",
        requires_current_student_enrollment=True,
        required_skills=["Python"],
    )
    assessment = JobEligibilityEvaluator.evaluate_eligibility(student_applicant, job_intern)
    assert assessment.categories["education"].outcome == EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS
    assert assessment.categories["skills"].outcome == EligibilityOutcome.MEETS_KNOWN_REQUIREMENTS


def test_student_completed_degree_requirement_fails(student_applicant: ApplicantProfile):
    # 3. Position requiring completed bachelor's degree immediately -> DOES_NOT_MEET
    job_degree_req = JobOpportunityContext(
        title="Software Engineer I",
        employer_name="Google",
        required_education_level="Bachelor",
        degree_must_be_completed=True,
    )
    assessment = JobEligibilityEvaluator.evaluate_eligibility(student_applicant, job_degree_req)
    assert assessment.categories["education"].outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT
    assert "currently in progress" in assessment.categories["education"].explanation
    assert assessment.has_blocking_disqualification is True


def test_student_experience_years_fails(student_applicant: ApplicantProfile):
    # 4. Position requiring 3 years of professional work -> DOES_NOT_MEET
    job_mid = JobOpportunityContext(
        title="Backend Engineer",
        employer_name="Netflix",
        required_experience_years=3.0,
    )
    assessment = JobEligibilityEvaluator.evaluate_eligibility(student_applicant, job_mid)
    assert assessment.categories["experience"].outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT
    assert "requires 3.0 years" in assessment.categories["experience"].explanation
    assert assessment.has_blocking_disqualification is True


def test_student_unsupported_certification_fails(student_applicant: ApplicantProfile):
    # 5. Position requiring unsupported certification (AWS Certified Solutions Architect) -> DOES_NOT_MEET
    job_cert = JobOpportunityContext(
        title="Cloud Software Engineer",
        employer_name="Amazon Web Services",
        required_certifications=["AWS Certified Solutions Architect - Associate"],
    )
    assessment = JobEligibilityEvaluator.evaluate_eligibility(student_applicant, job_cert)
    assert assessment.categories["certifications"].outcome == EligibilityOutcome.DOES_NOT_MEET_REQUIREMENT
    assert assessment.has_blocking_disqualification is True


def test_student_work_authorization_unspecified(student_applicant: ApplicantProfile):
    # 6. Position requiring verified work authorization in US when unspecified in candidate profile -> NEEDS_USER_CONFIRMATION
    job_auth = JobOpportunityContext(
        title="Software Engineer Intern",
        employer_name="TechCorp",
        work_authorization_required=True,
        visa_sponsorship_offered=False,
        location_country="United States",
    )
    assessment = JobEligibilityEvaluator.evaluate_eligibility(student_applicant, job_auth)
    assert assessment.categories["work_authorization"].outcome == EligibilityOutcome.NEEDS_USER_CONFIRMATION
    assert ReviewTrigger.WORK_AUTH_UNCERTAIN in assessment.review_triggers
    assert assessment.is_eligible_known is False  # Cannot claim FullyEligible when authorization is unknown
