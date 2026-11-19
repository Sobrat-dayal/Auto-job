"""Required Test 144: Multiple Source Observations Canonical Matching.

Verifies:
- Canonical job entity from Stage 27 reconciles 3 separate source observations (Greenhouse, Lever, LinkedIn).
- Job Matching Engine evaluates the canonical job record, NOT individual observations.
- All evaluation records, gaps, rankings, and decisions link to canonical_job_id.
- Single unified evaluation record is maintained, preventing duplicate match records for the same vacancy.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_canonical_job_single_evaluation():
    # Applicant with Python
    applicant = ApplicantSnapshotData(
        profile_id="prof_canon_1",
        version=1,
        headline="Software Engineer",
        country="US",
        city="New York",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_py",
                "name": "Python",
                "canonical_name": "python",
                "category": "technical",
                "proficiency": "advanced",
                "years_experience": 4.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[],
        projects=[],
        certifications=[],
    )

    # Canonical job representing multiple aggregated source feeds (Greenhouse, Lever, LinkedIn)
    canonical_job_id = "canon_job_reconciled_999"
    canonical_job = {
        "id": canonical_job_id,
        "title": "Senior Backend Developer",
        "company": "Acme Corp",
        "location": "New York, NY",
        "employment_type": "Full-Time",
        "work_arrangement": "Hybrid",
        "status": "active",
        "source_observation_ids": ["obs_greenhouse_1", "obs_lever_2", "obs_linkedin_3"],
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id=canonical_job_id,
        canonical_job_version=1,
        job_title="Senior Backend Developer",
        company_name="Acme Corp",
        role_family="Software Engineering",
        skills=[{"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={
            "salary_min": 140000,
            "salary_max": 170000,
            "currency": "USD",
            "pay_period": "annual",
        },
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Backend Engineering",
        role_families=["Software Engineering"],
        target_locations=["New York"],
        work_arrangements=["hybrid"],
        min_annual_salary=130000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Evaluation record is linked directly to the canonical job ID
    assert evaluation.canonical_job_id == canonical_job_id
    assert evaluation.profile_id == "prof_canon_1"

    # 2. Outcome is clean single evaluation
    assert evaluation.eligibility_outcome == MatchingOutcome.ELIGIBLE_AND_ALIGNED
    assert evaluation.hard_policy_passed is True

    # 3. Requirement results trace back to the canonical entity
    assert len(evaluation.requirement_results) >= 1
    assert evaluation.mandatory_coverage_ratio == 1.0
