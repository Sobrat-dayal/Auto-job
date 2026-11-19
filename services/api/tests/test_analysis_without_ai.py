"""Unit tests for deterministic analysis without AI (offline fallback) (Section 123)."""

import pytest

from app.recruitment.intelligence.contracts import AnalysisStatus, DegreeLevel, PayPeriod, WorkplaceType
from app.recruitment.intelligence.extraction.compensation import extract_compensation_intelligence
from app.recruitment.intelligence.extraction.deadlines import extract_application_instructions
from app.recruitment.intelligence.extraction.education import extract_education_requirements
from app.recruitment.intelligence.extraction.eligibility import extract_eligibility_conditions
from app.recruitment.intelligence.extraction.employment import extract_employment_conditions
from app.recruitment.intelligence.extraction.experience import extract_experience_requirements
from app.recruitment.intelligence.extraction.responsibilities import extract_responsibilities
from app.recruitment.intelligence.extraction.skills import extract_skills_from_sections
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description


def test_deterministic_offline_pipeline():
    raw_html = """
    <h1>Staff Backend Engineer</h1>
    <p>Location: Fully Remote</p>
    <p>Salary: $175,000 - $210,000 per year</p>
    
    <h2>Responsibilities</h2>
    <ul>
        <li>Architect distributed storage systems in Python and Go.</li>
        <li>Lead technical architecture discussions.</li>
    </ul>

    <h2>Minimum Qualifications</h2>
    <ul>
        <li>Bachelor's degree in Computer Science or equivalent practical experience.</li>
        <li>7+ years of experience in distributed systems.</li>
        <li>Hands-on experience with PostgreSQL, Docker, and Kubernetes.</li>
        <li>Must have valid US work authorization.</li>
    </ul>

    <h2>Preferred Qualifications</h2>
    <ul>
        <li>Experience with Terraform and AWS.</li>
    </ul>

    <h2>How to Apply</h2>
    <p>Applications close on Deadline: May 30, 2026. Submit Resume and Cover Letter.</p>
    """

    # 1. Clean HTML
    cleaned = clean_html_description(raw_html)
    assert "<p>" not in cleaned

    # 2. Segment
    sections = segment_job_description(cleaned)
    assert len(sections) >= 3

    # 3. Extract skills deterministically
    skills, atomic_skills = extract_skills_from_sections(sections, cleaned)
    skill_names = [s.name for s in skills]
    assert "Python" in skill_names
    assert "Go" in skill_names
    assert "PostgreSQL" in skill_names
    assert "Docker" in skill_names
    assert "Kubernetes" in skill_names

    # 4. Extract education
    edu, atomic_edu = extract_education_requirements(sections, cleaned)
    assert len(edu) == 1
    assert edu[0].degree_level == DegreeLevel.BACHELOR
    assert edu[0].alternative_experience_years == 4.0

    # 5. Extract experience
    exp, atomic_exp = extract_experience_requirements(sections, cleaned)
    assert len(exp) >= 1
    assert any(e.minimum_years == 7.0 for e in exp)

    # 6. Extract employment
    emp = extract_employment_conditions(sections, cleaned)
    assert emp.workplace_type == WorkplaceType.REMOTE_GLOBAL

    # 7. Extract compensation
    comp = extract_compensation_intelligence(sections, cleaned)
    assert comp.is_disclosed is True
    assert comp.base_min == 175000.0
    assert comp.base_max == 210000.0
    assert comp.pay_period == PayPeriod.ANNUAL

    # 8. Extract eligibility
    elig = extract_eligibility_conditions(sections, cleaned)
    assert elig.work_authorization_required is True

    # 9. Extract deadlines
    deadlines = extract_application_instructions(sections, cleaned)
    assert deadlines.deadline_utc is not None
    assert deadlines.deadline_utc.month == 5
    assert "Resume / CV" in deadlines.required_documents

    # 10. Extract responsibilities
    resp = extract_responsibilities(sections)
    assert len(resp) >= 2
