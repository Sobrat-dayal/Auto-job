"""Required Test 136: Academic Project vs. Professional Experience Tenure.

Verifies:
- Candidate has completed multiple academic projects and coursework, but has zero professional employment tenure.
- Job specifies 3+ years of professional software engineering experience.
- Matching engine strictly differentiates academic projects from professional employment.
- Experience requirement evaluated as RELATED_EXPERIENCE_ONLY.
- Mandatory tenure requirement is NOT satisfied.
- Blocking gap is recorded.
"""

import pytest
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    ApplicationReadiness,
    RequirementMatchCategory,
    GapType,
    GapSeverity,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match


@pytest.mark.asyncio
async def test_academic_project_vs_professional_tenure():
    # Applicant has academic projects only, NO professional roles
    applicant = ApplicantSnapshotData(
        profile_id="prof_academic_only_1",
        version=1,
        headline="Recent Computer Science Graduate",
        country="US",
        city="Boston",
        authorized_countries=["US"],
        requires_sponsorship=False,
        skills=[
            {
                "id": "skl_java",
                "name": "Java",
                "canonical_name": "java",
                "category": "technical",
                "proficiency": "intermediate",
                "years_experience": 2.0,
                "is_verified": True,
            }
        ],
        education=[
            {
                "id": "edu_bsc",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "academic_status": "completed",
            }
        ],
        experience=[],  # Zero professional employment records
        projects=[
            {
                "id": "proj_capstone",
                "title": "Distributed Key-Value Store",
                "category": "academic",
                "role": "Lead Student Developer",
                "technologies": ["Java"],
            },
            {
                "id": "proj_compiler",
                "title": "C-Minus Compiler",
                "category": "academic",
                "role": "Team Member",
                "technologies": ["Java", "C++"],
            },
        ],
        certifications=[],
    )

    canonical_job = {
        "id": "job_mid_backend_1",
        "title": "Backend Software Engineer",
        "company": "Enterprise Software LLC",
        "location": "Boston, MA",
        "employment_type": "Full-Time",
        "work_arrangement": "Hybrid",
        "status": "active",
        "discovered_at": "2026-03-30T10:00:00Z",
    }

    # Job strictly mandates 3+ years professional experience
    job_intel = JobIntelligenceSnapshotData(
        canonical_job_id="job_mid_backend_1",
        job_title="Backend Software Engineer",
        company_name="Enterprise Software LLC",
        role_family="Software Engineering",
        skills=[
            {"id": "req_java", "name": "Java", "priority": "MANDATORY", "min_years": 2.0},
        ],
        experience=[
            {
                "id": "req_exp_tenure",
                "min_years": 3.0,
                "domain": "Software Engineering",
                "entry_level_waiver": False,
            }
        ],
        employment_conditions={
            "workplace_type": "hybrid",
            "remote_allowed_countries": ["US"],
            "employment_type": "full_time",
        },
        compensation={
            "salary_min": 110000,
            "salary_max": 140000,
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
        title="Software Engineering",
        role_families=["Software Engineering"],
        target_locations=["US", "Boston"],
        work_arrangements=["hybrid"],
        min_annual_salary=100000,
        salary_currency="USD",
        blocked_employers=[],
    )

    evaluation = evaluate_job_match(
        applicant_snapshot=applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intel,
        career_strategy=policy,
    )

    # 1. Experience detail shows distinction: academic projects receive related experience credit only
    assert evaluation.experience_detail is not None
    assert evaluation.experience_detail.calculated_professional_years == 0.0
    assert evaluation.experience_detail.academic_project_count == 2
    assert (
        evaluation.experience_detail.match_status
        == RequirementMatchCategory.RELATED_EXPERIENCE_ONLY
    )
    assert "academic project" in evaluation.experience_detail.explanation.lower()

    # 2. Mandatory experience requirement is not satisfied
    exp_res = next(
        (r for r in evaluation.requirement_results if r.requirement_id == "req_exp_tenure"),
        None,
    )
    assert exp_res is not None
    assert exp_res.is_satisfied is False
    assert exp_res.match_category == RequirementMatchCategory.RELATED_EXPERIENCE_ONLY

    # 3. Overall outcome is KNOWN_REQUIREMENT_NOT_MET
    assert evaluation.eligibility_outcome == MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET
    assert evaluation.application_readiness == ApplicationReadiness.INELIGIBLE

    # 4. Gap is recorded
    gap = next((g for g in evaluation.gaps if "experience" in g.skill_or_qualification.lower()), None)
    assert gap is not None
    assert gap.severity == GapSeverity.BLOCKING
    assert gap.gap_type == GapType.RELATED_ONLY
