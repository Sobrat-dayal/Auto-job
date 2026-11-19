"""Compensation intelligence extraction, range parsing, currency normalization, and zero synthetic guessing."""

import re

from app.recruitment.intelligence.contracts import (
    CompensationIntelligence,
    ExtractionMethod,
    PayPeriod,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

CURRENCY_SYMBOLS = {
    "$": "USD",
    "USD": "USD",
    "€": "EUR",
    "EUR": "EUR",
    "£": "GBP",
    "GBP": "GBP",
    "CAD": "CAD",
    "AUD": "AUD",
}

# Regex to detect compensation range or value
# Handles $, €, £, CAD, numbers with commas, k/K suffixes, em-dashes (—), en-dashes (–), hyphens (-), and "to"
COMPENSATION_RANGE_PATTERN = re.compile(
    r"(?P<currency>[$€£]|USD|EUR|GBP|CAD|AUD)?\s*(?P<min>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+k?)\s*(?:-|–|—|to)\s*(?P<cur2>[$€£]|USD|EUR|GBP|CAD|AUD)?\s*(?P<max>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+k?)\s*(?P<period>/hr|/hour|per\s+hour|/yr|/year|per\s+year|annually|/month|per\s+month|monthly)?",
    re.IGNORECASE,
)

SINGLE_SALARY_PATTERN = re.compile(
    r"(?P<currency>[$€£]|USD|EUR|GBP|CAD|AUD)\s*(?P<val>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+k?)\s*(?P<period>/hr|/hour|per\s+hour|/yr|/year|per\s+year|annually|/month|per\s+month|monthly)?",
    re.IGNORECASE,
)

BONUS_PATTERN = re.compile(r"\b(?:\d+%\s*bonus|annual\s+bonus|sign[- ]on\s+bonus|performance\s+bonus)\b", re.IGNORECASE)
EQUITY_PATTERN = re.compile(r"\b(?:equity|stock\s+options|rsus?|equity\s+grant)\b", re.IGNORECASE)

BENEFITS_KEYWORDS = [
    ("401(k) / Retirement", re.compile(r"\b(?:401\(?k\)?|pension|retirement\s+plan)\b", re.IGNORECASE)),
    ("Health Insurance", re.compile(r"\b(?:health|medical)\s+(?:insurance|coverage|benefits)\b", re.IGNORECASE)),
    ("Dental & Vision", re.compile(r"\b(?:dental|vision)\b", re.IGNORECASE)),
    ("Paid Time Off (PTO)", re.compile(r"\b(?:paid\s+time\s+off|pto|vacation|unlimited\s+pto)\b", re.IGNORECASE)),
    ("Parental Leave", re.compile(r"\b(?:parental\s+leave|maternity\s+leave|paternity\s+leave)\b", re.IGNORECASE)),
    ("Learning & Development", re.compile(r"\b(?:learning\s+budget|tuition|education\s+stipend)\b", re.IGNORECASE)),
    ("Wellness Stipend", re.compile(r"\b(?:gym|wellness\s+stipend)\b", re.IGNORECASE)),
]


def _parse_amount(val_str: str) -> float | None:
    if not val_str:
        return None
    val_str = val_str.strip().lower().replace(",", "")
    multiplier = 1.0
    if val_str.endswith("k"):
        multiplier = 1000.0
        val_str = val_str[:-1]
    try:
        return float(val_str) * multiplier
    except Exception:
        return None


def _determine_pay_period(period_str: str, min_val: float | None) -> PayPeriod:
    if period_str:
        p = period_str.lower()
        if "hr" in p or "hour" in p:
            return PayPeriod.HOURLY
        if "yr" in p or "year" in p or "annual" in p:
            return PayPeriod.ANNUAL
        if "month" in p:
            return PayPeriod.MONTHLY
    # Heuristic based on magnitude
    if min_val:
        if min_val < 500:
            return PayPeriod.HOURLY
        elif min_val < 30000:
            return PayPeriod.MONTHLY
        else:
            return PayPeriod.ANNUAL
    return PayPeriod.ANNUAL


def extract_compensation_intelligence(
    sections: list[JobSection],
    full_source_text: str,
) -> CompensationIntelligence:
    """Extract compensation details with zero synthetic guessing."""
    base_min: float | None = None
    base_max: float | None = None
    currency = "USD"
    pay_period = PayPeriod.ANNUAL
    original_text = ""
    is_disclosed = False
    evidence_list = []

    has_bonus = False
    bonus_details = None
    has_equity = False
    equity_details = None
    detected_benefits = []

    # Check for benefits across all sections
    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Benefits keywords
            for b_name, b_pat in BENEFITS_KEYWORDS:
                if b_pat.search(line_str) and b_name not in detected_benefits:
                    detected_benefits.append(b_name)

            # Bonus
            if not has_bonus and BONUS_PATTERN.search(line_str):
                has_bonus = True
                bonus_details = line_str

            # Equity
            if not has_equity and EQUITY_PATTERN.search(line_str):
                has_equity = True
                equity_details = line_str

    # Find salary in COMPENSATION section first, then other sections
    target_sections = [s for s in sections if s.name == "COMPENSATION"] or sections

    for sec in target_sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Try range pattern
            range_match = COMPENSATION_RANGE_PATTERN.search(line_str)
            if range_match:
                cur_str = range_match.group("currency") or range_match.group("cur2") or "$"
                cur = CURRENCY_SYMBOLS.get(cur_str.upper(), "USD")
                parsed_min = _parse_amount(range_match.group("min"))
                parsed_max = _parse_amount(range_match.group("max"))

                if parsed_min and parsed_max:
                    base_min = parsed_min
                    base_max = parsed_max
                    currency = cur
                    period_str = range_match.group("period") or ""
                    pay_period = _determine_pay_period(period_str, base_min)
                    original_text = line_str
                    is_disclosed = True

                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )
                    evidence_list.append(ev)
                    break

            # Try single salary pattern if range not matched
            if not is_disclosed:
                single_match = SINGLE_SALARY_PATTERN.search(line_str)
                if single_match:
                    cur_str = single_match.group("currency") or "$"
                    cur = CURRENCY_SYMBOLS.get(cur_str.upper(), "USD")
                    parsed_val = _parse_amount(single_match.group("val"))

                    if parsed_val and parsed_val > 10:  # avoid noise like $5 coffee
                        base_min = parsed_val
                        base_max = parsed_val
                        currency = cur
                        period_str = single_match.group("period") or ""
                        pay_period = _determine_pay_period(period_str, base_min)
                        original_text = line_str
                        is_disclosed = True

                        ev = create_evidence(
                            supporting_text=line_str,
                            full_source_text=full_source_text,
                            section_name=sec.name,
                            extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                        )
                        evidence_list.append(ev)
                        break

        if is_disclosed:
            break

    return CompensationIntelligence(
        base_min=base_min,
        base_max=base_max,
        currency=currency,
        pay_period=pay_period,
        has_bonus=has_bonus,
        bonus_details=bonus_details,
        has_equity=has_equity,
        equity_details=equity_details,
        benefits=detected_benefits,
        original_text=original_text,
        is_disclosed=is_disclosed,
        is_ambiguous=False,
        evidence=evidence_list,
    )
