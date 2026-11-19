"""Unit tests for requirement classification: Mandatory vs Preferred vs Informational (Section 109)."""

import pytest

from app.recruitment.intelligence.contracts import RequirementCategory
from app.recruitment.intelligence.extraction.skills import extract_skills_from_sections
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_mandatory_vs_preferred_classification():
    job_text = """
    About the Role:
    We are looking for a Senior Backend Engineer to join our core platform team.

    Responsibilities:
    * Build scalable microservices using Python and Docker.
    * Collaborate with frontend engineers using React.

    Minimum Qualifications:
    * 5+ years of experience with Python.
    * 3+ years of experience with PostgreSQL.
    * Strong experience with AWS.

    Preferred Qualifications:
    * Experience with Kubernetes and Terraform.
    * Familiarity with Go or Rust.
    """

    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    skills, atomic_reqs = extract_skills_from_sections(sections, cleaned)

    req_map = {r.name: r.category for r in atomic_reqs}

    # Minimum qualifications must be MANDATORY
    assert req_map.get("Python") == RequirementCategory.MANDATORY
    assert req_map.get("PostgreSQL") == RequirementCategory.MANDATORY
    assert req_map.get("AWS") == RequirementCategory.MANDATORY

    # Preferred qualifications must be PREFERRED and never promoted to Mandatory
    assert req_map.get("Kubernetes") == RequirementCategory.PREFERRED
    assert req_map.get("Terraform") == RequirementCategory.PREFERRED

    # Verify no preferred requirement is marked mandatory
    preferred_items = [r for r in atomic_reqs if r.category == RequirementCategory.PREFERRED]
    assert len(preferred_items) >= 2
    for item in preferred_items:
        assert item.category != RequirementCategory.MANDATORY


def test_responsibility_skills_not_promoted_to_mandatory():
    job_text = """
    About the Role:
    Software Engineer role.

    Responsibilities:
    * You will touch React and Next.js occasionally.

    Required Qualifications:
    * Python proficiency is required.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    skills, atomic_reqs = extract_skills_from_sections(sections, cleaned)

    req_map = {r.name: r.category for r in atomic_reqs}
    assert req_map.get("Python") == RequirementCategory.MANDATORY
    # React mentioned only in Responsibilities should not be Mandatory
    assert req_map.get("React") != RequirementCategory.MANDATORY
