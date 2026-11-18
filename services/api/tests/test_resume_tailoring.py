"""Unit tests for Stage 23 job description parsing and evidence-grounded tailoring."""

import pytest
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    EmploymentRecord,
    SkillItem,
    SkillCategory,
    ProficiencyLevel,
)
from app.recruitment.resume.tailoring.job_parser import JobDescriptionParser
from app.recruitment.resume.tailoring.evidence_matching import EvidenceMatchingEngine
from app.recruitment.resume.tailoring.prioritization import ContentPrioritizationEngine
from app.recruitment.resume.contracts import (
    RequirementMatchCategory,
    ResumeDocument,
    ResumeSection,
    ResumeEntry,
    ResumeType,
    SectionType,
    DocumentStatus,
    PageFormat,
)


@pytest.fixture
def applicant_profile() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_tailor_01",
        owner_id="usr_01",
        contact=ContactInfo(
            legal_name="Jordan Lee",
            primary_email="jordan.lee@example.com",
            phone="+1-555-0144",
        ),
        skills=[
            SkillItem(id="sk_01", name="Python", canonical_name="python", category=SkillCategory.PROGRAMMING_LANGUAGES, proficiency=ProficiencyLevel.EXPERT),
            SkillItem(id="sk_02", name="FastAPI", canonical_name="fastapi", category=SkillCategory.BACKEND, proficiency=ProficiencyLevel.ADVANCED),
            SkillItem(id="sk_03", name="PostgreSQL", canonical_name="postgresql", category=SkillCategory.DATABASES, proficiency=ProficiencyLevel.ADVANCED),
            SkillItem(id="sk_04", name="Docker", canonical_name="docker", category=SkillCategory.CLOUD_DEVOPS, proficiency=ProficiencyLevel.INTERMEDIATE),
        ],
        experience=[
            EmploymentRecord(
                id="exp_01",
                employer="FinTech Labs",
                job_title="Backend Developer",
                start_date="2021-03-01",
                end_date=None,
                is_current=True,
                technologies=["Python", "FastAPI", "PostgreSQL"],
            )
        ],
    )


def test_job_description_parser():
    raw_job = """
    Senior Python Backend Engineer - Cloud Platforms
    Employer: Acme Cloud Corp
    Location: Remote
    
    Requirements:
    - 4+ years of professional development experience in Python
    - Strong proficiency in FastAPI or Flask framework
    - Hands-on experience with PostgreSQL and relational schema design
    - Experience with Docker containerization
    - Familiarity with Kubernetes orchestration and AWS cloud architecture
    
    Responsibilities:
    - Build scalable microservices for distributed cloud deployment
    - Ensure 99.9% uptime and low latency API endpoints
    """

    snapshot = JobDescriptionParser.parse_job_description(
        raw_text=raw_job,
        job_title="Senior Python Backend Engineer",
        employer="Acme Cloud Corp",
    )

    assert snapshot.job_title == "Senior Python Backend Engineer"
    assert len(snapshot.tech_stack) > 0
    all_tech = [t.lower() for t in snapshot.tech_stack]
    assert "python" in all_tech
    assert "fastapi" in all_tech


def test_evidence_matching_engine_no_hallucinations(applicant_profile: ApplicantProfile):
    raw_job = """
    Requirements:
    - Experience with Python
    - Experience with FastAPI
    - Experience with Rust
    """
    snapshot = JobDescriptionParser.parse_job_description(raw_text=raw_job)

    mappings = EvidenceMatchingEngine.match_requirements(snapshot, applicant_profile)

    # Check that Python is directly supported
    python_matches = [m for m in mappings if "python" in m.requirement_text.lower()]
    assert len(python_matches) > 0
    assert python_matches[0].match_category == RequirementMatchCategory.DIRECTLY_SUPPORTED

    # Check that Rust (not in profile) is marked as NOT_EVIDENCED
    rust_matches = [m for m in mappings if "rust" in m.requirement_text.lower()]
    if rust_matches:
        assert rust_matches[0].match_category == RequirementMatchCategory.NOT_EVIDENCED
        assert rust_matches[0].claim_id is None


def test_content_prioritization():
    doc = ResumeDocument(
        id="res_prio_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Software Engineer Resume",
        resume_type=ResumeType.GENERAL,
        status=DocumentStatus.DRAFT,
        current_version=1,
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={"legal_name": "Jordan Lee"},
        sections=[
            ResumeSection(
                id="sec_skills",
                section_type=SectionType.SKILLS,
                display_title="Technical Skills",
                ordering=0,
                entries=[
                    ResumeEntry(
                        id="ent_sk",
                        title="Languages",
                        tags=["C++", "Python", "Java"],
                        description="C++, Python, Java",
                    )
                ],
            )
        ],
    )

    raw_job = "Need strong Python development skills."
    snapshot = JobDescriptionParser.parse_job_description(raw_text=raw_job)
    profile = ApplicantProfile(
        id="p1",
        owner_id="u1",
        skills=[SkillItem(name="Python", canonical_name="python", category=SkillCategory.PROGRAMMING_LANGUAGES)],
    )
    mappings = EvidenceMatchingEngine.match_requirements(snapshot, profile)

    prioritized_doc = ContentPrioritizationEngine.prioritize_resume(doc, mappings)
    tags = prioritized_doc.sections[0].entries[0].tags
    assert tags[0] == "Python"
