"""Unit tests for Stage 25 Recruitment Policy Models, Contracts, and Budgets."""

from decimal import Decimal
import pytest
from app.recruitment.policy.contracts import (
    AllowlistMode,
    AutonomyMode,
    CareerStrategy,
    CompensationPolicy,
    CompensationUnit,
    GeographicPreference,
    RecruitmentBudget,
    RoleFamily,
    SeniorityLevel,
    TargetRoleItem,
    WorkArrangement,
)


def test_career_strategy_model_defaults():
    strategy = CareerStrategy(
        title="Default Test Strategy",
        owner_id="usr_01",
    )
    assert strategy.title == "Default Test Strategy"
    assert strategy.is_active is False
    assert strategy.autonomy_mode == AutonomyMode.PREPARE_AND_REVIEW
    assert strategy.compensation.currency == "USD"
    assert strategy.geography.country == "United States"


def test_recruitment_budget_remaining_calculations():
    budget = RecruitmentBudget(
        owner_id="usr_01",
        max_daily_applications=20,
        max_weekly_applications=80,
        max_monthly_applications=300,
        daily_reserved=3,
        daily_confirmed=7,
        weekly_confirmed=25,
        monthly_confirmed=100,
    )

    # Remaining daily = 20 - (3 reserved + 7 confirmed) = 10
    assert budget.remaining_daily == 10
    # Remaining weekly = 80 - 25 = 55
    assert budget.remaining_weekly == 55
    # Remaining monthly = 300 - 100 = 200
    assert budget.remaining_monthly == 200


def test_compensation_policy_annualization_settings():
    comp = CompensationPolicy(
        currency="USD",
        unit=CompensationUnit.HOURLY,
        min_acceptable_amount=Decimal("50.00"),
        preferred_min=Decimal("70.00"),
        hours_per_week_assumption=40,
        weeks_per_year_assumption=52,
    )
    assert comp.hours_per_week_assumption == 40
    assert comp.weeks_per_year_assumption == 52
    assert comp.is_hard_minimum is True
