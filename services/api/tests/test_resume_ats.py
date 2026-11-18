"""Unit tests for Stage 23 ATS readability auditing and machine-parsing verification."""

import pytest
from app.recruitment.resume.contracts import (
    ResumeDocument,
    ResumeSection,
    ResumeEntry,
    ResumeType,
    SectionType,
    DocumentStatus,
    PageFormat,
    ATSCheckStatus,
)
from app.recruitment.resume.ats.readability import ATSReadabilityAnalyzer


@pytest.fixture
def sample_resume() -> ResumeDocument:
    return ResumeDocument(
        id="res_ats_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="ATS Valid Resume",
        resume_type=ResumeType.GENERAL,
        target_role="Software Engineer",
        job_ref=None,
        template_id="ats_classic",
        template_version="1.0.0",
        status=DocumentStatus.DRAFT,
        current_version=1,
        locale="en_US",
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={
            "legal_name": "Taylor Swiftly",
            "primary_email": "taylor.swiftly@example.com",
            "phone": "+1-555-0188",
            "portfolio_url": "https://github.com/tswiftly",
        },
        sections=[
            ResumeSection(
                id="sec_1",
                section_type=SectionType.SUMMARY,
                display_title="Professional Summary",
                ordering=0,
                entries=[
                    ResumeEntry(
                        id="ent_sum",
                        title="Summary",
                        description="Software Engineer with 4 years building web and cloud services across scalable distributed systems and backend architectures.",
                    )
                ],
            ),
            ResumeSection(
                id="sec_2",
                section_type=SectionType.EXPERIENCE,
                display_title="Work Experience",
                ordering=1,
                entries=[
                    ResumeEntry(
                        id="ent_exp",
                        title="Software Engineer",
                        organization="Core Systems LLC",
                        start_date="2020-01-01",
                        end_date="2023-05-01",
                        bullet_points=[
                            "Developed microservices with Python and PostgreSQL handling high traffic",
                            "Implemented automated test pipelines using Pytest with 95% branch coverage",
                        ],
                    )
                ],
            ),
            ResumeSection(
                id="sec_3",
                section_type=SectionType.EDUCATION,
                display_title="Education",
                ordering=2,
                entries=[
                    ResumeEntry(
                        id="ent_edu",
                        title="B.S. in Computer Science",
                        organization="MIT",
                        start_date="2016-09-01",
                        end_date="2020-05-01",
                    )
                ],
            ),
            ResumeSection(
                id="sec_4",
                section_type=SectionType.SKILLS,
                display_title="Technical Skills",
                ordering=3,
                entries=[
                    ResumeEntry(
                        id="ent_sk",
                        title="Languages & Frameworks",
                        description="Python, TypeScript, FastAPI, React, PostgreSQL, Docker, Linux",
                    )
                ],
            ),
        ],
    )


def test_ats_readability_audit_passes(sample_resume: ResumeDocument):
    report = ATSReadabilityAnalyzer.evaluate_document(sample_resume)

    assert report.overall_status in [ATSCheckStatus.PASS, ATSCheckStatus.WARNING]
    assert report.error_count == 0

    check_names = [c.check_name for c in report.checks]
    assert "Machine-Readable Text" in check_names
    assert "Standard Section Headings" in check_names


def test_ats_readability_audit_detects_missing_contact(sample_resume: ResumeDocument):
    sample_resume.header_contact = {}  # Empty contact
    report = ATSReadabilityAnalyzer.evaluate_document(sample_resume)

    contact_check = next(c for c in report.checks if "Contact" in c.check_name)
    assert contact_check.status in [ATSCheckStatus.WARNING, ATSCheckStatus.ERROR]
