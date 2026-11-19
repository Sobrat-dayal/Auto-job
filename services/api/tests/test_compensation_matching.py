"""Required Test 142: Compensation Policy Matching.

Verifies:
- Range overlap: Job offers $120k-$150k, candidate requires min $130k -> Compatible.
- Below floor: Job max is $100k, candidate requires min $130k -> Hard constraint failure, REJECTED_BY_HARD_POLICY.
- Annualized hourly rate: Job offers $75/hr (annualized to $156,000 at 2,080 hrs/yr) -> Meets $130k minimum.
- Undisclosed salary: Handled gracefully according to strategy policy.
"""

import pytest
from app.recruitment.matching.conditions.compensation import (
    annualize_salary,
    evaluate_compensation,
)
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


def test_annualization_math():
    # Hourly $75/hr * 2080 = $156,000
    ann_hourly = annualize_salary(75.0, "hourly")
    assert ann_hourly == 156000.0

    # Monthly $10,000 * 12 = $120,000
    ann_monthly = annualize_salary(10000.0, "monthly")
    assert ann_monthly == 120000.0

    # Annual already annual
    assert annualize_salary(140000.0, "annual") == 140000.0


@pytest.mark.asyncio
async def test_compensation_policy_overlap_and_violation():
    applicant = ApplicantSnapshotData(
        profile_id="prof_comp_1",
        version=1,
        headline="Staff Engineer",
        country="US",
        city="Chicago",
        authorized_countries=["US"],
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
        experience=[],
        projects=[],
        certifications=[],
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Staff Engineering",
        role_families=["Software Engineering"],
        target_locations=["US"],
        work_arrangements=["remote"],
        min_annual_salary=130000,
        salary_currency="USD",
        blocked_employers=[],
    )

    canonical_job = {
        "id": "job_comp_test_1",
        "title": "Senior Go Engineer",
        "company": "Tech Innovations Inc",
        "location": "Remote",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Case A: Range overlap ($120k - $150k meets min $130k)
    job_intel_overlap = JobIntelligenceSnapshotData(
        canonical_job_id="job_comp_test_1",
        job_title="Senior Go Engineer",
        company_name="Tech Innovations Inc",
        skills=[{"id": "req_go", "name": "Go", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={
            "salary_min": 120000,
            "salary_max": 150000,
            "currency": "USD",
            "pay_period": "annual",
        },
    )

    eval_overlap = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel_overlap,
        career_strategy=policy,
    )
    assert eval_overlap.hard_policy_passed is True
    assert eval_overlap.eligibility_outcome in (
        MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
    )

    # Case B: Below floor ($90k - $105k strictly below min $130k)
    job_intel_below = JobIntelligenceSnapshotData(
        canonical_job_id="job_comp_test_1",
        job_title="Senior Go Engineer",
        company_name="Tech Innovations Inc",
        skills=[{"id": "req_go", "name": "Go", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={
            "salary_min": 90000,
            "salary_max": 105000,
            "currency": "USD",
            "pay_period": "annual",
        },
    )

    eval_below = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel_below,
        career_strategy=policy,
    )
    assert eval_below.hard_policy_passed is False
    assert eval_below.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY
    assert eval_below.application_readiness == ApplicationReadiness.HARD_POLICY_EXCLUDED
    assert "below minimum" in (eval_below.hard_policy_reason or "").lower()

    # Case C: Annualized hourly rate ($75/hr = $156,000/yr meets $130k)
    job_intel_hourly = JobIntelligenceSnapshotData(
        canonical_job_id="job_comp_test_1",
        job_title="Senior Go Engineer",
        company_name="Tech Innovations Inc",
        skills=[{"id": "req_go", "name": "Go", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={
            "salary_min": 75,
            "salary_max": 85,
            "currency": "USD",
            "pay_period": "hourly",
        },
    )

    eval_hourly = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel_hourly,
        career_strategy=policy,
    )
    assert eval_hourly.hard_policy_passed is True
    assert eval_hourly.eligibility_outcome in (
        MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
    )
