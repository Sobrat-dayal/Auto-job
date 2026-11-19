"""Work authorization, visa sponsorship, citizenship restrictions, and security clearances."""

import re

from app.recruitment.intelligence.contracts import (
    EligibilityConditions,
    ExtractionMethod,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

AUTH_REQUIRED_PATTERNS = [
    re.compile(
        r"\b(?:legally\s+authorized\s+to\s+work|valid\s+(?:u\.?s\.?\s+)?work\s+authorization|eligible\s+to\s+work|must\s+have\s+(?:valid\s+)?(?:u\.?s\.?\s+)?work\s+authorization|right\s+to\s+work|work\s+authorization\s+required)\b",
        re.IGNORECASE,
    ),
]

SPONSORSHIP_REFUSED_PATTERNS = [
    re.compile(
        r"\b(?:sponsorship\s+(?:is\s+)?unavailable|no\s+visa\s+sponsorship|unable\s+to\s+sponsor|will\s+not\s+sponsor|cannot\s+sponsor\s+visas?|without\s+need\s+for\s+sponsorship)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bnot\s+offering\s+sponsorship\b",
        re.IGNORECASE,
    ),
]

SPONSORSHIP_OFFERED_PATTERNS = [
    re.compile(
        r"\b(?:visa\s+sponsorship\s+(?:is\s+)?available|we\s+sponsor\s+visas?|h[- ]?1b\s+sponsorship\s+available|sponsorship\s+offered)\b",
        re.IGNORECASE,
    )
]

CITIZENSHIP_PATTERNS = [
    ("US_CITIZEN_ONLY", re.compile(r"\bu\.?s\.?\s+citizenship\s+(?:is\s+)?required\b", re.IGNORECASE)),
    ("US_PERSON", re.compile(r"\bu\.?s\.?\s+person\s+(?:status|required)\b", re.IGNORECASE)),
]

CLEARANCE_PATTERNS = [
    re.compile(r"\b(?:active\s+)?(?:secret|top\s+secret|ts/sci|public\s+trust)\s+(?:clearance|security\s+clearance)\b", re.IGNORECASE),
    re.compile(r"\bability\s+to\s+obtain\s+(?:a\s+)?security\s+clearance\b", re.IGNORECASE),
]


def extract_eligibility_conditions(
    sections: list[JobSection],
    full_source_text: str,
) -> EligibilityConditions:
    """Extract work authorization, visa sponsorship, citizenship, and clearance details."""
    work_auth_required = False
    sponsorship_offered: bool | None = None
    sponsorship_refused: bool | None = None
    citizenship_restrictions: list[str] = []
    clearance_required: str | None = None
    evidence_list = []

    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check work authorization required
            for p in AUTH_REQUIRED_PATTERNS:
                if p.search(line_str):
                    work_auth_required = True
                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )
                    evidence_list.append(ev)
                    break

            # Check sponsorship refused
            for p in SPONSORSHIP_REFUSED_PATTERNS:
                if p.search(line_str):
                    sponsorship_refused = True
                    sponsorship_offered = False
                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )
                    evidence_list.append(ev)
                    break

            # Check sponsorship offered (if not refused)
            if sponsorship_refused is not True:
                for p in SPONSORSHIP_OFFERED_PATTERNS:
                    if p.search(line_str):
                        sponsorship_offered = True
                        sponsorship_refused = False
                        ev = create_evidence(
                            supporting_text=line_str,
                            full_source_text=full_source_text,
                            section_name=sec.name,
                            extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                        )
                        evidence_list.append(ev)
                        break

            # Check citizenship
            for code, p in CITIZENSHIP_PATTERNS:
                if p.search(line_str) and code not in citizenship_restrictions:
                    citizenship_restrictions.append(code)
                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )
                    evidence_list.append(ev)

            # Check clearance
            if clearance_required is None:
                for p in CLEARANCE_PATTERNS:
                    m = p.search(line_str)
                    if m:
                        clearance_required = m.group(0)
                        ev = create_evidence(
                            supporting_text=line_str,
                            full_source_text=full_source_text,
                            section_name=sec.name,
                            extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                        )
                        evidence_list.append(ev)
                        break

    return EligibilityConditions(
        work_authorization_required=work_auth_required,
        visa_sponsorship_offered=sponsorship_offered,
        visa_sponsorship_refused=sponsorship_refused,
        citizenship_restrictions=citizenship_restrictions,
        security_clearance_required=clearance_required,
        is_ambiguous=False,
        evidence=evidence_list,
    )
