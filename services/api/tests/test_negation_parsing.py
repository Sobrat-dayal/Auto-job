"""Unit tests for negation parsing and exclusion logic (Section 111)."""

import pytest

from app.recruitment.intelligence.contracts import DegreeLevel
from app.recruitment.intelligence.extraction.education import extract_education_requirements
from app.recruitment.intelligence.extraction.eligibility import extract_eligibility_conditions
from app.recruitment.intelligence.extraction.experience import extract_experience_requirements
from app.recruitment.intelligence.extraction.requirement_logic import is_negated_phrase, is_skill_negated
from app.recruitment.intelligence.extraction.skills import extract_skills_from_sections
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_skill_negation_scoped():
    text = "Prior AWS experience not required for this entry position."
    assert is_skill_negated(text, "AWS") is True
    assert is_negated_phrase(text) is True

    # When extracting skills, AWS should be excluded or not marked mandatory
    job_text = """
    Minimum Qualifications:
    * Strong Python programming skills.
    * Prior AWS experience not required.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    skills, atomic_reqs = extract_skills_from_sections(sections, cleaned)

    skill_names = [s.name for s in skills]
    assert "Python" in skill_names
    assert "AWS" not in skill_names


def test_no_prior_experience_required():
    job_text = """
    Requirements:
    * No prior professional experience required.
    * Passion for learning technology.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    exp_reqs, atomic_exp = extract_experience_requirements(sections, cleaned)

    assert len(exp_reqs) == 1
    assert exp_reqs[0].minimum_years == 0.0
    assert exp_reqs[0].is_mandatory is False


def test_degree_not_required():
    job_text = """
    Qualifications:
    * High school diploma or college degree not required.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    edu_reqs, atomic_edu = extract_education_requirements(sections, cleaned)

    assert len(edu_reqs) == 1
    assert edu_reqs[0].degree_level == DegreeLevel.NOT_REQUIRED
    assert edu_reqs[0].is_mandatory is False


def test_sponsorship_unavailable():
    job_text = """
    Employment Terms:
    * Visa sponsorship is unavailable for this role.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    eligibility = extract_eligibility_conditions(sections, cleaned)

    assert eligibility.visa_sponsorship_refused is True
    assert eligibility.visa_sponsorship_offered is False
