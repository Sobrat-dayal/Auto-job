"""Unit tests for deadline intelligence and document requirements (Section 117)."""

import pytest

from app.recruitment.intelligence.extraction.deadlines import extract_application_instructions
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_deadline_parsing():
    job_text = """
    How to Apply:
    Please submit your application by Deadline: April 15, 2026.
    Required documents: Resume and Cover Letter.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    instructions = extract_application_instructions(sections, cleaned)

    assert instructions.deadline_utc is not None
    assert instructions.deadline_utc.year == 2026
    assert instructions.deadline_utc.month == 4
    assert instructions.deadline_utc.day == 15
    assert "Resume / CV" in instructions.required_documents
    assert "Cover Letter" in instructions.required_documents


def test_rolling_review():
    job_text = """
    About the Hiring Process:
    Applications are reviewed on a rolling basis. Early submissions are encouraged.
    Please include your portfolio and resume.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    instructions = extract_application_instructions(sections, cleaned)

    assert instructions.is_rolling is True
    assert "Portfolio / GitHub" in instructions.required_documents
