"""Unit tests for work authorization, visa sponsorship, and clearance requirements (Section 116)."""

import pytest

from app.recruitment.intelligence.extraction.eligibility import extract_eligibility_conditions
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_visa_sponsorship_refused_and_clearance():
    job_text = """
    Eligibility Requirements:
    * Candidates must be legally authorized to work in the United States.
    * No visa sponsorship available now or in the future.
    * Active Secret security clearance required.
    * US citizenship is required due to government contract requirements.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    eligibility = extract_eligibility_conditions(sections, cleaned)

    assert eligibility.work_authorization_required is True
    assert eligibility.visa_sponsorship_refused is True
    assert eligibility.visa_sponsorship_offered is False
    assert "US_CITIZEN_ONLY" in eligibility.citizenship_restrictions
    assert eligibility.security_clearance_required is not None


def test_visa_sponsorship_offered():
    job_text = """
    We welcome international talent! Visa sponsorship is available for qualified applicants.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    eligibility = extract_eligibility_conditions(sections, cleaned)

    assert eligibility.visa_sponsorship_offered is True
    assert eligibility.visa_sponsorship_refused is False


def test_visa_sponsorship_undisclosed():
    job_text = """
    About the Role:
    Software engineer working on web applications.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    eligibility = extract_eligibility_conditions(sections, cleaned)

    # Invariant: Never assume visa sponsorship when unmentioned
    assert eligibility.visa_sponsorship_offered is None
    assert eligibility.visa_sponsorship_refused is None
