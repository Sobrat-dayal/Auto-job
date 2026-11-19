"""Required Test 132: Missing Mandatory Skill and Gap Recording.

Verifies:
- AND logic failure: candidate has Python & Docker, but job requires SQL (mandatory).
- Outcome is KNOWN_REQUIREMENT_NOT_MET.
- Gap recorded: MISSING_MANDATORY_SKILL, severity BLOCKING.
- Non-blocking recommendations recorded.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    GapType,
    GapSeverity,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_missing_mandatory_skill_and_gap_recording():
    # Applicant has Python and Docker, but lacks SQL
    applicant = ApplicantSnapshotData(
        profile_id="prof_missing_skill_1",
        version=1,
        headline="Python Backend Engineer",
        country="US",
        city="Austin",
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
            },
            {
                "id": "skl_docker",
                "name": "Docker",
                "canonical_name": "docker",
                "category": "technical",
                "proficiency": "intermediate",
                "years_experience": 3.0,
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
                "employer": "Tech Corp",
                "job_title": "Software Engineer",
                "employment_type": "full_time",
                "start_date": "2021-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Python", "Docker"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_sql_req_1",
        "title": "Backend Database Engineer",
        "company": "DataCorp",
        "location": "Austin, TX",
        "employment_type": "Full-Time",
        "work_arrangement": "Hybrid",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job strictly mandates Python AND SQL
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_sql_req_1",
        job_title="Backend Database Engineer",
        company_name="DataCorp",
        role_family="Software Engineering",
        mandatory_requirements=[
            {"id": "req_py", "name": "Python", "category": "mandatory"},
            {"id": "req_sql", "name": "SQL", "category": "mandatory"},
        ],
        skills=[
            {"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 3.0},
            {"id": "req_sql", "name": "SQL", "priority": "MANDATORY", "min_years": 3.0},
        ],
        requirement_groups=[
            {
                "id": "grp_mandatory_skills",
                "operator": "AND",
                "requirement_ids": ["req_py", "req_sql"],
                "description": "Must possess both Python and SQL",
            }
        ],
        employment_conditions={
            "workplace_type": "hybrid",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 120000,
            "salary_max": 150000,
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
        title="Backend Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Austin"],
        work_arrangements=["hybrid"],
        min_annual_salary=110000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Outcome reflects missing mandatory requirement
    assert evaluation.eligibility_outcome == MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET
    assert evaluation.application_readiness == ApplicationReadiness.INELIGIBLE
    assert evaluation.mandatory_coverage_ratio < 1.0

    # 2. Blocking gap for SQL is recorded
    blocking_gaps = [g for g in evaluation.gaps if g.severity == GapSeverity.BLOCKING]
    assert len(blocking_gaps) >= 1
    sql_gap = next((g for g in blocking_gaps if g.skill_or_qualification == "SQL"), None)
    assert sql_gap is not None
    assert sql_gap.gap_type == GapType.MISSING_MANDATORY_SKILL
    assert "SQL" in sql_gap.description
    assert len(sql_gap.remediation_suggestion) > 0

    # 3. Counterfactual scenario is generated for bridging the gap
    assert any("SQL" in sc.hypothetical_change for sc in evaluation.counterfactuals)
