"""Unit & Integration Tests for Cover Letter Generation, Templates, Validation & Export (Stage 24)."""

from __future__ import annotations

import os
from pathlib import Path
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
from app.recruitment.writing.contracts import (
    CoverLetterContentBlock,
    CoverLetterDocument,
    CoverLetterExportRequest,
    CoverLetterType,
    WritingDocumentStatus,
    WritingLength,
    WritingTone,
)
from app.recruitment.writing.cover_letters.exports import CoverLetterExportManager
from app.recruitment.writing.cover_letters.generation import CoverLetterGenerator
from app.recruitment.writing.cover_letters.templates import CoverLetterTemplateRegistry
from app.recruitment.writing.cover_letters.validation import CoverLetterValidator
from app.recruitment.writing.cover_letters.versions import CoverLetterVersionManager


@pytest.fixture
def sample_profile() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_test_writing",
        owner_id="user_test",
        contact=ContactInfo(
            legal_name="Alex Mercer",
            primary_email="alex.mercer@example.com",
            phone="+1 (555) 234-5678",
            portfolio_url="https://alexmercer.dev",
        ),
        location=LocationInfo(
            city="San Francisco",
            country="United States",
        ),
        education=[
            EducationRecord(
                institution="University of California, Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2022-09",
                end_date="2026-05",
                academic_status=AcademicStatus.CURRENTLY_ENROLLED,
                gpa=3.85,
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
                employer="CloudScale Systems",
                job_title="Software Engineering Intern",
                employment_type=EmploymentType.INTERNSHIP,
                start_date="2024-06",
                end_date="2024-09",
                technologies=["Python", "FastAPI", "Docker"],
            )
        ],
        projects=[
            ProjectRecord(
                title="Distributed Event Pipeline",
                description="High-throughput stream processing microservice",
                technologies=["Python", "FastAPI", "Redis"],
                applicant_contribution="Implemented event ingestion routes and buffer workers",
            )
        ],
    )


def test_template_registry():
    templates = CoverLetterTemplateRegistry.list_templates()
    assert len(templates) >= 6
    ids = [t.id for t in templates]
    assert "classic_professional" in ids
    assert "modern_minimalist" in ids
    assert "technical_engineering" in ids
    assert "internship_graduate" in ids


def test_cover_letter_generation_internship(sample_profile: ApplicantProfile):
    blocks = CoverLetterGenerator.generate_blocks(
        profile=sample_profile,
        target_role="Software Engineering Intern",
        letter_type=CoverLetterType.INTERNSHIP,
        employer_name="Stripe",
        tone=WritingTone.EARLY_CAREER,
        length_preference=WritingLength.STANDARD,
    )
    assert len(blocks) >= 6
    block_types = [b.block_type for b in blocks]
    assert "header" in block_types
    assert "salutation" in block_types
    assert "opening" in block_types
    assert "qualifications" in block_types
    assert "evidence_example" in block_types
    assert "closing" in block_types
    assert "signature" in block_types

    full_text = "\n".join([b.text for b in blocks])
    assert "Alex Mercer" in full_text
    assert "Stripe" in full_text
    assert "University of California, Berkeley" in full_text
    assert "Distributed Event Pipeline" in full_text


def test_cover_letter_validation_grounding(sample_profile: ApplicantProfile):
    blocks = CoverLetterGenerator.generate_blocks(
        profile=sample_profile,
        target_role="Backend Engineer",
        letter_type=CoverLetterType.ROLE_SPECIFIC,
        employer_name="TechCorp",
    )
    doc = CoverLetterDocument(
        profile_id=sample_profile.id,
        profile_snapshot_id="snap_01",
        title="Valid Cover Letter",
        target_role="Backend Engineer",
        employer_name="TechCorp",
        blocks=blocks,
    )

    result = CoverLetterValidator.validate_cover_letter(doc, sample_profile)
    assert result["is_valid"]
    assert result["grounding_status"] == "grounded"


def test_cover_letter_versioning_lifecycle(sample_profile: ApplicantProfile):
    mgr = CoverLetterVersionManager()
    doc = CoverLetterDocument(
        profile_id=sample_profile.id,
        profile_snapshot_id="snap_01",
        title="Versioned Cover Letter",
        target_role="Backend Engineer",
        employer_name="TechCorp",
        blocks=[
            CoverLetterContentBlock(
                block_type="opening",
                text="Opening paragraph text.",
                ordering=0,
            )
        ],
    )

    record = mgr.snapshot_version(doc, actor_id="user_test", changelog="First approval")
    assert record.version_number == 1
    assert len(record.content_hash) == 64
    assert doc.status == WritingDocumentStatus.APPROVED

    versions = mgr.list_versions(doc.id)
    assert len(versions) == 1
    assert versions[0].content_hash == record.content_hash

    # Restore into fresh draft
    restored = mgr.restore_version(doc.id, 1, doc)
    assert restored.current_version == 2
    assert restored.status == WritingDocumentStatus.DRAFT


def test_cover_letter_export_docx_and_pdf(sample_profile: ApplicantProfile, tmp_path: Path):
    blocks = CoverLetterGenerator.generate_blocks(
        profile=sample_profile,
        target_role="Software Engineer",
        letter_type=CoverLetterType.ROLE_SPECIFIC,
        employer_name="InnovateInc",
    )
    doc = CoverLetterDocument(
        id="cl_export_test",
        profile_id=sample_profile.id,
        profile_snapshot_id="snap_01",
        title="Export Test Cover Letter",
        target_role="Software Engineer",
        employer_name="InnovateInc",
        blocks=blocks,
    )

    # 1. Export PDF
    pdf_req = CoverLetterExportRequest(format="pdf", validate_extraction=True)
    pdf_res = CoverLetterExportManager.export(doc, pdf_req)
    assert pdf_res["format"] == "pdf"
    assert pdf_res["file_size_bytes"] > 0
    assert os.path.exists(pdf_res["file_path"])
    assert pdf_res["validation"]["all_passed"]

    # 2. Export DOCX
    docx_req = CoverLetterExportRequest(format="docx")
    docx_res = CoverLetterExportManager.export(doc, docx_req)
    assert docx_res["format"] == "docx"
    assert docx_res["file_size_bytes"] > 0
    assert os.path.exists(docx_res["file_path"])
