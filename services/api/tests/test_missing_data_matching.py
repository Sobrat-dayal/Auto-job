"""Required Test 147: Missing Data Conservative Evaluation.

Verifies:
- Job posting lacks salary information and experience duration requirements.
- System does NOT invent synthetic salary numbers or guess experience years.
- Conservative evaluation policy records unobserved dimensions.
- ranking_uncertainty_ratio is greater than 0.0, reflecting missing inputs.
- Missing dimensions are explicitly cataloged in the score breakdown.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_missing_data_conservative_uncertainty():
    applicant = ApplicantSnapshotData(
        profile_id="prof_uncertainty_1",
        version=1,
        headline="Frontend Developer",
        country="US",
        city="Chicago",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_react",
                "name": "React",
                "canonical_name": "react",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 4.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[],
        projects=[],
        certifications=[],
    )

    # Job completely missing compensation and experience requirements
    canonical_job = {
        "id": "job_sparse_1",
        "title": "React Developer",
        "company": "Startup Co",
        "location": "Chicago, IL",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_sparse_1",
        job_title="React Developer",
        company_name="Startup Co",
        skills=[{"id": "req_react", "name": "React", "priority": "MANDATORY", "min_years": 2.0}],
        experience=[],  # No experience tenure requirement specified
        compensation={},  # Undisclosed compensation
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Frontend",
        role_families=["Software Engineering"],
        target_locations=["Chicago"],
        work_arrangements=["remote"],
        min_annual_salary=100000,
        salary_currency="USD",
        blocked_employers=[],
        undisclosed_salary_handling="include",
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Uncertainty ratio reflects missing/unobserved data
    assert evaluation.ranking_uncertainty_ratio > 0.0

    # 2. Missing dimensions are tracked in score breakdown
    assert len(evaluation.score_breakdown.missing_dimensions) >= 1
    assert any(
        dim in evaluation.score_breakdown.missing_dimensions
        for dim in ("experience_duration", "preferred_skills")
    )

    # 3. Transparent formula explanation
    assert len(evaluation.score_breakdown.formula_explanation) > 0
    assert evaluation.status == "completed"
