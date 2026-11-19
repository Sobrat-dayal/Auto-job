"""Responsibility and deliverable extraction separating duties from candidate prerequisites."""

import re

from app.recruitment.intelligence.preprocessing.segmentation import JobSection

ACTION_VERB_PATTERN = re.compile(
    r"^(?:•|\*|-)?\s*(?:build|design|develop|architect|lead|maintain|collaborate|implement|deliver|manage|optimize|create|scale|support|test|drive|partner)\b",
    re.IGNORECASE,
)


def extract_responsibilities(sections: list[JobSection]) -> list[str]:
    """Extract day-to-day role responsibilities and deliverables."""
    responsibilities: list[str] = []

    resp_sections = [s for s in sections if s.name == "RESPONSIBILITIES"]
    for sec in resp_sections:
        for line in sec.lines:
            line_str = line.strip()
            # Clean leading bullet markers
            cleaned = re.sub(r"^[•\*\-\d\.]+\s*", "", line_str).strip()
            if cleaned and len(cleaned) > 15:
                responsibilities.append(cleaned)

    if not responsibilities:
        # Fallback: search for action verb bullets across general sections
        for sec in sections:
            if sec.name in ("MINIMUM_QUALIFICATIONS", "PREFERRED_QUALIFICATIONS", "COMPENSATION", "BENEFITS", "EEO_LEGAL"):
                continue
            for line in sec.lines:
                line_str = line.strip()
                if ACTION_VERB_PATTERN.match(line_str):
                    cleaned = re.sub(r"^[•\*\-\d\.]+\s*", "", line_str).strip()
                    if cleaned and len(cleaned) > 15:
                        responsibilities.append(cleaned)

    return responsibilities
