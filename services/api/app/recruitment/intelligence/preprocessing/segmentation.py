"""Job description segmentation into structural sections."""

import re
from dataclasses import dataclass


@dataclass
class JobSection:
    name: str  # e.g. MINIMUM_QUALIFICATIONS, PREFERRED_QUALIFICATIONS, RESPONSIBILITIES
    header_text: str
    body_text: str
    start_char: int
    end_char: int
    lines: list[str]


SECTION_PATTERNS = [
    (
        "MINIMUM_QUALIFICATIONS",
        re.compile(
            r"^(?:#+\s*)?(?:minimum|basic|required|mandatory|core)?\s*(?:qualifications|requirements|what you(?:'ll| will)? bring|must have|who you are|what we(?:'re| are) looking for|skills required|qualifications required)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "PREFERRED_QUALIFICATIONS",
        re.compile(
            r"^(?:#+\s*)?(?:preferred|desired|bonus|nice to have|additional|preferred qualifications|what gives you an edge|bonus points|preferred requirements|pluses|good to have)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "RESPONSIBILITIES",
        re.compile(
            r"^(?:#+\s*)?(?:responsibilities|duties|what you(?:'ll| will)? do|the role|about the role|your mission|key responsibilities|what you will be doing|day-to-day|role overview)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "COMPENSATION",
        re.compile(
            r"^(?:#+\s*)?(?:compensation|salary|salary range|pay range|total rewards|remuneration|wage)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "BENEFITS",
        re.compile(
            r"^(?:#+\s*)?(?:benefits|perks|what we offer|employee benefits|our offer)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "HOW_TO_APPLY",
        re.compile(
            r"^(?:#+\s*)?(?:how to apply|application process|next steps|application deadline|to apply)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
    (
        "EEO_LEGAL",
        re.compile(
            r"^(?:#+\s*)?(?:equal (?:opportunity|employment)|diversity|eeo|accommodations|legal notices|about us|company overview)[\s:]*$",
            re.IGNORECASE,
        ),
    ),
]


def segment_job_description(full_text: str) -> list[JobSection]:
    """Segment a clean job description into typed structural sections."""
    if not full_text:
        return []

    lines = full_text.splitlines()
    detected_headings: list[tuple[int, str, str]] = []  # (line_index, section_name, line_text)

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 100:
            continue

        for sec_name, pattern in SECTION_PATTERNS:
            if pattern.match(stripped):
                detected_headings.append((idx, sec_name, stripped))
                break

    if not detected_headings:
        # If no explicit headings found, treat entire text as ABOUT_ROLE / GENERAL
        return [
            JobSection(
                name="GENERAL",
                header_text="",
                body_text=full_text,
                start_char=0,
                end_char=len(full_text),
                lines=lines,
            )
        ]

    sections: list[JobSection] = []

    # If there is content before the first heading, treat it as ABOUT_ROLE
    first_idx, first_name, first_head = detected_headings[0]
    if first_idx > 0:
        pre_body_lines = lines[:first_idx]
        pre_body = "\n".join(pre_body_lines).strip()
        if pre_body:
            sections.append(
                JobSection(
                    name="ABOUT_ROLE",
                    header_text="Overview",
                    body_text=pre_body,
                    start_char=0,
                    end_char=len(pre_body),
                    lines=pre_body_lines,
                )
            )

    # Segment between detected headings
    current_char = len(sections[0].body_text) + 1 if sections else 0

    for i, (line_idx, sec_name, header) in enumerate(detected_headings):
        next_line_idx = detected_headings[i + 1][0] if i + 1 < len(detected_headings) else len(lines)
        body_lines = lines[line_idx + 1 : next_line_idx]
        body_text = "\n".join(body_lines).strip()

        start_c = full_text.find(header, current_char)
        if start_c == -1:
            start_c = full_text.find(header)
        end_c = start_c + len(header) + len(body_text) + 1 if start_c != -1 else 0
        current_char = max(current_char, end_c)

        sections.append(
            JobSection(
                name=sec_name,
                header_text=header,
                body_text=body_text,
                start_char=max(0, start_c),
                end_char=max(0, end_c),
                lines=body_lines,
            )
        )

    return sections
