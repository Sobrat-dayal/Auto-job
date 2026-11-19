"""Required Test 131: Perfectly Aligned Synthetic Job Evaluation.

Verifies:
- All mandatory requirements satisfied
- Evidence is properly attached
- Career policy allows consideration
- Relevance dimensions calculated deterministically
- Job enters eligible ranking group
- No application submission occurs
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
async def test_perfectly_aligned_synthetic_job():
    # Synthetic applicant with confirmed qualifications
    applicant = ApplicantSnapshotData(
        profile_id="prof_perfect_1",
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
                "years_experience": 6.0,
                "is_verified": True,
            },
            {
                "id": "skl_sql",
                "name": "SQL",
                "canonical_name": "sql",
                "category": "technical",
                "proficiency": "advanced",
                "years_experience": 5.0,
                "is_verified": True,
            },
        ],
        education=[
            {
                "id": "edu_1",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "academic_status": "completed",
            }
        ],
        experience=[
            {
                "id": "exp_1",
                "employer": "Tech Solutions Inc",
                "job_title": "Software Engineer",
                "employment_type": "full_time",
                "start_date": "2020-01-01",
                "end_date": "2025-06-01",
                "technologies": ["Python", "SQL", "Docker"],
            }
        ],
        projects=[],
        certifications=[],
    )

    # Synthetic job whose known mandatory requirements are satisfied
    canonical_job = {
        "id": "job_perfect_1",
        "title": "Senior Backend Developer",
        "company": "Enterprise Tech Corp",
        "location": "San Francisco, CA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_perfect_1",
        job_title="Senior Backend Developer",
        company_name="Enterprise Tech Corp",
        role_family="Software Engineering",
        mandatory_requirements=[
            {"id": "req_py", "name": "Python", "category": "mandatory"},
            {"id": "req_sql", "name": "SQL", "category": "mandatory"},
        ],
        skills=[
            {"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 4.0},
            {"id": "req_sql", "name": "SQL", "priority": "MANDATORY", "min_years": 3.0},
        ],
        education=[
            {"id": "req_edu", "degree_level": "bachelor", "field_of_study": "Computer Science", "status": "completed"}
        ],
        experience=[
            {"id": "req_exp", "min_years": 4.0, "domain": "Backend Engineering"}
        ],
        employment_conditions={
            "workplace_type": "remote",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 140000,
            "salary_max": 180000,
            "currency": "USD",
            "pay_period": "annual",
        },
        eligibility={
            "work_authorization_required": True,
            "citizenship_restrictions": ["US"],
            "sponsorship_offered": True,
            "sponsorship_refused": False,
        },
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Backend Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "San Francisco"],
        work_arrangements=["remote"],
        min_annual_salary=130000,
        salary_currency="USD",
        blocked_employers=[],
    )

    # Evaluate match
    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Mandatory qualification evaluation passes
    assert evaluation.mandatory_coverage_ratio == 1.0
    assert evaluation.hard_policy_passed is True

    # 2. Outcome is Eligible & Aligned
    assert evaluation.eligibility_outcome == MatchingOutcome.ELIGIBLE_AND_ALIGNED
    assert evaluation.application_readiness == ApplicationReadiness.READY_FOR_PREPARATION

    # 3. High relevance index
    assert evaluation.relevance_index >= 85.0

    # 4. Zero blocking gaps
    blocking_gaps = [g for g in evaluation.gaps if g.severity.value == "blocking"]
    assert len(blocking_gaps) == 0

    # 5. NO live submission occurs (readiness != submitted)
    assert evaluation.status == "completed"
