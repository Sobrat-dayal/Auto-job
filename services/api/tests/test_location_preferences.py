"""Unit tests for Section 105: Geographic, Work Arrangement, and Relocation Policies."""

import pytest
from app.recruitment.policy.contracts import (
    CareerStrategy,
    CompensationPolicy,
    GeographicPreference,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    RelocationPreference,
    UndisclosedSalaryHandling,
    WorkArrangement,
    WorkArrangementPreference,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.profile.contracts import ApplicantProfile, LocationInfo


@pytest.fixture
def location_strategy() -> CareerStrategy:
    return CareerStrategy(
        id="strat_loc_01",
        title="Location Strategy",
        work_arrangement=WorkArrangementPreference(
            allowed_arrangements=[WorkArrangement.REMOTE, WorkArrangement.HYBRID],
            preferred_arrangement=WorkArrangement.REMOTE,
            is_hard_constraint=True,  # Disallows ONSITE strictly
        ),
        geography=GeographicPreference(
            country="United States",
            allowed_countries=["United States"],
            allowed_cities=["Seattle", "San Francisco"],
            excluded_locations=["Miami", "Dallas"],
            remote_within_country_only=True,
            relocation=RelocationPreference.CONDITIONAL,
        ),
        compensation=CompensationPolicy(undisclosed_handling=UndisclosedSalaryHandling.CONSIDER),
    )


def test_location_and_arrangement_evaluation(location_strategy: CareerStrategy):
    profile = ApplicantProfile(
        id="p_us",
        owner_id="u_us",
        display_label="US Dev",
        location=LocationInfo(country="United States", city="Seattle"),
    )

    # 1. Remote permitted country (US candidate for US remote role) -> PROCEED
    job_remote_us = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Stripe",
        work_arrangement=WorkArrangement.REMOTE,
        location_country="United States",
        remote_country_restriction="United States",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_remote_us)
    dec = PolicyRulesEngine.evaluate_decision(location_strategy, job_remote_us, elig)
    assert dec.decision == PolicyDecisionOutcome.PROCEED

    # 2. Remote unsupported country (Remote restricted to Germany only) -> REJECTED_BY_PREFERENCE
    job_remote_de = JobOpportunityContext(
        title="Software Engineer",
        employer_name="SAP",
        work_arrangement=WorkArrangement.REMOTE,
        location_country="Germany",
        remote_country_restriction="Germany",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_remote_de)
    dec = PolicyRulesEngine.evaluate_decision(location_strategy, job_remote_de, elig)
    assert dec.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "Remote country boundary restriction" in dec.precedence_rule_applied

    # 3. Hybrid allowed city (Seattle) -> PROCEED
    job_hybrid_seattle = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Amazon",
        work_arrangement=WorkArrangement.HYBRID,
        location_city="Seattle",
        location_country="United States",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_hybrid_seattle)
    dec = PolicyRulesEngine.evaluate_decision(location_strategy, job_hybrid_seattle, elig)
    assert dec.decision == PolicyDecisionOutcome.PROCEED

    # 4. On-site position (Hard constraint disallows onsite) -> REJECTED_BY_PREFERENCE
    job_onsite = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Hardware Inc",
        work_arrangement=WorkArrangement.ONSITE,
        location_city="Seattle",
        location_country="United States",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_onsite)
    dec = PolicyRulesEngine.evaluate_decision(location_strategy, job_onsite, elig)
    assert dec.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "Hard work arrangement constraint" in dec.precedence_rule_applied

    # 5. Excluded city (Miami) -> REJECTED_BY_PREFERENCE
    job_miami = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Fintech Corp",
        work_arrangement=WorkArrangement.HYBRID,
        location_city="Miami",
        location_country="United States",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_miami)
    dec = PolicyRulesEngine.evaluate_decision(location_strategy, job_miami, elig)
    assert dec.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "Hard excluded location" in dec.precedence_rule_applied
