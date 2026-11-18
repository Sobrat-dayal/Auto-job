"""Unit tests for Section 107: Employer Allowlist, Blocklist, and Identity Ambiguity."""

import pytest
from app.recruitment.policy.contracts import (
    AllowlistMode,
    BlockedEmployerItem,
    CareerStrategy,
    CompensationPolicy,
    EmployerRestrictions,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    ReviewTrigger,
    UndisclosedSalaryHandling,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.employers.restrictions import EmployerRestrictionController
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.profile.contracts import ApplicantProfile, LocationInfo


@pytest.fixture
def employer_strategy() -> CareerStrategy:
    return CareerStrategy(
        id="strat_emp_01",
        title="Employer Strategy",
        compensation=CompensationPolicy(undisclosed_handling=UndisclosedSalaryHandling.CONSIDER),
        employers=EmployerRestrictions(
            allowlist_mode=AllowlistMode.NO_ALLOWLIST,
            allowed_employers=["Stripe", "GitHub", "Vercel"],
            blocked_employers=[
                BlockedEmployerItem(
                    id="blk_01",
                    employer_name="BadCorp Technologies",
                    domain="badcorp.com",
                    reason="Wage theft and predatory non-compete clauses",
                )
            ],
        ),
    )


def test_employer_blocklist_enforcement(employer_strategy: CareerStrategy):
    profile = ApplicantProfile(id="p1", owner_id="u1", display_label="Test", location=LocationInfo(country="United States"))

    # 1. Preferred employer can proceed
    job_stripe = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Stripe",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_stripe)
    dec_stripe = PolicyRulesEngine.evaluate_decision(employer_strategy, job_stripe, elig)
    assert dec_stripe.decision == PolicyDecisionOutcome.PROCEED

    # 2. Blocked employer is denied
    job_bad = JobOpportunityContext(
        title="Software Engineer",
        employer_name="BadCorp Technologies Inc.",
        employer_domain="badcorp.com",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_bad)
    dec_bad = PolicyRulesEngine.evaluate_decision(employer_strategy, job_bad, elig)
    assert dec_bad.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY
    assert "Level 6: Employer blocklist enforcement" in dec_bad.precedence_rule_applied
    assert "Wage theft and predatory non-compete clauses" in dec_bad.explanation

    # 3. Block by domain alone
    job_domain = JobOpportunityContext(
        title="Software Engineer",
        employer_name="Stealth Subsidiary",
        employer_domain="badcorp.com",
    )
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_domain)
    dec_dom = PolicyRulesEngine.evaluate_decision(employer_strategy, job_domain, elig)
    assert dec_dom.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY


def test_strict_allowlist_enforcement(employer_strategy: CareerStrategy):
    profile = ApplicantProfile(id="p1", owner_id="u1", display_label="Test", location=LocationInfo(country="United States"))
    employer_strategy.employers.allowlist_mode = AllowlistMode.STRICT_ALLOWLIST

    # Allowed employer passes
    job_gh = JobOpportunityContext(title="Software Engineer", employer_name="GitHub")
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_gh)
    dec_gh = PolicyRulesEngine.evaluate_decision(employer_strategy, job_gh, elig)
    assert dec_gh.decision == PolicyDecisionOutcome.PROCEED

    # Unlisted employer fails strict allowlist
    job_unlisted = JobOpportunityContext(title="Software Engineer", employer_name="Random Startup LLC")
    elig = JobEligibilityEvaluator.evaluate_eligibility(profile, job_unlisted)
    dec_unlisted = PolicyRulesEngine.evaluate_decision(employer_strategy, job_unlisted, elig)
    assert dec_unlisted.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY
    assert "strict allowlist" in dec_unlisted.explanation


def test_ambiguous_employer_identity():
    blocked = [
        BlockedEmployerItem(id="b1", employer_name="Stripe Global", domain="stripeglobal.com")
    ]
    # "Stripe Payments" is similar to "Stripe Global", so it flags ambiguity
    is_amb, reason = EmployerRestrictionController.is_identity_ambiguous("Stripe Payments", blocked)
    assert is_amb is True
    assert "Stripe Global" in reason
