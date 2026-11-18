"""Unit tests for Stage 23 dual document renderers (DOCX and PDF) and round-trip extraction."""

import os
import tempfile
import pytest
from docx import Document
from pypdf import PdfReader

from app.recruitment.resume.contracts import (
    ResumeDocument,
    ResumeSection,
    ResumeEntry,
    ResumeType,
    SectionType,
    DocumentStatus,
    PageFormat,
)
from app.recruitment.resume.templates.registry import ResumeTemplateRegistry
from app.recruitment.resume.renderers.docx_renderer import DocxRenderer
from app.recruitment.resume.renderers.pdf_renderer import PdfRenderer
from app.recruitment.resume.renderers.validation import DocumentRoundTripValidator


@pytest.fixture
def printable_resume() -> ResumeDocument:
    return ResumeDocument(
        id="res_render_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Alex Mercer - Senior Software Engineer",
        resume_type=ResumeType.EXPERIENCED,
        target_role="Senior Software Engineer",
        job_ref=None,
        template_id="ats_classic",
        template_version="1.0.0",
        status=DocumentStatus.APPROVED,
        current_version=1,
        locale="en_US",
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={
            "legal_name": "Alex Mercer",
            "primary_email": "alex.mercer@example.com",
            "phone": "+1 (555) 019-2834",
            "portfolio_url": "https://github.com/alexmercer",
        },
        sections=[
            ResumeSection(
                id="sec_sum",
                section_type=SectionType.SUMMARY,
                display_title="Professional Summary",
                ordering=0,
                entries=[
                    ResumeEntry(
                        id="e_sum",
                        title="Summary",
                        description="Senior Software Engineer with 6+ years designing distributed cloud architectures.",
                    )
                ],
            ),
            ResumeSection(
                id="sec_exp",
                section_type=SectionType.EXPERIENCE,
                display_title="Work Experience",
                ordering=1,
                entries=[
                    ResumeEntry(
                        id="e_exp_1",
                        title="Lead Systems Architect",
                        organization="CloudNative Corp",
                        location="San Francisco, CA",
                        start_date="2022-01-01",
                        end_date=None,
                        is_current=True,
                        bullet_points=[
                            "Engineered distributed event ingestion processing 120,000 requests/sec with FastAPI",
                            "Reduced end-to-end processing latency from 450ms to 85ms across 14 microservices",
                        ],
                        tags=["Python", "FastAPI", "Docker", "Kafka"],
                    )
                ],
            ),
            ResumeSection(
                id="sec_sk",
                section_type=SectionType.SKILLS,
                display_title="Technical Skills",
                ordering=2,
                entries=[
                    ResumeEntry(
                        id="e_sk",
                        title="Technologies",
                        description="Python, Rust, FastAPI, PostgreSQL, Docker, Kubernetes, Linux",
                    )
                ],
            ),
        ],
    )


def test_docx_rendering_and_structure(printable_resume: ResumeDocument):
    template = ResumeTemplateRegistry.get_template("ats_classic")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_resume.docx")
        DocxRenderer.render_to_file(printable_resume, template, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 1000

        # Open with python-docx and inspect paragraphs
        doc = Document(output_path)
        full_text = "\n".join([p.text for p in doc.paragraphs])
        assert "Alex Mercer" in full_text
        assert "CloudNative Corp" in full_text
        assert "PROFESSIONAL SUMMARY" in full_text.upper()
        assert "WORK EXPERIENCE" in full_text.upper()


def test_pdf_rendering_and_text_extraction(printable_resume: ResumeDocument):
    template = ResumeTemplateRegistry.get_template("ats_classic")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_resume.pdf")
        PdfRenderer.render_to_file(printable_resume, template, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 1000

        # Open with pypdf and verify text is extractable (not flattened/rasterized)
        reader = PdfReader(output_path)
        assert len(reader.pages) >= 1
        page_text = reader.pages[0].extract_text()

        assert "Alex Mercer" in page_text
        assert "WORK EXPERIENCE" in page_text.upper()
        assert "CloudNative Corp" in page_text


def test_document_round_trip_validation(printable_resume: ResumeDocument):
    template = ResumeTemplateRegistry.get_template("ats_classic")

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "verified.pdf")
        PdfRenderer.render_to_file(printable_resume, template, pdf_path)

        # Validate round-trip
        extracted = DocumentRoundTripValidator.extract_text_from_pdf(pdf_path)
        assert extracted["has_extractable_text"] is True

        verification = DocumentRoundTripValidator.verify_document_content(extracted["full_text"], printable_resume)
        assert verification["all_passed"] is True
