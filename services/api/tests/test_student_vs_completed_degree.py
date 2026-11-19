"""Required Test 135: Currently Enrolled Student vs. Completed Degree.

Verifies:
- Candidate profile confirms currently enrolled student status (academic_status="currently_enrolled").
- Job mandates completed Bachelor's degree upon hiring.
- Engine does NOT treat enrolled student as having completed the degree.
- Requirement is evaluated as KNOWN_NOT_SATISFIED.
- Blocking gap is recorded.
- Final outcome is KNOWN_REQUIREMENT_NOT_MET (Ineligible).
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
    GapSeverity,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_enrolled_student_vs_completed_degree():
    # Currently enrolled student (graduating in 2028)
    applicant = ApplicantSnapshotData(
        profile_id="prof_student_1",
        version=1,
        headline="Computer Science Undergraduate",
        country="US",
        city="Pittsburgh",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_cpp",
                "name": "C++",
                "canonical_name": "c++",
                "category": "technical",
                "proficiency": "advanced",
                "years_experience": 2.0,
                "is_verified": True,
            }
        ],
        education=[
            {
                "id": "edu_enrolled_1",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "academic_status": "currently_enrolled",
                "expected_completion": "2028-05-15",
            }
        ],
        experience=[],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_completed_deg_req_1",
        "title": "Software Engineer I",
        "company": "Enterprise Systems",
        "location": "Pittsburgh, PA",
        "employment_type": "Full-Time",
        "work_arrangement": "Onsite",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job strictly mandates completed Bachelor's degree (no student waiver)
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_completed_deg_req_1",
        job_title="Software Engineer I",
        company_name="Enterprise Systems",
        role_family="Software Engineering",
        skills=[
            {"id": "req_cpp", "name": "C++", "priority": "MANDATORY", "min_years": 1.0},
        ],
        education=[
            {
                "id": "req_edu_bachelor",
                "degree_level": "bachelor",
                "field_of_study": "Computer Science",
                "status": "completed",
                "practical_experience_waiver": False,
            }
        ],
        employment_conditions={
            "workplace_type": "onsite",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 85000,
            "salary_max": 105000,
            "currency": "USD",
            "pay_period": "annual",
        },
        eligibility={
            "work_authorization_required": True,
            "citizenship_restrictions": ["US"],
            "sponsorship_offered": False,
            "sponsorship_refused": False,
        },
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Entry Level Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Pittsburgh"],
        work_arrangements=["onsite"],
        min_annual_salary=80000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Education detail explicitly identifies enrolled student mismatch
    assert evaluation.education_detail is not None
    assert (
        evaluation.education_detail.match_status
        == RequirementMatchCategory.KNOWN_NOT_SATISFIED
    )
    assert evaluation.education_detail.status_compatible is False
    assert "currently enrolled" in evaluation.education_detail.explanation.lower()

    # 2. Education requirement result is NOT satisfied
    edu_req_res = next(
        (r for r in evaluation.requirement_results if r.requirement_id == "req_edu_bachelor"),
        None,
    )
    assert edu_req_res is not None
    assert edu_req_res.is_satisfied is False
    assert edu_req_res.match_category == RequirementMatchCategory.KNOWN_NOT_SATISFIED

    # 3. Overall outcome is ineligibility due to known unmet mandatory requirement
    assert evaluation.eligibility_outcome == MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET
    assert evaluation.application_readiness == ApplicationReadiness.INELIGIBLE

    # 4. Blocking gap recorded for education
    assert any(g.severity == GapSeverity.BLOCKING for g in evaluation.gaps)
