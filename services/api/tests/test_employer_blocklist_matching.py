"""Required Test 143: Blocked Employer Hard Constraint.

Verifies:
- Candidate's active Career Strategy contains an employer blocklist ["ToxicCorp", "EvilCorp"].
- Canonical job originates from "ToxicCorp".
- Engine immediately enforces hard restriction (hard_policy_passed=False).
- Final outcome is REJECTED_BY_HARD_POLICY (ApplicationReadiness: HARD_POLICY_EXCLUDED).
- Precedence: 100% skill match, top salary, and perfect location are completely ignored.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_blocked_employer_hard_rejection():
    applicant = ApplicantSnapshotData(
        profile_id="prof_blocklist_1",
        version=1,
        headline="Senior Architect",
        country="US",
        city="San Francisco",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_py",
                "name": "Python",
                "canonical_name": "python",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 8.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[],
        projects=[],
        certifications=[],
    )

    # Job from blocked employer
    canonical_job = {
        "id": "job_toxic_1",
        "title": "Principal Architect",
        "company": "ToxicCorp Inc",
        "location": "San Francisco, CA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_toxic_1",
        job_title="Principal Architect",
        company_name="ToxicCorp Inc",
        role_family="Software Engineering",
        skills=[{"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 5.0}],
        compensation={
            "salary_min": 250000,
            "salary_max": 300000,
            "currency": "USD",
            "pay_period": "annual",
        },
    )

    # Career Strategy with ToxicCorp on blocked list
    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Architecture",
        role_families=["Software Engineering"],
        target_locations=["San Francisco"],
        work_arrangements=["remote"],
        min_annual_salary=200000,
        salary_currency="USD",
        blocked_employers=["ToxicCorp", "EvilCorp LLC"],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Hard policy failed
    assert evaluation.hard_policy_passed is False
    assert "blocked" in (evaluation.hard_policy_reason or "").lower()
    assert "toxiccorp" in (evaluation.hard_policy_reason or "").lower()

    # 2. Outcome is REJECTED_BY_HARD_POLICY
    assert evaluation.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY
    assert evaluation.application_readiness == ApplicationReadiness.HARD_POLICY_EXCLUDED

    # 3. Soft relevance index does not bypass blocklist
    assert evaluation.eligibility_outcome != MatchingOutcome.ELIGIBLE_AND_ALIGNED
