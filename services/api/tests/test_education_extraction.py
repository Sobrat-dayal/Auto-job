"""Unit tests for education requirement extraction (Section 112)."""

import pytest

from app.recruitment.intelligence.contracts import DegreeLevel
from app.recruitment.intelligence.extraction.education import extract_education_requirements
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_bachelor_degree_with_fields_and_equivalency():
    job_text = """
    Minimum Qualifications:
    * Bachelor's degree in Computer Science, Software Engineering, or related technical field, or equivalent practical experience.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    edu_reqs, atomic = extract_education_requirements(sections, cleaned)

    assert len(edu_reqs) == 1
    req = edu_reqs[0]
    assert req.degree_level == DegreeLevel.BACHELOR
    assert "Computer Science" in req.fields_of_study
    assert "Software Engineering" in req.fields_of_study
    assert req.alternative_experience_years == 4.0
    assert req.is_mandatory is True
    assert len(req.evidence) == 1
    assert req.evidence[0].verified_in_source is True


def test_master_or_phd_extraction():
    job_text = """
    Preferred Qualifications:
    * Master's degree or Ph.D. in Computer Science, Mathematics, or Statistics.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    edu_reqs, atomic = extract_education_requirements(sections, cleaned)

    levels = [e.degree_level for e in edu_reqs]
    assert DegreeLevel.MASTER in levels or DegreeLevel.DOCTORATE in levels
    for e in edu_reqs:
        assert e.is_mandatory is False
