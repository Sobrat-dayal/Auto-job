"""Unit tests for Section 106: Compensation Normalizer, Multi-Currency Comparison, and Units."""

from decimal import Decimal
import pytest
from app.recruitment.policy.compensation.normalizer import CompensationNormalizer
from app.recruitment.policy.contracts import (
    CareerStrategy,
    CompensationMatchStatus,
    CompensationPolicy,
    CompensationUnit,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    UndisclosedSalaryHandling,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.profile.contracts import ApplicantProfile


@pytest.fixture
def comp_policy() -> CompensationPolicy:
    return CompensationPolicy(
        currency="USD",
        unit=CompensationUnit.ANNUAL,
        min_acceptable_amount=Decimal("90000.00"),
        preferred_min=Decimal("120000.00"),
        preferred_max=Decimal("160000.00"),
        undisclosed_handling=UndisclosedSalaryHandling.REQUIRE_REVIEW,
        is_hard_minimum=True,
    )


def test_annualization_units():
    # Hourly: $50/hr * 40 hrs * 52 wks = $104,000
    assert CompensationNormalizer.annualize_amount(Decimal("50.00"), CompensationUnit.HOURLY) == Decimal("104000.00")
    # Monthly: $10,000/mo * 12 mos = $120,000
    assert CompensationNormalizer.annualize_amount(Decimal("10000.00"), CompensationUnit.MONTHLY) == Decimal("120000.00")
    # Weekly: $2,500/wk * 52 wks = $130,000
    assert CompensationNormalizer.annualize_amount(Decimal("2500.00"), CompensationUnit.WEEKLY) == Decimal("130000.00")
    # Stipend: $10,000 summer stipend * 4 = $40,000
    assert CompensationNormalizer.annualize_amount(Decimal("10000.00"), CompensationUnit.STIPEND) == Decimal("40000.00")


def test_compensation_evaluation(comp_policy: CompensationPolicy):
    # 1. Within preferred range ($130,000)
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=Decimal("130000.00"),
        offered_max=Decimal("150000.00"),
    )
    assert status == CompensationMatchStatus.WITHIN_PREFERRED_RANGE
    assert ann == Decimal("130000.00")

    # 2. Meets minimum but below preferred target ($100,000)
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=Decimal("100000.00"),
        offered_max=Decimal("110000.00"),
    )
    assert status == CompensationMatchStatus.MEETS_MINIMUM
    assert ann == Decimal("100000.00")

    # 3. Below hard minimum ($70,000 < $90,000)
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=Decimal("70000.00"),
        offered_max=Decimal("80000.00"),
    )
    assert status == CompensationMatchStatus.BELOW_MINIMUM
    assert ann == Decimal("70000.00")

    # 4. Hourly equivalent ($60/hr -> $124,800 annualized)
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=Decimal("60.00"),
        offered_max=Decimal("65.00"),
        offered_unit=CompensationUnit.HOURLY,
    )
    assert status == CompensationMatchStatus.WITHIN_PREFERRED_RANGE
    assert ann == Decimal("124800.00")

    # 5. Undisclosed salary with REQUIRE_REVIEW setting
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=None,
        offered_max=None,
    )
    assert status == CompensationMatchStatus.COMPENSATION_UNKNOWN
    assert ann is None

    # 6. Currency comparison without verified exchange rates -> NOT_COMPARABLE
    status, ann, exp = CompensationNormalizer.evaluate_compensation(
        policy=comp_policy,
        offered_min=Decimal("100000.00"),
        offered_max=Decimal("120000.00"),
        offered_currency="EUR",  # Policy requires USD
        exchange_rate=None,  # No exchange rate
    )
    assert status == CompensationMatchStatus.NOT_COMPARABLE
    assert "No verified exchange rate available" in exp
