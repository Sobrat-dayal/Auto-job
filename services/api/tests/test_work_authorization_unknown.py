"""Required Test 139: Unknown Work Authorization Conservative Handling.

Verifies:
- Candidate profile has unconfirmed work authorization (authorized_countries = []).
- Job mandates UK work authorization.
- Engine does NOT guess or infer authorization based on city, nationality, or surname.
- Requirement status is evaluated as UNKNOWN.
- Review request is generated for the applicant.
- Final outcome is REQUIRES_APPLICANT_REVIEW (Readiness: REQUIRES_REVIEW).
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
    ReviewType,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_unknown_work_authorization_triggers_review():
    # Applicant with no confirmed work authorization on file
    applicant = ApplicantSnapshotData(
        profile_id="prof_unknown_auth_1",
        version=1,
        headline="Software Engineer",
        country="GB",
        city="London",
        authorized_countries=[],  # Unconfirmed / Empty
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_go",
                "name": "Go",
                "canonical_name": "go",
                "category": "technical",
                "proficiency": "expert",
                "years_experience": 4.0,
                "is_verified": True,
            }
        ],
        education=[],
        experience=[
            {
                "id": "exp_1",
                "employer": "Tech UK",
                "job_title": "Backend Engineer",
                "employment_type": "full_time",
                "start_date": "2021-01-01",
                "end_date": "2025-01-01",
                "technologies": ["Go"],
            }
        ],
        projects=[],
        certifications=[],
    )

    canonical_job = {
        "id": "job_uk_auth_1",
        "title": "Go Systems Developer",
        "company": "London FinTech Ltd",
        "location": "London, UK",
        "employment_type": "Full-Time",
        "work_arrangement": "Hybrid",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_uk_auth_1",
        job_title="Go Systems Developer",
        company_name="London FinTech Ltd",
        role_family="Software Engineering",
        skills=[
            {"id": "req_go", "name": "Go", "priority": "MANDATORY", "min_years": 3.0},
        ],
        employment_conditions={
            "workplace_type": "hybrid",
            "remote_allowed_countries": ["GB"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 75000,
            "salary_max": 95000,
            "currency": "GBP",
            "pay_period": "annual",
        },
        eligibility={
            "work_authorization_required": True,
            "citizenship_restrictions": ["GB"],
            "sponsorship_offered": False,
            "sponsorship_refused": False,
        },
    )

    policy = CareerStrategySnapshotData(
        strategy_id="strat_1",
        title="Go Engineering",
        role_families=["Software Engineering"],
        target_locations=["GB", "London"],
        work_arrangements=["hybrid"],
        min_annual_salary=70000,
        salary_currency="GBP",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Work authorization requirement is evaluated as UNKNOWN (no inference)
    auth_req = next(
        (r for r in evaluation.requirement_results if "work authorization" in r.name.lower()),
        None,
    )
    assert auth_req is not None
    assert auth_req.match_category == RequirementMatchCategory.UNKNOWN
    assert auth_req.is_satisfied is False

    # 2. Outcome is REQUIRES_APPLICANT_REVIEW
    assert evaluation.eligibility_outcome == MatchingOutcome.REQUIRES_APPLICANT_REVIEW
    assert evaluation.application_readiness == ApplicationReadiness.REQUIRES_REVIEW

    # 3. Actionable review request generated
    assert len(evaluation.review_requests) >= 1
    auth_review = next(
        (rev for rev in evaluation.review_requests if rev.get("review_type") == ReviewType.UNKNOWN_WORK_AUTH or "authorization" in rev.get("reason", "").lower()),
        None,
    )
    assert auth_review is not None
