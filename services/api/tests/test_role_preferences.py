"""Unit tests for Section 104: Target Role Preferences, Taxonomy, and Seniority Constraints."""

import pytest
from app.recruitment.policy.contracts import (
    CareerStrategy,
    CompensationPolicy,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    RoleFamily,
    SeniorityLevel,
    SeniorityPreference,
    TargetRoleItem,
    UndisclosedSalaryHandling,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.policy.taxonomy.roles import RoleTaxonomyEngine
from app.recruitment.profile.contracts import ApplicantProfile, LocationInfo


@pytest.fixture
def role_strategy() -> CareerStrategy:
    return CareerStrategy(
        id="strat_test_roles",
        title="Role Preference Strategy",
        target_roles=[
            TargetRoleItem(
                id="r1",
                title="Backend Engineer",
                role_family=RoleFamily.BACKEND,
                priority=1,
            ),
            TargetRoleItem(
                id="r2",
                title="AI/ML Engineer",
                role_family=RoleFamily.AI_ML,
                priority=1,
            ),
            TargetRoleItem(
                id="r3",
                title="Frontend Developer",
                role_family=RoleFamily.FRONTEND,
                priority=2,
            ),
            TargetRoleItem(
                id="r4",
                title="Senior Engineering Manager",
                role_family=RoleFamily.BACKEND,
                seniority=SeniorityLevel.MANAGEMENT,
                is_excluded=True,
                priority=10,
            ),
        ],
        seniority=SeniorityPreference(
            allowed_levels=[SeniorityLevel.ENTRY_LEVEL, SeniorityLevel.JUNIOR, SeniorityLevel.MID_LEVEL, SeniorityLevel.SENIOR]
        ),
        compensation=CompensationPolicy(undisclosed_handling=UndisclosedSalaryHandling.CONSIDER),
    )


def test_role_family_classification():
    # Verify deterministic taxonomy mapping
    assert RoleTaxonomyEngine.classify_role_family("Principal Backend Architect") == RoleFamily.BACKEND
    assert RoleTaxonomyEngine.classify_role_family("Machine Learning Research Scientist") == RoleFamily.RESEARCH
    assert RoleTaxonomyEngine.classify_role_family("Staff ML Engineer") == RoleFamily.AI_ML
    assert RoleTaxonomyEngine.classify_role_family("React Frontend Developer") == RoleFamily.FRONTEND
    assert RoleTaxonomyEngine.classify_role_family("Site Reliability Engineer") == RoleFamily.CLOUD_DEVOPS


def test_seniority_detection():
    assert RoleTaxonomyEngine.detect_seniority("Software Engineering Intern") == SeniorityLevel.INTERNSHIP
    assert RoleTaxonomyEngine.detect_seniority("Junior Python Developer") == SeniorityLevel.ENTRY_LEVEL
    assert RoleTaxonomyEngine.detect_seniority("Senior Distributed Systems Engineer") == SeniorityLevel.SENIOR
    assert RoleTaxonomyEngine.detect_seniority("Staff Software Engineer") == SeniorityLevel.STAFF


def test_role_preferences_evaluation(role_strategy: CareerStrategy):
    profile = ApplicantProfile(
        id="p1", owner_id="u1", display_label="Test Dev", location=LocationInfo(country="United States")
    )

    # 1. Backend Engineer (High Priority Match)
    job_backend = JobOpportunityContext(
        title="Senior Backend Engineer",
        employer_name="Stripe",
        role_family=RoleFamily.BACKEND,
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_backend)
    dec_backend = PolicyRulesEngine.evaluate_decision(role_strategy, job_backend, elig)
    assert dec_backend.decision == PolicyDecisionOutcome.PROCEED
    assert dec_backend.overall_score >= 80.0
    assert any("Backend Engineer" in m for p in dec_backend.soft_preferences for m in p.matched_elements)

    # 2. AI/ML Engineer (High Priority Match)
    job_ai = JobOpportunityContext(
        title="AI/ML Engineer - Inference Platform",
        employer_name="Anthropic",
        role_family=RoleFamily.AI_ML,
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_ai)
    dec_ai = PolicyRulesEngine.evaluate_decision(role_strategy, job_ai, elig)
    assert dec_ai.decision == PolicyDecisionOutcome.PROCEED

    # 3. Frontend Developer (Acceptable Priority 2)
    job_fe = JobOpportunityContext(
        title="Frontend Developer",
        employer_name="Vercel",
        role_family=RoleFamily.FRONTEND,
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_fe)
    dec_fe = PolicyRulesEngine.evaluate_decision(role_strategy, job_fe, elig)
    assert dec_fe.decision == PolicyDecisionOutcome.PROCEED

    # 4. Senior Engineering Manager (Explicitly Excluded -> REJECTED_BY_PREFERENCE)
    job_mgr = JobOpportunityContext(
        title="Senior Engineering Manager - Infrastructure",
        employer_name="Google",
        role_family=RoleFamily.BACKEND,
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_mgr)
    dec_mgr = PolicyRulesEngine.evaluate_decision(role_strategy, job_mgr, elig)
    assert dec_mgr.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "Excluded Job Title" in dec_mgr.hard_constraints[0].rule_name
    assert "Senior Engineering Manager" in dec_mgr.explanation
