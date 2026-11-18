"""Unit tests for Section 109: Policy Precedence Hierarchy and Conflicting Scenarios."""

import pytest
from app.recruitment.policy.contracts import (
    AllowlistMode,
    BlockedEmployerItem,
    CareerStrategy,
    EmployerRestrictions,
    GeographicPreference,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    WorkArrangement,
    WorkArrangementPreference,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.profile.contracts import ApplicantProfile, LocationInfo


@pytest.fixture
def base_strategy() -> CareerStrategy:
    return CareerStrategy(
        id="strat_prec_01",
        title="Precedence Strategy",
        work_arrangement=WorkArrangementPreference(
            allowed_arrangements=[WorkArrangement.REMOTE],
            is_hard_constraint=True,
        ),
        geography=GeographicPreference(
            country="United States",
            allowed_countries=["United States"],
            excluded_locations=["Dallas"],
        ),
        employers=EmployerRestrictions(
            allowed_employers=["Google"],
            blocked_employers=[
                BlockedEmployerItem(id="b1", employer_name="Google", reason="Explicit user block")
            ],
        ),
    )


def test_preferred_employer_blocked_precedence(base_strategy: CareerStrategy):
    """When an employer is both preferred/allowlisted and explicitly blocked, the blocklist takes absolute precedence."""
    profile = ApplicantProfile(id="p1", owner_id="u1", display_label="Dev")
    job = JobOpportunityContext(title="Backend Engineer", employer_name="Google")
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job)

    decision = PolicyRulesEngine.evaluate_decision(base_strategy, job, elig)
    assert decision.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY
    assert "Level 6: Employer blocklist enforcement" in decision.precedence_rule_applied
    assert "Explicit user block" in decision.explanation


def test_emergency_stop_precedence(base_strategy: CareerStrategy):
    """When Emergency Stop is active, it overrides all other rules (Level 1 precedence)."""
    profile = ApplicantProfile(id="p1", owner_id="u1", display_label="Dev")
    job = JobOpportunityContext(title="Backend Engineer", employer_name="Stripe")
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job)

    decision = PolicyRulesEngine.evaluate_decision(base_strategy, job, elig, is_emergency_stop_active=True)
    assert decision.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY
    assert "Level 1: Emergency Stop active" in decision.precedence_rule_applied


def test_high_relevance_outside_geography_fails(base_strategy: CareerStrategy):
    """A position with high skill alignment that is in an excluded location is rejected by hard preference (Level 8)."""
    profile = ApplicantProfile(id="p1", owner_id="u1", display_label="Dev")
    job = JobOpportunityContext(
        title="Backend Engineer",
        employer_name="Stripe",
        work_arrangement=WorkArrangement.REMOTE,
        location_city="Dallas",  # Dallas is excluded
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job)

    decision = PolicyRulesEngine.evaluate_decision(base_strategy, job, elig)
    assert decision.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "Level 8: Hard excluded location" in decision.precedence_rule_applied


def test_conflict_detector():
    """PolicyRulesEngine.detect_conflicts detects allowlist/blocklist collision."""
    strat = CareerStrategy(
        id="s1",
        title="Contradictory Strat",
        employers=EmployerRestrictions(
            allowed_employers=["Microsoft"],
            blocked_employers=[BlockedEmployerItem(id="b1", employer_name="Microsoft", reason="Block")],
        ),
    )
    conflicts = PolicyRulesEngine.detect_conflicts(strat)
    assert len(conflicts) > 0
    assert any("Microsoft" in c.title for c in conflicts)
