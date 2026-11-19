"""Required Test 137: Overlapping Employment Duration Calculation.

Verifies:
- Candidate held two concurrent full-time employment roles spanning the exact same calendar period (2021-01-01 to 2022-12-31, 24 calendar months).
- Experience calculator merges overlapping intervals [start, end].
- Resulting professional experience tenure is 2.0 years, NOT double-counted as 4.0 years.
- has_overlapping_roles flag is set to True.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match
from app.recruitment.matching.qualifications.experience import (
    calculate_non_overlapping_duration,
)


def test_calculate_non_overlapping_duration_unit():
    # Two overlapping roles across 2021 and 2022 (24 calendar months = ~2.0 years)
    roles = [
        {
            "id": "exp_role_a",
            "employer": "Company Alpha",
            "employment_type": "full_time",
            "start_date": "2021-01-01",
            "end_date": "2022-12-31",
        },
        {
            "id": "exp_role_b",
            "employer": "Company Beta",
            "employment_type": "full_time",
            "start_date": "2021-06-01",
            "end_date": "2022-12-31",
        },
    ]

    years, months, has_overlap = calculate_non_overlapping_duration(roles)

    # 1. Overlapping flag is detected
    assert has_overlap is True

    # 2. Months is 24 months, years is ~2.0, NOT 3.5 or 4.0
    assert 23 <= months <= 25
    assert 1.95 <= years <= 2.05


@pytest.mark.asyncio
async def test_overlapping_employment_in_job_match_evaluation():
    # Candidate with two overlapping roles in 2021-2022
    applicant = ApplicantSnapshotData(
        profile_id="prof_overlap_1",
        version=1,
        headline="Full Stack Engineer",
        country="US",
        city="Chicago",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_ts",
                "name": "TypeScript",
                "canonical_name": "typescript",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 2.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[
            {
                "id": "exp_a",
                "employer": "Alpha Tech",
                "job_title": "Software Engineer",
                "employment_type": "full_time",
                "start_date": "2021-01-01",
                "end_date": "2022-12-31",
                "technologies": ["TypeScript"],
            },
            {
                "id": "exp_b",
                "employer": "Beta Solutions",
                "job_title": "Contract Engineer",
                "employment_type": "full_time",
                "start_date": "2021-06-01",
                "end_date": "2022-12-31",
                "technologies": ["TypeScript"],
            },
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_mid_ts_1",
        "title": "TypeScript Engineer",
        "company": "NextGen Software",
        "location": "Chicago, IL",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job requiring 3+ years experience
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_mid_ts_1",
        job_title="TypeScript Engineer",
        company_name="NextGen Software",
        role_family="Software Engineering",
        skills=[
            {"id": "req_ts", "name": "TypeScript", "priority": "MANDATORY", "min_years": 1.0},
        ],
        experience=[
            {"id": "req_exp", "min_years": 3.0, "domain": "Software Engineering"}
        ],
        employment_conditions={
            "workplace_type": "remote",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 100000,
            "salary_max": 130000,
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
        title="TypeScript Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Chicago"],
        work_arrangements=["remote"],
        min_annual_salary=95000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # Verification:
    # 1. Experience detail reflects non-overlapping calculation: ~2.0 years
    assert evaluation.experience_detail is not None
    assert evaluation.experience_detail.has_overlapping_roles is True
    assert 1.95 <= evaluation.experience_detail.calculated_professional_years <= 2.05

    # 2. Because 2.0 < 3.0, the mandatory requirement is NOT satisfied (preventing false pass from 4.0 double count)
    assert evaluation.experience_detail.calculated_professional_years < 3.0
    exp_req = next(
        (r for r in evaluation.requirement_results if r.requirement_id == "req_exp"),
        None,
    )
    assert exp_req is not None
    assert exp_req.is_satisfied is False
