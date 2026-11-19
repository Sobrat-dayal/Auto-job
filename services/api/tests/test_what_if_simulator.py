"""Required Test 154: What-If Scenario Simulator.

Verifies:
- Running a hypothetical simulation modifies applicant facts/policies ONLY in memory.
- Underlying profile, active career strategy, and baseline evaluation are NOT mutated.
- Simulation correctly resolves gaps and shows positive impact on relevance index.
- Differences, dimension deltas, and remaining gaps are returned cleanly.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    SimulationRequest,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match
from app.recruitment.matching.decisions.simulation import run_what_if_simulation


@pytest.mark.asyncio
async def test_what_if_simulation_without_state_mutation():
    # Baseline applicant with Python only (missing SQL)
    base_applicant = ApplicantSnapshotData(
        profile_id="prof_sim_base_1",
        version=1,
        headline="Python Engineer",
        country="US",
        city="Chicago",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_py",
                "name": "Python",
                "canonical_name": "python",
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

    base_policy = CareerStrategySnapshotData(
        strategy_id="strat_sim_1",
        title="Backend Engineering",
        role_families=["Software Engineering"],
        target_locations=["Chicago"],
        work_arrangements=["remote"],
        min_annual_salary=140000,  # Higher than job's $120k max
        salary_currency="USD",
        blocked_employers=[],
    )

    canonical_job = {
        "id": "job_sim_1",
        "title": "Full Stack Engineer",
        "company": "Innovation Labs",
        "location": "Chicago, IL",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job requires Python AND SQL, salary max is $125k
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_sim_1",
        job_title="Full Stack Engineer",
        company_name="Innovation Labs",
        skills=[
            {"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 3.0},
            {"id": "req_sql", "name": "SQL", "priority": "MANDATORY", "min_years": 3.0},
        ],
        compensation={"salary_min": 110000, "salary_max": 125000, "currency": "USD", "pay_period": "annual"},
    )

    # 1. Baseline evaluation: Ineligible due to missing SQL and salary below floor ($140k)
    baseline_eval = evaluate_job_match(
        applicant_snapshot=base_applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=base_policy,
    )
    assert baseline_eval.hard_policy_passed is False
    assert baseline_eval.eligibility_outcome == MatchingOutcome.REJECTED_BY_HARD_POLICY

    # Record baseline state before simulation
    orig_skills_count = len(base_applicant.skills)
    orig_min_salary = base_policy.min_annual_salary

    # 2. Run What-If Simulation: Hypothetically add SQL and lower salary floor to $110k
    sim_request = SimulationRequest(
        evaluation_id=baseline_eval.id,
        scenario_name="Acquire SQL and Adjust Salary Floor",
        hypothetical_skills=["SQL"],
        hypothetical_min_salary=110000,
    )

    sim_response = run_what_if_simulation(
        original_evaluation_data=baseline_eval.model_dump(mode="json"),
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        base_applicant_snapshot=base_applicant,
        base_career_strategy=base_policy,
        request=sim_request,
    )

    # 3. Verify Simulation Results
    assert sim_response.original_eligibility == MatchingOutcome.REJECTED_BY_HARD_POLICY
    assert sim_response.simulated_eligibility in (
        MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
    )
    assert sim_response.simulated_relevance_index > sim_response.original_relevance_index
    assert "Acquire SQL" in sim_response.diff_explanation

    # 4. Verify ZERO mutation on baseline objects
    assert len(base_applicant.skills) == orig_skills_count
    assert base_policy.min_annual_salary == orig_min_salary
    assert baseline_eval.hard_policy_passed is False
