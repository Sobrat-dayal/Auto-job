"""Unit tests for remote eligibility and employment conditions (Section 115)."""

import pytest

from app.recruitment.intelligence.contracts import WorkplaceType
from app.recruitment.intelligence.extraction.employment import extract_employment_conditions
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_remote_us_only():
    job_text = """
    About the Role:
    This is a 100% remote position (US only). Candidates must reside in the United States.
    Up to 15% travel required for annual company onsites.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    emp = extract_employment_conditions(sections, cleaned)

    assert emp.workplace_type in (WorkplaceType.REMOTE_COUNTRY_ONLY, WorkplaceType.REMOTE_GLOBAL)
    assert "US" in emp.allowed_countries or emp.workplace_type == WorkplaceType.REMOTE_GLOBAL
    assert emp.travel_percentage == 15.0


def test_hybrid_office_days():
    job_text = """
    Work Arrangement:
    Hybrid role with 2 days per week in our Seattle office.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    emp = extract_employment_conditions(sections, cleaned)

    assert emp.workplace_type == WorkplaceType.HYBRID
    assert emp.office_days_per_week == 2


def test_onsite_workplace():
    job_text = """
    Location:
    On-site in New York City. In-person collaboration required Monday through Friday.
    No travel required.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    emp = extract_employment_conditions(sections, cleaned)

    assert emp.workplace_type == WorkplaceType.ONSITE
    assert emp.travel_percentage == 0.0
