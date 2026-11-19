"""Education requirement extraction, degree levels, fields of study, and equivalencies."""

import re

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    DegreeLevel,
    DegreeStatus,
    EducationRequirement,
    EvidenceConfidence,
    ExtractionMethod,
    QualificationType,
    RequirementCategory,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

DEGREE_PATTERNS: list[tuple[DegreeLevel, re.Pattern]] = [
    (
        DegreeLevel.DOCTORATE,
        re.compile(r"\b(?:ph\.?d|doctorate|doctoral\s+degree)\b", re.IGNORECASE),
    ),
    (
        DegreeLevel.MASTER,
        re.compile(r"\b(?:master(?:'s)?\s+degree|m\.?s\.?|m\.?sc\.?|mba|m\.?eng\.?)\b", re.IGNORECASE),
    ),
    (
        DegreeLevel.BACHELOR,
        re.compile(
            r"\b(?:bachelor(?:'s)?\s+degree|b\.?s\.?|b\.?sc\.?|b\.?a\.?|b\.?eng\.?|undergraduate\s+degree|4-year\s+degree)\b",
            re.IGNORECASE,
        ),
    ),
    (
        DegreeLevel.ASSOCIATE,
        re.compile(r"\b(?:associate(?:'s)?\s+degree|2-year\s+degree)\b", re.IGNORECASE),
    ),
    (
        DegreeLevel.HIGH_SCHOOL,
        re.compile(r"\b(?:high\s+school\s+diploma|ged|secondary\s+school)\b", re.IGNORECASE),
    ),
]

FIELDS_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Computer Science", re.compile(r"\bcomputer\s+science\b", re.IGNORECASE)),
    ("Software Engineering", re.compile(r"\bsoftware\s+engineering\b", re.IGNORECASE)),
    ("Data Science", re.compile(r"\bdata\s+science\b", re.IGNORECASE)),
    ("Information Technology", re.compile(r"\binformation\s+technology\b", re.IGNORECASE)),
    ("Electrical Engineering", re.compile(r"\belectrical\s+engineering\b", re.IGNORECASE)),
    ("Mathematics", re.compile(r"\bmathematics|math\b", re.IGNORECASE)),
    ("Statistics", re.compile(r"\bstatistics\b", re.IGNORECASE)),
    ("Physics", re.compile(r"\bphysics\b", re.IGNORECASE)),
]

NO_DEGREE_PATTERN = re.compile(
    r"\b(?:no\s+(?:degree|college|university)\s+(?:is\s+)?required|degree\s+not\s+required|without\s+a\s+degree)\b",
    re.IGNORECASE,
)

EQUIVALENT_EXPERIENCE_PATTERN = re.compile(
    r"\bor\s+(?:an?\s+)?equivalent\s+(?:practical|work|professional)?\s*experience\b",
    re.IGNORECASE,
)

EQUIVALENT_YEARS_PATTERN = re.compile(
    r"\bor\s+(\d+)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s*equivalent\s+experience\b",
    re.IGNORECASE,
)


def extract_education_requirements(
    sections: list[JobSection],
    full_source_text: str,
) -> tuple[list[EducationRequirement], list[AtomicRequirement]]:
    """Extract structured education requirements from job sections."""
    education_reqs: list[EducationRequirement] = []
    atomic_reqs: list[AtomicRequirement] = []

    # First check for explicit "No degree required"
    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue
            if NO_DEGREE_PATTERN.search(line_str):
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                edu = EducationRequirement(
                    degree_level=DegreeLevel.NOT_REQUIRED,
                    degree_status=DegreeStatus.NOT_REQUIRED,
                    is_mandatory=False,
                    raw_text=line_str,
                    evidence=[ev],
                )
                education_reqs.append(edu)
                return education_reqs, atomic_reqs

    seen_levels: set[DegreeLevel] = set()

    for sec in sections:
        is_mandatory_section = sec.name == "MINIMUM_QUALIFICATIONS"

        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            for level, pattern in DEGREE_PATTERNS:
                if pattern.search(line_str):
                    if level in seen_levels:
                        continue
                    seen_levels.add(level)

                    # Extract fields of study
                    fields: list[str] = []
                    for field_name, f_pat in FIELDS_PATTERNS:
                        if f_pat.search(line_str):
                            fields.append(field_name)

                    # Extract alternative experience
                    alt_years = None
                    alt_match = EQUIVALENT_YEARS_PATTERN.search(line_str)
                    if alt_match:
                        try:
                            alt_years = float(alt_match.group(1))
                        except Exception:
                            alt_years = None
                    elif EQUIVALENT_EXPERIENCE_PATTERN.search(line_str):
                        alt_years = 4.0 if level == DegreeLevel.BACHELOR else 2.0

                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )

                    edu_req = EducationRequirement(
                        degree_level=level,
                        fields_of_study=fields,
                        degree_status=DegreeStatus.COMPLETED,
                        alternative_experience_years=alt_years,
                        is_mandatory=is_mandatory_section,
                        raw_text=line_str,
                        evidence=[ev],
                    )
                    education_reqs.append(edu_req)

                    atomic = AtomicRequirement(
                        category=RequirementCategory.MANDATORY
                        if is_mandatory_section
                        else RequirementCategory.PREFERRED,
                        qualification_type=QualificationType.EDUCATION,
                        name=f"{level.value.replace('_', ' ').title()} Degree",
                        normalized_value=level.value,
                        raw_text=line_str,
                        confidence=EvidenceConfidence.EXPLICIT_VERIFIED_SOURCE
                        if ev.verified_in_source
                        else EvidenceConfidence.STRONGLY_SUPPORTED,
                        confidence_score=1.0 if ev.verified_in_source else 0.8,
                        evidence=[ev],
                    )
                    ev.requirement_id = atomic.id
                    atomic_reqs.append(atomic)

    return education_reqs, atomic_reqs
