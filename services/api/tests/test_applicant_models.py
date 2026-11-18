"""Unit tests for Stage 21 Applicant Profile Pydantic models, contracts, and validation rules."""

import pytest

from app.recruitment.profile.contracts import (
    AchievementItem,
    ApplicantClaim,
    ApplicantProfile,
    CertificationRecord,
    ClaimCategory,
    ContactInfo,
    DataQualityIssue,
    DataQualityReport,
    EducationRecord,
    EmploymentEligibility,
    EmploymentRecord,
    EvidenceMetadata,
    LocationInfo,
    ProficiencyLevel,
    ProfileConflict,
    QualitySeverity,
    SkillCategory,
    SkillItem,
    VerificationStatus,
)


def test_applicant_profile_defaults():
    profile = ApplicantProfile(
        id="prof_test_123",
        owner_id="user_test_456",
        display_label="Senior Cloud Engineer",
        status="active",
        version=1,
    )

    assert profile.id == "prof_test_123"
    assert profile.owner_id == "user_test_456"
    assert profile.version == 1
    assert profile.education == []
    assert profile.experience == []
    assert profile.skills == []
    assert profile.projects == []
    assert profile.certifications == []
    assert profile.created_at is not None
    assert profile.updated_at is not None


def test_contact_and_location_models():
    contact = ContactInfo(
        legal_name="John Doe",
        preferred_name="Johnny",
        primary_email="johnny@example.com",
        phone="+1-555-0199",
        portfolio_url="https://johndoe.dev",
    )
    assert contact.legal_name == "John Doe"
    assert contact.primary_email == "johnny@example.com"
    assert contact.phone == "+1-555-0199"

    location = LocationInfo(
        city="Austin",
        state_province="TX",
        postal_code="78701",
        country="United States",
        remote_preference="flexible",
    )
    assert location.city == "Austin"
    assert location.country == "United States"
    assert location.remote_preference == "flexible"


def test_employment_eligibility_model():
    eligibility = EmploymentEligibility(
        authorized_countries=["United States"],
        requires_sponsorship=False,
        notice_period_days=14,
        available_start_date="2026-12-01",
        confirmed_by_user=True,
    )
    assert eligibility.requires_sponsorship is False
    assert eligibility.authorized_countries == ["United States"]
    assert eligibility.notice_period_days == 14
    assert eligibility.confirmed_by_user is True


def test_education_and_experience_models():
    edu = EducationRecord(
        id="edu_1",
        institution="MIT",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        start_date="2016-09",
        end_date="2020-05",
        gpa=3.92,
        distinctions=["Dean's List", "Tau Beta Pi"],
    )
    assert edu.institution == "MIT"
    assert len(edu.distinctions) == 2

    ach = AchievementItem(
        id="ach_1",
        statement="Reduced system p99 latency by 72% using Rust caching layer",
        metric_value="72%",
        metric_unit="percent",
    )
    assert "latency" in ach.statement

    exp = EmploymentRecord(
        id="exp_1",
        employer="Tech Global Corp",
        job_title="Lead Distributed Systems Engineer",
        start_date="2021-01",
        is_current=True,
        achievements=[ach],
        technologies=["Python", "Rust", "PostgreSQL", "Kafka"],
    )
    assert exp.is_current is True
    assert len(exp.achievements) == 1
    assert "Rust" in exp.technologies


def test_skill_item_validation():
    skill = SkillItem(
        id="sk_1",
        name="FastAPI",
        canonical_name="fastapi",
        category=SkillCategory.BACKEND,
        proficiency=ProficiencyLevel.EXPERT,
        years_experience=4.5,
    )
    assert skill.canonical_name == "fastapi"
    assert skill.category == SkillCategory.BACKEND
    assert skill.proficiency == ProficiencyLevel.EXPERT


def test_evidence_metadata_validation():
    sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    evidence = EvidenceMetadata(
        evidence_id="ev_1",
        profile_id="prof_1",
        filename="resume_verified.pdf",
        storage_path="/data/artifacts/evidence/ev_1.pdf",
        content_hash=sha,
        file_size_bytes=1048576,
        file_type="pdf",
        source_category="resume",
    )
    assert len(evidence.content_hash) == 64
    assert evidence.file_size_bytes == 1048576


def test_claim_and_conflict_models():
    claim = ApplicantClaim(
        claim_id="cl_1",
        profile_id="prof_1",
        category=ClaimCategory.SKILL,
        normalized_value="Skill: FastAPI (expert)",
        original_text="Expert in FastAPI with 4 years experience",
        verification_status=VerificationStatus.EVIDENCE_SUPPORTED,
    )
    assert claim.verification_status == VerificationStatus.EVIDENCE_SUPPORTED
    assert claim.category == ClaimCategory.SKILL

    conflict = ProfileConflict(
        conflict_id="conf_1",
        profile_id="prof_1",
        claim_id_a="cl_1",
        claim_id_b="cl_2",
        category=ClaimCategory.EMPLOYMENT,
        field_name="employment.current_employer",
        description="Conflicting current employers",
    )
    assert conflict.resolution_status == "pending"
    assert conflict.claim_id_a == "cl_1"


def test_data_quality_report():
    report = DataQualityReport(
        profile_id="prof_1",
        completeness_score=90.0,
        is_recruitment_ready=True,
        category_breakdown={"contact": 100.0, "education": 90.0, "skills": 85.0},
        issues=[
            DataQualityIssue(
                code="SKILLS_NEED_EVIDENCE",
                severity=QualitySeverity.WARNING,
                category="evidence",
                field_ref="skills",
                message="Some skills lack uploaded document evidence",
            )
        ],
    )
    assert report.completeness_score == 90.0
    assert report.is_recruitment_ready is True
    assert len(report.issues) == 1
