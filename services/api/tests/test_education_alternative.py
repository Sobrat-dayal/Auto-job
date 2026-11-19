"""Required Test 134: Degree Requirement and Practical Experience Equivalent.

Verifies:
- Candidate holds an Associate degree, but has 5 years of verified professional experience.
- Job specifies "Bachelor's degree or 4+ years equivalent professional experience".
- Practical experience waiver applies.
- Requirement is evaluated as SATISFIED_BY_ALTERNATIVE.
- Overall outcome is CONDITIONALLY_ELIGIBLE or ELIGIBLE_AND_ALIGNED (not blocked).
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
async def test_degree_requirement_practical_experience_waiver():
    # Applicant has Associate degree + 5 years of verified professional experience
    applicant = ApplicantSnapshotData(
        profile_id="prof_assoc_waiver_1",
        version=1,
        headline="Senior Systems Administrator",
        country="US",
        city="Denver",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_linux",
                "name": "Linux",
                "canonical_name": "linux",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 5.0,
                "is_verified": True,
            }
        ],
        education=[
            {
                "id": "edu_assoc",
                "degree": "Associate of Science",
                "field_of_study": "Computer Information Systems",
                "academic_status": "completed",
            }
        ],
        experience=[
            {
                "id": "exp_sysadmin",
                "employer": "Enterprise IT Corp",
                "job_title": "Systems Administrator",
                "employment_type": "full_time",
                "start_date": "2020-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Linux"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_syseng_waiver_1",
        "title": "Senior Systems Engineer",
        "company": "Cloud Infrastructure Co",
        "location": "Denver, CO",
        "employment_type": "Full-Time",
        "work_arrangement": "Hybrid",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job requires Bachelor's degree OR 4 years equivalent experience
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_syseng_waiver_1",
        job_title="Senior Systems Engineer",
        company_name="Cloud Infrastructure Co",
        role_family="Infrastructure",
        skills=[
            {"id": "req_linux", "name": "Linux", "priority": "MANDATORY", "min_years": 4.0},
        ],
        education=[
            {
                "id": "req_edu_degree",
                "degree_level": "bachelor",
                "field_of_study": "Computer Science",
                "status": "completed",
                "practical_experience_waiver": True,
                "years_experience_equivalent": 4.0,
            }
        ],
        experience=[
            {"id": "req_exp_infra", "min_years": 4.0, "domain": "Infrastructure"}
        ],
        employment_conditions={
            "workplace_type": "hybrid",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 130000,
            "salary_max": 160000,
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
        title="Systems Engineering",
        role_families=["Infrastructure"],
        target_locations=["US", "Denver"],
        work_arrangements=["hybrid"],
        min_annual_salary=120000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Education detail shows alternative practical experience equivalence
    assert evaluation.education_detail is not None
    assert (
        evaluation.education_detail.match_status
        == RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE
    )
    assert "practical equivalency" in evaluation.education_detail.explanation.lower()

    # 2. Education requirement result is satisfied
    edu_req_res = next(
        (r for r in evaluation.requirement_results if r.requirement_id == "req_edu_degree" or "bachelor" in r.name.lower()),
        None,
    )
    assert edu_req_res is not None
    assert edu_req_res.is_satisfied is True
    assert edu_req_res.match_category == RequirementMatchCategory.SATISFIED_BY_ALTERNATIVE

    # 3. Overall outcome is conditionally eligible (accepted practical route)
    assert evaluation.eligibility_outcome == MatchingOutcome.CONDITIONALLY_ELIGIBLE
    assert evaluation.application_readiness == ApplicationReadiness.READY_FOR_PREPARATION
    assert evaluation.hard_policy_passed is True
