"""Required Test 141: Remote Country Restrictions.

Verifies:
- Candidate resides in India (IN) and is not authorized in the US.
- Job is advertised as "Remote", but restricted strictly to USA residents (allowed_countries=["US"]).
- Engine identifies geographic jurisdiction incompatibility for remote employment.
- Hard constraint fails (hard_policy_passed=False).
- Final outcome is REJECTED_BY_HARD_POLICY.
- When applicant is in US, remote compatibility passes directly.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_remote_country_restriction_rejection():
    # Applicant based in India
    applicant_india = ApplicantSnapshotData(
        profile_id="prof_in_1",
        version=1,
        headline="Senior Backend Engineer",
        country="IN",
        city="Hyderabad",
        authorized_countries=["IN"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_go",
                "name": "Go",
                "canonical_name": "go",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 5.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[
            {
                "id": "exp_1",
                "employer": "Tech India",
                "job_title": "Backend Lead",
                "employment_type": "full_time",
                "start_date": "2020-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Go"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_us_remote_only_1",
        "title": "Remote Backend Engineer",
        "company": "Silicon Valley Cloud Inc",
        "location": "Remote - US Only",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job is Remote, but explicitly limited to US
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_us_remote_only_1",
        job_title="Remote Backend Engineer",
        company_name="Silicon Valley Cloud Inc",
        role_family="Software Engineering",
        skills=[
            {"id": "req_go", "name": "Go", "priority": "MANDATORY", "min_years": 4.0},
        ],
        employment_conditions={
            "workplace_type": "remote",
            "allowed_countries": ["US"],
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 140000,
            "salary_max": 170000,
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
        title="Remote Backend",
        role_families=["Software Engineering"],
        target_locations=["Remote"],
        work_arrangements=["remote"],
        min_annual_salary=120000,
        salary_currency="USD",
        blocked_employers=[],
    )

    # 1. Candidate in India should be REJECTED_BY_HARD_POLICY
    eval_india = evaluate_job_match(
        applicant_snapshot=applicant_india,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )
    assert eval_india.hard_policy_passed is False
    assert eval_india.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY
    assert eval_india.application_readiness == ApplicationReadiness.HARD_POLICY_EXCLUDED

    # 2. Candidate in US should pass remote restriction
    applicant_us = ApplicantSnapshotData(
        profile_id="prof_us_1",
        version=1,
        headline="Senior Backend Engineer",
        country="US",
        city="Austin",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=applicant_india.skills,
        education=[],
        experience=applicant_india.experience,
        projects=[],
        certifications=[],
    )

    eval_us = evaluate_job_match(
        applicant_snapshot=applicant_us,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )
    assert eval_us.hard_policy_passed is True
    assert eval_us.eligibility_outcome in (
        MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
    )
    assert eval_us.application_readiness == ApplicationReadiness.READY_FOR_PREPARATION
