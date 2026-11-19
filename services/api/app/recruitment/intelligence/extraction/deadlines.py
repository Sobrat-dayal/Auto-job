"""Application deadlines, instructions, and required document extraction."""

from datetime import UTC, datetime
import re

from app.recruitment.intelligence.contracts import (
    ApplicationInstructions,
    ExtractionMethod,
)
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

ROLLING_PATTERN = re.compile(
    r"\b(?:rolling\s+basis|open\s+until\s+filled|reviewed\s+as\s+received|ongoing\s+review)\b",
    re.IGNORECASE,
)

DEADLINE_PATTERN = re.compile(
    r"\b(?:deadline|applications?\s+close|closing\s+date|apply\s+by)[:\s]+([A-Za-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})\b",
    re.IGNORECASE,
)

DOCUMENT_KEYWORDS = [
    ("Resume / CV", re.compile(r"\b(?:resume|cv|curriculum\s+vitae)\b", re.IGNORECASE)),
    ("Cover Letter", re.compile(r"\bcover\s+letter\b", re.IGNORECASE)),
    ("Portfolio / GitHub", re.compile(r"\b(?:portfolio|github\s+link|work\s+samples)\b", re.IGNORECASE)),
    ("Academic Transcript", re.compile(r"\b(?:transcripts?|academic\s+records)\b", re.IGNORECASE)),
    ("References", re.compile(r"\b(?:references|recommendation\s+letters)\b", re.IGNORECASE)),
]


def _parse_date_string(date_str: str) -> datetime | None:
    for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def extract_application_instructions(
    sections: list[JobSection],
    full_source_text: str,
    application_url: str = "",
) -> ApplicationInstructions:
    """Extract closing deadlines, rolling review status, and document requirements."""
    is_rolling = False
    deadline_utc: datetime | None = None
    required_docs: list[str] = []
    instructions_text = ""
    evidence_list = []

    # Check for document requirements across sections
    for sec in sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            for doc_name, d_pat in DOCUMENT_KEYWORDS:
                if d_pat.search(line_str) and doc_name not in required_docs:
                    required_docs.append(doc_name)

    # Check for deadlines and instructions
    target_sections = [s for s in sections if s.name in ("HOW_TO_APPLY", "GENERAL", "ABOUT_ROLE")] or sections

    for sec in target_sections:
        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            if ROLLING_PATTERN.search(line_str):
                is_rolling = True
                ev = create_evidence(
                    supporting_text=line_str,
                    full_source_text=full_source_text,
                    section_name=sec.name,
                    extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                )
                evidence_list.append(ev)

            d_match = DEADLINE_PATTERN.search(line_str)
            if d_match:
                parsed_dt = _parse_date_string(d_match.group(1).strip())
                if parsed_dt:
                    deadline_utc = parsed_dt
                    instructions_text = line_str
                    ev = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )
                    evidence_list.append(ev)

    return ApplicationInstructions(
        deadline_utc=deadline_utc,
        is_rolling=is_rolling,
        application_url=application_url,
        required_documents=required_docs,
        instructions_text=instructions_text,
        evidence=evidence_list,
    )
