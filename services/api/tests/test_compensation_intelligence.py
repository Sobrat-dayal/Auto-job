"""Unit tests for compensation intelligence, ranges, currencies, and zero synthetic guessing (Section 114)."""

import pytest

from app.recruitment.intelligence.contracts import PayPeriod
from app.recruitment.intelligence.extraction.compensation import extract_compensation_intelligence
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_compensation_range_annual_em_dash():
    job_text = """
    Compensation:
    Base Salary: $140,000—$180,000 / year.
    Eligible for a 15% annual bonus and equity grant (RSUs).
    Benefits: 401(k) matching, health insurance, and unlimited PTO.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    comp = extract_compensation_intelligence(sections, cleaned)

    assert comp.is_disclosed is True
    assert comp.base_min == 140000.0
    assert comp.base_max == 180000.0
    assert comp.currency == "USD"
    assert comp.pay_period == PayPeriod.ANNUAL
    assert comp.has_bonus is True
    assert comp.has_equity is True
    assert "401(k) / Retirement" in comp.benefits
    assert "Health Insurance" in comp.benefits
    assert "Paid Time Off (PTO)" in comp.benefits


def test_compensation_hourly_rate():
    job_text = """
    Rate: $65 - $85 / hour depending on experience.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    comp = extract_compensation_intelligence(sections, cleaned)

    assert comp.is_disclosed is True
    assert comp.base_min == 65.0
    assert comp.base_max == 85.0
    assert comp.pay_period == PayPeriod.HOURLY


def test_compensation_zero_synthetic_guessing():
    # Job text with NO mention of salary
    job_text = """
    About the Role:
    We are seeking a talented Senior Cloud Architect.

    Requirements:
    * 5+ years of AWS and Terraform experience.
    """
    cleaned = clean_html_description(job_text)
    sections = segment_job_description(cleaned)
    comp = extract_compensation_intelligence(sections, cleaned)

    # Invariant: Never invent salary numbers when undisclosed!
    assert comp.is_disclosed is False
    assert comp.base_min is None
    assert comp.base_max is None
