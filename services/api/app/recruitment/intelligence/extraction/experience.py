"""Experience requirements and duration extraction."""

import re

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    EvidenceConfidence,
    ExperienceRequirement,
    ExtractionMethod,
    QualificationType,
    RequirementCategory,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

EXPERIENCE_RANGE_PATTERN = re.compile(
    r"\b(?:minimum\s+of\s+|at\s+least\s+)?(\d+)(?:\s*(?:to|-|–|—)\s*(\d+))?\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?(?:[^\.\n;,]{0,60}?)\b(?:experience|work\s+experience)\b",
    re.IGNORECASE,
)

NO_EXP_PATTERN = re.compile(
    r"\b(?:no\s+(?:prior|previous)?\s*(?:professional\s+)?experience\s+(?:is\s+)?required|entry[- ]level|no\s+experience\s+necessary)\b",
    re.IGNORECASE,
)

DOMAINS = [
    ("Backend Development", re.compile(r"\bbackend\b", re.IGNORECASE)),
    ("Frontend Development", re.compile(r"\bfrontend\b", re.IGNORECASE)),
    ("Full-Stack Development", re.compile(r"\bfull[- ]?stack\b", re.IGNORECASE)),
    ("Distributed Systems", re.compile(r"\bdistributed\s+systems\b", re.IGNORECASE)),
    ("Machine Learning", re.compile(r"\bmachine\s+learning|ai\b", re.IGNORECASE)),
    ("Cloud Architecture", re.compile(r"\bcloud(?:\s+infrastructure|\s+architecture)?\b", re.IGNORECASE)),
    ("DevOps & SRE", re.compile(r"\bdevops|sre|site\s+reliability\b", re.IGNORECASE)),
    ("Software Development", re.compile(r"\bsoftware\s+(?:engineering|development)\b", re.IGNORECASE)),
]


def extract_experience_requirements(
    sections: list[JobSection],
    full_source_text: str,
) -> tuple[list[ExperienceRequirement], list[AtomicRequirement]]:
    """Extract experience duration and domain requirements from job sections."""
    experience_reqs: list[ExperienceRequirement] = []
    atomic_reqs: list[AtomicRequirement] = []

    # Check for entry level / no experience required
    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue
            if NO_EXP_PATTERN.search(line_str):
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                exp = ExperienceRequirement(
                    minimum_years=0.0,
                    maximum_years=0.0,
                    domain_categories=["Entry-Level"],
                    is_mandatory=False,
                    raw_text=line_str,
                    evidence=[ev],
                )
                experience_reqs.append(exp)
                return experience_reqs, atomic_reqs

    seen_spans: set[str] = set()

    for sec in sections:
        is_mandatory = sec.name == "MINIMUM_QUALIFICATIONS"

        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            match = EXPERIENCE_RANGE_PATTERN.search(line_str)
            if match:
                raw_min = match.group(1)
                raw_max = match.group(2)
                try:
                    min_years = float(raw_min)
                except Exception:
                    min_years = None
                try:
                    max_years = float(raw_max) if raw_max else None
                except Exception:
                    max_years = None

                # Extract domains
                domains = [name for name, d_pat in DOMAINS if d_pat.search(line_str)]
                if not domains:
                    domains = ["Software Engineering"]

                span_key = f"{min_years}-{max_years}-{':'.join(domains)}"
                if span_key in seen_spans:
                    continue
                seen_spans.add(span_key)

                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )

                exp_req = ExperienceRequirement(
                    minimum_years=min_years,
                    maximum_years=max_years,
                    domain_categories=domains,
                    is_mandatory=is_mandatory,
                    raw_text=line_str,
                    evidence=[ev],
                )
                experience_reqs.append(exp_req)

                atomic = AtomicRequirement(
                    category=RequirementCategory.MANDATORY if is_mandatory else RequirementCategory.PREFERRED,
                    qualification_type=QualificationType.EXPERIENCE,
                    name=f"{min_years}+ Years Experience" if min_years else "Experience Requirement",
                    normalized_value=f"exp_{int(min_years or 0)}y",
                    raw_text=line_str,
                    min_years=min_years,
                    max_years=max_years,
                    confidence=EvidenceConfidence.EXPLICIT_VERIFIED_SOURCE
                    if ev.verified_in_source
                    else EvidenceConfidence.STRONGLY_SUPPORTED,
                    confidence_score=1.0 if ev.verified_in_source else 0.8,
                    evidence=[ev],
                )
                ev.requirement_id = atomic.id
                atomic_reqs.append(atomic)

    return experience_reqs, atomic_reqs
