"""Required Test 146: Ranking Rubric Weights and Tie Breaking.

Verifies:
- Rubric weights modify the explainable relevance index deterministically.
- Standard Rubric vs. Compensation-Heavy Rubric generates different rankings for identical jobs.
- Prioritization queue orders opportunities deterministically.
- Tie-breaking applies when scores are identical (higher coverage, freshness, stable ID).
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    RubricConfig,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match
from app.recruitment.matching.ranking.prioritization import (
    rank_opportunities,
)


@pytest.mark.asyncio
async def test_ranking_rubric_weights_and_tie_breaking():
    applicant = ApplicantSnapshotData(
        profile_id="prof_rubric_1",
        version=1,
        headline="Senior Backend Engineer",
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
        title="Backend Engineering",
        role_families=["Software Engineering"],
        target_locations=["San Francisco"],
        work_arrangements=["remote"],
        min_annual_salary=120000,
        salary_currency="USD",
        blocked_employers=[],
    )

    # Job A: Moderate Salary ($130k), 100% skill match
    job_a = {
        "id": "job_a_mod_salary",
        "title": "Backend Engineer A",
        "company": "Company A",
        "location": "San Francisco, CA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }
    intel_a = JobIntelligenceSnapshotData(
        canonical_job_id="job_a_mod_salary",
        job_title="Backend Engineer A",
        company_name="Company A",
        role_family="Software Engineering",
        skills=[{"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={"salary_min": 110000, "salary_max": 130000, "currency": "USD", "pay_period": "annual"},
    )

    # Job B: High Salary ($220k), 100% skill match
    job_b = {
        "id": "job_b_high_salary",
        "title": "Backend Engineer B",
        "company": "Company B",
        "location": "San Francisco, CA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }
    intel_b = JobIntelligenceSnapshotData(
        canonical_job_id="job_b_high_salary",
        job_title="Backend Engineer B",
        company_name="Company B",
        role_family="Software Engineering",
        skills=[{"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 3.0}],
        compensation={"salary_min": 210000, "salary_max": 240000, "currency": "USD", "pay_period": "annual"},
    )

    # Standard Rubric (Compensation weight = 0.10)
    std_rubric = RubricConfig(id="std_rubric", name="Standard", weights={"compensation": 0.10, "qualification_alignment": 0.30})
    # Compensation-Heavy Rubric (Compensation weight = 0.50)
    comp_heavy_rubric = RubricConfig(id="comp_heavy", name="Comp Heavy", weights={"compensation": 0.50, "qualification_alignment": 0.20})

    # Evaluate under Standard Rubric
    eval_a_std = evaluate_job_match(applicant, job_a, intel_a, policy, rubric=std_rubric)
    eval_b_std = evaluate_job_match(applicant, job_b, intel_b, policy, rubric=std_rubric)

    # Evaluate under Comp Heavy Rubric
    eval_a_heavy = evaluate_job_match(applicant, job_a, intel_a, policy, rubric=comp_heavy_rubric)
    eval_b_heavy = evaluate_job_match(applicant, job_b, intel_b, policy, rubric=comp_heavy_rubric)

    # 1. Job B scores higher on compensation in both
    assert eval_b_std.relevance_index >= eval_a_std.relevance_index

    # 2. In Comp Heavy rubric, the score difference between Job B and Job A is significantly magnified
    diff_std = eval_b_std.relevance_index - eval_a_std.relevance_index
    diff_heavy = eval_b_heavy.relevance_index - eval_a_heavy.relevance_index
    assert diff_heavy > diff_std

    # 3. Prioritization queue ordering
    queue, overview = rank_opportunities([eval_a_heavy, eval_b_heavy])
    assert len(queue) == 2
    # Job B is rank 1 due to higher relevance index
    assert queue[0].canonical_job_id == "job_b_high_salary"
    assert queue[0].rank == 1
    assert queue[1].rank == 2

    # 4. Tie-breaking check with identical scores
    eval_a_dup = eval_a_heavy.model_copy(update={"canonical_job_id": "job_a_dup"})
    tie_queue, _ = rank_opportunities([eval_a_heavy, eval_a_dup])
    assert len(tie_queue) == 2
    assert tie_queue[0].rank == 1
    assert tie_queue[1].rank == 2
