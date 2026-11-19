"""Required Test 140: Visa Sponsorship Conflict Hard Constraint.

Verifies:
- Candidate profile explicitly declares visa sponsorship required (requires_sponsorship=True).
- Job intelligence confirms employer does not sponsor visas (sponsorship_refused=True or sponsorship_offered=False).
- Hard constraint failure is triggered (hard_policy_passed=False).
- Final outcome is REJECTED_BY_HARD_POLICY (ApplicationReadiness: HARD_POLICY_EXCLUDED).
- This rejection cannot be overridden even if candidate has a 100% perfect skill and experience match.
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
async def test_visa_sponsorship_conflict_hard_rejection():
    # Applicant who requires visa sponsorship
    applicant = ApplicantSnapshotData(
        profile_id="prof_visa_needed_1",
        version=1,
        headline="Principal Distributed Systems Engineer",
        country="IN",
        city="Bengaluru",
        authorized_countries=["IN"],
        requires_sponsorship=True,  # Explicitly requires sponsorship
        skills=[
            {
                "id": "skl_rust",
                "name": "Rust",
                "canonical_name": "rust",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 7.0,
                "is_verified": True,
            }
        ],
        education=[
            {
                "id": "edu_1",
                "degree": "Master of Science",
                "field_of_study": "Computer Science",
                "academic_status": "completed",
            }
        ],
        experience=[
            {
                "id": "exp_1",
                "employer": "Global Tech",
                "job_title": "Staff Engineer",
                "employment_type": "full_time",
                "start_date": "2018-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Rust"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_us_no_sponsor_1",
        "title": "Principal Systems Engineer",
        "company": "US Defense Contractor LLC",
        "location": "Dallas, TX",
        "employment_type": "Full-Time",
        "work_arrangement": "Onsite",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job states: No visa sponsorship offered under any circumstance
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_us_no_sponsor_1",
        job_title="Principal Systems Engineer",
        company_name="US Defense Contractor LLC",
        role_family="Software Engineering",
        skills=[
            {"id": "req_rust", "name": "Rust", "priority": "MANDATORY", "min_years": 5.0},
        ],
        experience=[
            {"id": "req_exp", "min_years": 5.0, "domain": "Software Engineering"}
        ],
        employment_conditions={
            "workplace_type": "onsite",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 180000,
            "salary_max": 240000,
            "currency": "USD",
            "pay_period": "annual",
        },
        eligibility={
            "work_authorization_required": True,
            "citizenship_restrictions": ["US"],
            "sponsorship_offered": False,
            "sponsorship_refused": True,  # Strictly refuses sponsorship
        },
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Principal Engineering",
        role_families=["Software Engineering"],
        target_locations=["US"],
        work_arrangements=["onsite"],
        min_annual_salary=170000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Hard policy constraint failed
    assert evaluation.hard_policy_passed is False
    assert "sponsorship" in (evaluation.hard_policy_reason or "").lower()

    # 2. Final outcome is REJECTED_BY_HARD_POLICY
    assert evaluation.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY
    assert evaluation.application_readiness == ApplicationReadiness.HARD_POLICY_EXCLUDED

    # 3. Sponsorship condition detail reflects conflict
    assert evaluation.eligibility_detail.hard_policy_passed is False
    assert (
        evaluation.eligibility_detail.sponsorship_status
        == RequirementMatchCategory.KNOWN_NOT_SATISFIED.value
    )

    # 4. Mandatory skills were technically 100% matched, but hard policy overrode them
    rust_req = next((r for r in evaluation.requirement_results if r.name == "Rust"), None)
    assert rust_req is not None
    assert rust_req.is_satisfied is True  # Proves skills did not prevent match; hard constraint did
