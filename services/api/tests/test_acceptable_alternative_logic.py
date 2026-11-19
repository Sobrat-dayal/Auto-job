"""Required Test 133: Acceptable Alternative Logic Evaluation.

Verifies:
- OR logic: Candidate has Python, job requires "Java OR Python".
- Logical group is evaluated as satisfied via acceptable alternative.
- Candidate does NOT get blocked because Java is missing.
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
async def test_acceptable_alternative_or_logic():
    # Applicant has Python, but NOT Java
    applicant = ApplicantSnapshotData(
        profile_id="prof_py_dev_1",
        version=1,
        headline="Python Specialist",
        country="US",
        city="Seattle",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_python",
                "name": "Python",
                "canonical_name": "python",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 6.0,
                "is_verified": True,
            }
        ],
        education=[
            {
                "id": "edu_1",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Engineering",
                "academic_status": "completed",
            }
        ],
        experience=[
            {
                "id": "exp_1",
                "employer": "CloudTech",
                "job_title": "Backend Engineer",
                "employment_type": "full_time",
                "start_date": "2020-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Python"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_polyglot_1",
        "title": "Senior Software Engineer",
        "company": "Enterprise Cloud Systems",
        "location": "Seattle, WA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job requires Java OR Python as acceptable alternatives
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_polyglot_1",
        job_title="Senior Software Engineer",
        company_name="Enterprise Cloud Systems",
        role_family="Software Engineering",
        skills=[
            {"id": "req_java", "name": "Java", "priority": "MANDATORY", "min_years": 4.0},
            {"id": "req_python", "name": "Python", "priority": "MANDATORY", "min_years": 4.0},
        ],
        requirement_groups=[
            {
                "id": "grp_core_backend_lang",
                "operator": "OR",
                "requirement_ids": ["req_java", "req_python"],
                "description": "Proficiency in Java or Python required",
            }
        ],
        employment_conditions={
            "workplace_type": "remote",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 150000,
            "salary_max": 190000,
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
        title="Senior Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Seattle"],
        work_arrangements=["remote"],
        min_annual_salary=140000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. OR group must be satisfied
    or_group = next(
        (g for g in evaluation.group_results if g.group_id == "grp_core_backend_lang"),
        None,
    )
    assert or_group is not None
    assert or_group.is_satisfied is True
    assert "OR" in or_group.operator

    # 2. Python is directly satisfied, Java is not evidenced, but group passes
    python_req = next(
        (r for r in evaluation.requirement_results if r.name == "Python"), None
    )
    assert python_req is not None
    assert python_req.match_category == RequirementMatchCategory.DIRECTLY_SATISFIED

    java_req = next(
        (r for r in evaluation.requirement_results if r.name == "Java"), None
    )
    assert java_req is not None
    assert java_req.match_category == RequirementMatchCategory.NOT_EVIDENCED

    # 3. Overall outcome is NOT blocked
    assert evaluation.eligibility_outcome in (
        MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        MatchingOutcome.ELIGIBLE_BUT_LOWER_PRIORITY,
        MatchingOutcome.CONDITIONALLY_ELIGIBLE,
    )
    assert evaluation.hard_policy_passed is True
