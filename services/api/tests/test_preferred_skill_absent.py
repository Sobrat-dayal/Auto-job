"""Required Test 138: Missing Preferred Skill Handling.

Verifies:
- Job mandates Python (MANDATORY) and prefers GraphQL (PREFERRED).
- Candidate profile has verified Python skills, but no GraphQL evidence.
- Mandatory qualification is directly satisfied (mandatory_coverage_ratio = 1.0).
- Preferred qualification is NOT satisfied (preferred_coverage_ratio < 1.0).
- Outcome is ELIGIBLE_AND_ALIGNED (candidate is NOT disqualified).
- Gap recorded for GraphQL has severity MODERATE (non-blocking).
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
    GapSeverity,
    GapType,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_missing_preferred_skill_does_not_block():
    # Applicant with Python, lacking GraphQL
    applicant = ApplicantSnapshotData(
        profile_id="prof_pref_skill_1",
        version=1,
        headline="Senior Python Engineer",
        country="US",
        city="Atlanta",
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
            }
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
                "employer": "Tech Hub",
                "job_title": "Python Developer",
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
        "id": "job_graphql_pref_1",
        "title": "Senior API Engineer",
        "company": "Modern Cloud Solutions",
        "location": "Atlanta, GA",
        "employment_type": "Full-Time",
        "work_arrangement": "Remote",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job: Python is MANDATORY, GraphQL is PREFERRED
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_graphql_pref_1",
        job_title="Senior API Engineer",
        company_name="Modern Cloud Solutions",
        role_family="Software Engineering",
        skills=[
            {"id": "req_py", "name": "Python", "priority": "MANDATORY", "min_years": 4.0},
            {"id": "req_gql", "name": "GraphQL", "priority": "PREFERRED", "min_years": 2.0},
        ],
        employment_conditions={
            "workplace_type": "remote",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 135000,
            "salary_max": 165000,
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
        title="API Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Atlanta"],
        work_arrangements=["remote"],
        min_annual_salary=125000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Mandatory coverage is 100%, preferred coverage is < 1.0 (GraphQL unmet)
    assert evaluation.mandatory_coverage_ratio == 1.0
    assert evaluation.preferred_coverage_ratio < 1.0
    assert evaluation.preferred_coverage_ratio == 0.5

    # 2. Candidate is NOT blocked: outcome is ELIGIBLE_AND_ALIGNED
    assert evaluation.eligibility_outcome == MatchingOutcome.ELIGIBLE_AND_ALIGNED
    assert evaluation.application_readiness == ApplicationReadiness.READY_FOR_PREPARATION
    assert evaluation.hard_policy_passed is True

    # 3. GraphQL is evaluated as not evidenced, but non-blocking
    gql_req = next(
        (r for r in evaluation.requirement_results if r.name == "GraphQL"), None
    )
    assert gql_req is not None
    assert gql_req.match_category == RequirementMatchCategory.NOT_EVIDENCED
    assert gql_req.category == "preferred"

    # 4. Gap exists for GraphQL, but severity is MODERATE (not BLOCKING)
    gql_gap = next(
        (g for g in evaluation.gaps if g.skill_or_qualification == "GraphQL"), None
    )
    assert gql_gap is not None
    assert gql_gap.severity == GapSeverity.MODERATE
    assert gql_gap.gap_type == GapType.MISSING_PREFERRED_SKILL

    # 5. Zero blocking gaps overall
    blocking_gaps = [g for g in evaluation.gaps if g.severity == GapSeverity.BLOCKING]
    assert len(blocking_gaps) == 0
