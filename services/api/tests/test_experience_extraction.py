"""Unit tests for experience requirements and duration extraction (Section 113)."""

import pytest

from app.recruitment.intelligence.extraction.experience import extract_experience_requirements
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_experience_range_extraction():
    job_text = """
    Minimum Qualifications:
    * 5+ years of professional software development experience.
    * 3-5 years of backend engineering experience.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    exp_reqs, atomic = extract_experience_requirements(sections, cleaned)

    assert len(exp_reqs) >= 1
    min_years_list = [e.minimum_years for e in exp_reqs]
    assert 5.0 in min_years_list or 3.0 in min_years_list

    # Check evidence traceability
    for e in exp_reqs:
        assert len(e.evidence) > 0
        assert e.evidence[0].verified_in_source is True


def test_domain_specific_experience():
    job_text = """
    Required Qualifications:
    * At least 4 years of experience in distributed systems and backend engineering.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    exp_reqs, atomic = extract_experience_requirements(sections, cleaned)

    assert len(exp_reqs) == 1
    assert exp_reqs[0].minimum_years == 4.0
    assert "Backend Development" in exp_reqs[0].domain_categories or "Distributed Systems" in exp_reqs[0].domain_categories
