"""Safe compensation extraction without guessing or synthetic currency inference (Stage 26)."""

import re
from typing import Optional
from app.recruitment.discovery.contracts import ExtractedCompensation

CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "CAD": "CAD",
    "AUD": "AUD",
}

SALARY_REGEX = re.compile(
    r"([$€£₹]|USD|CAD|EUR|GBP)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:-|to|–|—)\s*([$€£₹]|USD|CAD|EUR|GBP)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:(per\s+year|\/yr|annually|\/hr|per\s+hour|\/mo|per\s+month))?",
    re.IGNORECASE,
)

SINGLE_SALARY_REGEX = re.compile(
    r"([$€£₹]|USD|CAD|EUR|GBP)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:(per\s+year|\/yr|annually|\/hr|per\s+hour|\/mo|per\s+month))?",
    re.IGNORECASE,
)


def extract_compensation(text: Optional[str]) -> Optional[ExtractedCompensation]:
    """Parse salary range from text if explicitly published; returns None when absent."""
    if not text or not isinstance(text, str):
        return None

    clean_text = text.strip()

    # 1. Check range match ($120,000 - $160,000 /yr)
    range_match = SALARY_REGEX.search(clean_text)
    if range_match:
        curr_prefix1, min_str, curr_prefix2, max_str, period_str = range_match.groups()
        curr_raw = curr_prefix1 or curr_prefix2 or "USD"
        currency = CURRENCY_SYMBOLS.get(curr_raw, curr_raw)

        try:
            min_val = float(min_str.replace(",", ""))
            max_val = float(max_str.replace(",", ""))
        except ValueError:
            return None

        unit = "annual"
        if period_str:
            p_lower = period_str.lower()
            if "hr" in p_lower or "hour" in p_lower:
                unit = "hourly"
            elif "mo" in p_lower or "month" in p_lower:
                unit = "monthly"

        return ExtractedCompensation(
            min_amount=min_val,
            max_amount=max_val,
            currency=currency,
            unit=unit,
            pay_period=period_str or ("year" if unit == "annual" else unit),
            raw_text=range_match.group(0),
        )

    # 2. Check single figure ($140,000 /yr)
    single_match = SINGLE_SALARY_REGEX.search(clean_text)
    if single_match:
        curr_raw, amount_str, period_str = single_match.groups()
        currency = CURRENCY_SYMBOLS.get(curr_raw, curr_raw)
        try:
            amount_val = float(amount_str.replace(",", ""))
        except ValueError:
            return None

        unit = "annual"
        if period_str:
            p_lower = period_str.lower()
            if "hr" in p_lower or "hour" in p_lower:
                unit = "hourly"
            elif "mo" in p_lower or "month" in p_lower:
                unit = "monthly"

        return ExtractedCompensation(
            min_amount=amount_val,
            max_amount=amount_val,
            currency=currency,
            unit=unit,
            pay_period=period_str or ("year" if unit == "annual" else unit),
            raw_text=single_match.group(0),
        )

    return None
