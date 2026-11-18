"""Compensation Normalizer, Unit Conversion, and Multi-Currency Comparator (Stage 25)."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from app.recruitment.policy.contracts import (
    CompensationMatchStatus,
    CompensationPolicy,
    CompensationUnit,
    UndisclosedSalaryHandling,
)


class CompensationNormalizer:
    """Normalizes job compensation into comparable annual base figures and evaluates against policy."""

    @classmethod
    def annualize_amount(
        cls,
        amount: Decimal,
        unit: CompensationUnit,
        hours_per_week: int = 40,
        weeks_per_year: int = 52,
    ) -> Decimal:
        """Converts hourly, monthly, weekly, or stipend figures into an annualized baseline."""
        if unit == CompensationUnit.ANNUAL:
            return amount
        elif unit == CompensationUnit.HOURLY:
            return (amount * Decimal(hours_per_week) * Decimal(weeks_per_year)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif unit == CompensationUnit.DAILY:
            return (amount * Decimal(5) * Decimal(weeks_per_year)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif unit == CompensationUnit.WEEKLY:
            return (amount * Decimal(weeks_per_year)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif unit == CompensationUnit.MONTHLY:
            return (amount * Decimal(12)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif unit == CompensationUnit.STIPEND:
            # Internship stipend typically covers a 3-month summer term
            return (amount * Decimal(4)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif unit == CompensationUnit.FIXED_CONTRACT:
            return amount

        return amount

    @classmethod
    def evaluate_compensation(
        cls,
        policy: CompensationPolicy,
        offered_min: Optional[Decimal],
        offered_max: Optional[Decimal],
        offered_currency: Optional[str] = "USD",
        offered_unit: Optional[CompensationUnit] = CompensationUnit.ANNUAL,
        exchange_rate: Optional[Decimal] = None,
        rate_source: Optional[str] = None,
    ) -> tuple[CompensationMatchStatus, Optional[Decimal], str]:
        """Evaluates offered compensation against candidate policy.

        Returns:
            (status, annualized_offered_min, explanation)
        """
        # 1. Handle Undisclosed Compensation
        if offered_min is None and offered_max is None:
            if policy.undisclosed_handling == UndisclosedSalaryHandling.EXCLUDE:
                return (
                    CompensationMatchStatus.COMPENSATION_UNKNOWN,
                    None,
                    "Salary is undisclosed and candidate policy excludes positions without transparent compensation.",
                )
            elif policy.undisclosed_handling == UndisclosedSalaryHandling.REQUIRE_REVIEW:
                return (
                    CompensationMatchStatus.COMPENSATION_UNKNOWN,
                    None,
                    "Salary is undisclosed; requires human review per candidate policy.",
                )
            else:
                return (
                    CompensationMatchStatus.COMPENSATION_UNKNOWN,
                    None,
                    "Salary is undisclosed; permitted to proceed under candidate policy.",
                )

        # 2. Currency Compatibility Check
        offered_curr = (offered_currency or "USD").upper()
        policy_curr = policy.currency.upper()

        if offered_curr != policy_curr:
            if exchange_rate is None or exchange_rate <= 0:
                return (
                    CompensationMatchStatus.NOT_COMPARABLE,
                    None,
                    f"Compensation offered in {offered_curr} but policy requires {policy_curr}. No verified exchange rate available; automatic conversion refused.",
                )

        # 3. Annualization
        unit = offered_unit or CompensationUnit.ANNUAL
        annual_min = cls.annualize_amount(
            offered_min if offered_min is not None else offered_max,  # type: ignore
            unit=unit,
            hours_per_week=policy.hours_per_week_assumption,
            weeks_per_year=policy.weeks_per_year_assumption,
        )

        # Apply exchange rate if cross-currency
        if offered_curr != policy_curr and exchange_rate is not None:
            annual_min = (annual_min * exchange_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # 4. Compare with Policy Thresholds
        if annual_min < policy.min_acceptable_amount:
            return (
                CompensationMatchStatus.BELOW_MINIMUM,
                annual_min,
                f"Offered annualized compensation {policy_curr} {annual_min:,.2f} is below minimum acceptable {policy_curr} {policy.min_acceptable_amount:,.2f}.",
            )

        if annual_min < policy.preferred_min:
            return (
                CompensationMatchStatus.MEETS_MINIMUM,
                annual_min,
                f"Offered {policy_curr} {annual_min:,.2f} meets minimum threshold ({policy_curr} {policy.min_acceptable_amount:,.2f}) but is below preferred target ({policy_curr} {policy.preferred_min:,.2f}).",
            )

        if policy.preferred_max and annual_min > policy.preferred_max:
            return (
                CompensationMatchStatus.ABOVE_PREFERRED_RANGE,
                annual_min,
                f"Offered {policy_curr} {annual_min:,.2f} exceeds target preferred range ({policy_curr} {policy.preferred_max:,.2f}).",
            )

        return (
            CompensationMatchStatus.WITHIN_PREFERRED_RANGE,
            annual_min,
            f"Offered {policy_curr} {annual_min:,.2f} is within preferred range ({policy_curr} {policy.preferred_min:,.2f} - {policy.preferred_max or 'unlimited'}).",
        )
