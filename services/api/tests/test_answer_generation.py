"""Unit Tests for Factual Answer Generation, Duration Calculation & Answer Validation (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
    ContactInfo,
    EducationRecord,
    EmploymentRecord,
    EmploymentType,
    LocationInfo,
    ProjectRecord,
    SkillCategory,
    SkillItem,
    VerificationStatus,
)
from app.recruitment.writing.answers.experience_calc import ExperienceCalculator
from app.recruitment.writing.answers.generation import AnswerGenerator
from app.recruitment.writing.answers.validation import AnswerValidator
from app.recruitment.writing.contracts import (
    AnswerState,
    AnswerType,
    ApplicationAnswer,
    ApplicationQuestionRecord,
    QuestionCategory,
)


@pytest.fixture
def applicant_profile() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_calc_test",
        owner_id="user_test",
        contact=ContactInfo(legal_name="Alex Mercer"),
        location=LocationInfo(city="San Francisco", country="United States"),
        education=[
            EducationRecord(
                institution="UC Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2022-09",
                end_date="2026-05",
                academic_status=AcademicStatus.CURRENTLY_ENROLLED,
                expected_completion="2026-05",
            )
        ],
        skills=[
            SkillItem(
                name="Python",
                canonical_name="python",
                category=SkillCategory.PROGRAMMING_LANGUAGES,
                verification_status=VerificationStatus.USER_CONFIRMED,
                years_experience=3.0,
            ),
            SkillItem(
                name="FastAPI",
                canonical_name="fastapi",
                category=SkillCategory.BACKEND,
                verification_status=VerificationStatus.USER_CONFIRMED,
                years_experience=2.0,
            ),
        ],
        experience=[
            EmploymentRecord(
                employer="Startup Co",
                job_title="Software Intern",
                employment_type=EmploymentType.INTERNSHIP,
                start_date="2023-06",
                end_date="2023-09",
                technologies=["Python", "FastAPI"],
            ),
            EmploymentRecord(
                employer="Scale Systems",
                job_title="Junior Backend Engineer",
                employment_type=EmploymentType.FULL_TIME,
                start_date="2023-10",
                end_date="2024-10",
                technologies=["Python", "PostgreSQL"],
            ),
        ],
        projects=[
            ProjectRecord(
                title="Distributed Cache",
                description="In-memory key-value cache engine",
                technologies=["Python", "Redis"],
                applicant_contribution="Implemented LRU eviction and memory bounds",
            )
        ],
    )


def test_experience_calculator(applicant_profile: ApplicantProfile):
    breakdown = ExperienceCalculator.calculate_experience_breakdown(applicant_profile)
    assert breakdown["internship"] >= 0.2
    assert breakdown["professional_employment"] >= 1.0
    assert breakdown["total_work_experience"] >= 1.2

    py_years = ExperienceCalculator.get_technology_experience_years(applicant_profile, "Python")
    assert py_years == 3.0


def test_answer_generator_education_expected_date(applicant_profile: ApplicantProfile):
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="When do you expect to graduate?",
        normalized_question="when do you expect to graduate",
        category=QuestionCategory.EDUCATION,
        answer_type=AnswerType.DATE,
    )
    ans = AnswerGenerator.generate_answer(q, applicant_profile)
    assert ans.state == AnswerState.AVAILABLE_CONFIRMED
    assert "Expected 2026-05" in ans.answer_text or "2026-05" in ans.answer_text


def test_answer_generator_projects(applicant_profile: ApplicantProfile):
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="Describe a technical project you implemented.",
        normalized_question="describe a technical project you implemented",
        category=QuestionCategory.PROJECTS,
        answer_type=AnswerType.PARAGRAPH,
    )
    ans = AnswerGenerator.generate_answer(q, applicant_profile)
    assert ans.state == AnswerState.AVAILABLE_EVIDENCE_SUPPORTED
    assert "Distributed Cache" in ans.answer_text
    assert "Implemented LRU eviction" in ans.answer_text


def test_answer_generator_multiple_choice_matching(applicant_profile: ApplicantProfile):
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="Which technologies have you used?",
        normalized_question="which technologies have you used",
        category=QuestionCategory.SKILLS,
        answer_type=AnswerType.MULTIPLE_CHOICE,
        allowed_options=["Python", "Ruby", "Haskell", "FastAPI"],
    )
    ans = AnswerGenerator.generate_answer(q, applicant_profile)
    assert "Python" in ans.selected_options
    assert "FastAPI" in ans.selected_options
    assert "Ruby" not in ans.selected_options


def test_answer_validator_constraints():
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="Summarize your role (max 50 chars)",
        normalized_question="summarize your role",
        category=QuestionCategory.EXPERIENCE,
        answer_type=AnswerType.SHORT_TEXT,
        max_characters=50,
    )

    ans_valid = ApplicationAnswer(
        question_id=q.id,
        profile_id="p1",
        profile_version=1,
        answer_text="Backend engineer working with Python and FastAPI.",
    )
    val = AnswerValidator.validate_answer(ans_valid, q)
    assert val["is_valid"]

    ans_invalid = ApplicationAnswer(
        question_id=q.id,
        profile_id="p1",
        profile_version=1,
        answer_text="This answer is intentionally way too long and significantly exceeds the maximum character threshold of fifty characters.",
    )
    val2 = AnswerValidator.validate_answer(ans_invalid, q)
    assert not val2["is_valid"]
    assert any("exceeds character limit" in iss for iss in val2["issues"])
