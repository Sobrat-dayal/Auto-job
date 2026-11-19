"""Employment conditions, workplace type, hybrid schedules, and travel requirements."""

import re

from app.recruitment.intelligence.contracts import (
    EmploymentConditions,
    EmploymentType,
    ExtractionMethod,
    WorkplaceType,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

REMOTE_GLOBAL_PATTERN = re.compile(
    r"\b(?:fully\s+remote|100%\s*remote|work\s+from\s+anywhere|remote\s+worldwide|global\s+remote)\b",
    re.IGNORECASE,
)

REMOTE_COUNTRY_PATTERN = re.compile(
    r"\b(?:remote\s*(?:\(|-)?\s*(?:us|usa|united\s+states|canada|uk|europe)\s*(?:only|\))?|remote\s+in\s+the\s+(?:us|united\s+states))\b",
    re.IGNORECASE,
)

REMOTE_GENERAL_PATTERN = re.compile(
    r"\b(?:remote\s+role|remote\s+position|work\s+remotely|remote)\b",
    re.IGNORECASE,
)

HYBRID_PATTERN = re.compile(
    r"\b(?:hybrid(?:\s+work|\s+role|\s+schedule|\s+model)?|(\d+)\s*days?\s*(?:in|per\s+week\s+in)\s*(?:the\s+)?office)\b",
    re.IGNORECASE,
)

ONSITE_PATTERN = re.compile(
    r"\b(?:on[- ]?site|in[- ]?person|office[- ]?based)\b",
    re.IGNORECASE,
)

TRAVEL_PATTERN = re.compile(
    r"\b(?:up\s+to\s+)?(\d+)%\s*(?:travel|business\s+travel)\b|\b(no\s+travel\s+required|minimal\s+travel)\b",
    re.IGNORECASE,
)

EMPLOYMENT_TYPE_PATTERNS = [
    (EmploymentType.FULL_TIME, re.compile(r"\bfull[- ]?time\b", re.IGNORECASE)),
    (EmploymentType.PART_TIME, re.compile(r"\bpart[- ]?time\b", re.IGNORECASE)),
    (EmploymentType.CONTRACT, re.compile(r"\bcontract(?:or)?\b", re.IGNORECASE)),
    (EmploymentType.INTERNSHIP, re.compile(r"\bintern(?:ship)?\b", re.IGNORECASE)),
]


def extract_employment_conditions(
    sections: list[JobSection],
    full_source_text: str,
) -> EmploymentConditions:
    """Extract workplace type, location, schedule, travel, and contract terms."""
    workplace = WorkplaceType.UNKNOWN
    office_days: int | None = None
    travel_pct: float | None = None
    emp_type = EmploymentType.UNKNOWN
    allowed_countries: list[str] = []
    evidence_list = []

    # Check sections for workplace details
    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check Hybrid
            h_match = HYBRID_PATTERN.search(line_str)
            if h_match and workplace == WorkplaceType.UNKNOWN:
                workplace = WorkplaceType.HYBRID
                if h_match.group(1):
                    try:
                        office_days = int(h_match.group(1))
                    except Exception:
                        office_days = 2
                else:
                    # Search specifically for days count
                    day_match = re.search(r"(\d+)\s*days?\s*(?:a\s+week|weekly|per\s+week|in\s+(?:the\s+)?office|on[- ]site)", line_str, re.IGNORECASE)
                    office_days = int(day_match.group(1)) if day_match else None
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)
                continue

            # Check Remote Country-only
            if REMOTE_COUNTRY_PATTERN.search(line_str) and workplace == WorkplaceType.UNKNOWN:
                workplace = WorkplaceType.REMOTE_COUNTRY_ONLY
                if re.search(r"\b(?:us|usa|united\s+states)\b", line_str, re.IGNORECASE):
                    allowed_countries.append("US")
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)
                continue

            # Check Remote Global
            if REMOTE_GLOBAL_PATTERN.search(line_str) and workplace == WorkplaceType.UNKNOWN:
                workplace = WorkplaceType.REMOTE_GLOBAL
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)
                continue

            # Check general remote
            if REMOTE_GENERAL_PATTERN.search(line_str) and workplace == WorkplaceType.UNKNOWN:
                workplace = WorkplaceType.REMOTE_GLOBAL
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)
                continue

            # Check Onsite
            if ONSITE_PATTERN.search(line_str) and workplace == WorkplaceType.UNKNOWN:
                workplace = WorkplaceType.ONSITE
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)

            # Check travel
            t_match = TRAVEL_PATTERN.search(line_str)
            if t_match and travel_pct is None:
                if t_match.group(1):
                    try:
                        travel_pct = float(t_match.group(1))
                    except Exception:
                        travel_pct = None
                elif t_match.group(2) and "no travel" in t_match.group(2).lower():
                    travel_pct = 0.0

            # Check employment type
            if emp_type == EmploymentType.UNKNOWN:
                for et, et_pat in EMPLOYMENT_TYPE_PATTERNS:
                    if et_pat.search(line_str):
                        emp_type = et
                        break

    return EmploymentConditions(
        workplace_type=workplace,
        allowed_countries=allowed_countries,
        office_days_per_week=office_days,
        travel_percentage=travel_pct,
        employment_type=emp_type,
        evidence=evidence_list,
    )
