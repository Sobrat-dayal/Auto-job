"""Unit tests for Stage 23 resume content extraction, synthesis, and validation."""

import pytest
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    EducationRecord,
    EmploymentRecord,
    AchievementItem,
    ProjectRecord,
    SkillItem,
    SkillCategory,
    ProficiencyLevel,
)
from app.recruitment.resume.contracts import ResumeType, ResumeDocument, DocumentStatus, PageFormat
from app.recruitment.resume.content.fact_selection import FactSelectionEngine
from app.recruitment.resume.content.summary import ProfessionalSummaryGenerator
from app.recruitment.resume.content.skills import SkillsOrganizationEngine
from app.recruitment.resume.content.experience import ExperienceBulletEngine
from app.recruitment.resume.content.projects import ProjectEntryEngine
from app.recruitment.resume.content.content_validation import ContentValidationEngine


@pytest.fixture
def sample_profile() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_test_01",
        owner_id="usr_test_01",
        contact=ContactInfo(
            legal_name="Morgan Chen",
            primary_email="morgan.chen@example.com",
            phone="+1-555-0199",
            portfolio_url="https://github.com/morganchen",
        ),
        education=[
            EducationRecord(
                id="edu_01",
                institution="University of Washington",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2018-09-01",
                end_date="2022-06-01",
                gpa=3.85,
            )
        ],
        experience=[
            EmploymentRecord(
                id="exp_01",
                employer="CloudCorp",
                job_title="Backend Software Engineer",
                start_date="2022-07-01",
                end_date=None,
                is_current=True,
                achievements=[
                    AchievementItem(
                        id="ach_01",
                        statement="Engineered distributed REST APIs handling 50k requests/minute using FastAPI",
                        metric_unit="throughput",
                        metric_value="50k req/min",
                    ),
                    AchievementItem(
                        id="ach_02",
                        statement="Migrated monolithic database to partitioned PostgreSQL cluster with zero downtime",
                    ),
                ],
                technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
            )
        ],
        projects=[
            ProjectRecord(
                id="proj_01",
                title="Autonom Multi-Agent Core",
                description="Autonomous multi-agent task execution platform",
                technologies=["Python", "FastAPI", "React", "TypeScript"],
                repo_url="https://github.com/morganchen/autonom-core",
            )
        ],
        skills=[
            SkillItem(id="sk_01", name="Python", canonical_name="python", category=SkillCategory.PROGRAMMING_LANGUAGES, proficiency=ProficiencyLevel.EXPERT),
            SkillItem(id="sk_02", name="TypeScript", canonical_name="typescript", category=SkillCategory.PROGRAMMING_LANGUAGES, proficiency=ProficiencyLevel.ADVANCED),
            SkillItem(id="sk_03", name="FastAPI", canonical_name="fastapi", category=SkillCategory.BACKEND, proficiency=ProficiencyLevel.EXPERT),
            SkillItem(id="sk_04", name="Docker", canonical_name="docker", category=SkillCategory.CLOUD_DEVOPS, proficiency=ProficiencyLevel.INTERMEDIATE),
            SkillItem(id="sk_05", name="PostgreSQL", canonical_name="postgresql", category=SkillCategory.DATABASES, proficiency=ProficiencyLevel.ADVANCED),
        ],
    )


def test_fact_selection_engine():
    order = FactSelectionEngine.get_section_order(ResumeType.EXPERIENCED)
    assert len(order) > 0


def test_summary_generation_deterministic(sample_profile: ApplicantProfile):
    summary = ProfessionalSummaryGenerator.generate_summary(
        profile=sample_profile,
        target_role="Senior Backend Engineer",
    )
    assert len(summary) > 20
    assert "Senior Backend Engineer" in summary or "Morgan Chen" in summary or "Python" in summary


def test_skill_categorization(sample_profile: ApplicantProfile):
    grouped_entries = SkillsOrganizationEngine.group_skills(sample_profile.skills)
    assert len(grouped_entries) > 0
    languages_entry = next((e for e in grouped_entries if e.title == "Languages"), None)
    assert languages_entry is not None
    assert "Python" in languages_entry.description


def test_experience_bullet_engine(sample_profile: ApplicantProfile):
    entry = ExperienceBulletEngine.transform_experience(sample_profile.experience[0])
    assert entry.title == "Backend Software Engineer"
    assert entry.organization == "CloudCorp"
    assert len(entry.bullet_points) == 2
    assert "FastAPI" in entry.bullet_points[0]


def test_project_entry_engine(sample_profile: ApplicantProfile):
    entry = ProjectEntryEngine.transform_project(sample_profile.projects[0])
    assert entry.title == "Autonom Multi-Agent Core"
    assert len(entry.bullet_points) > 0


def test_content_validator_no_hallucinations(sample_profile: ApplicantProfile):
    doc = ResumeDocument(
        id="res_val_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Valid Resume",
        resume_type=ResumeType.GENERAL,
        status=DocumentStatus.DRAFT,
        current_version=1,
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={"legal_name": "Morgan Chen"},
        sections=[],
    )
    issues = ContentValidationEngine.validate_document(doc, sample_profile)
    assert len(issues) == 0
