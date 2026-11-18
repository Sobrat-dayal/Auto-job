"""Unit tests for Stage 21 Document Import Pipeline, DocumentParser, and CandidateExtractor."""

import json
import pytest

from app.recruitment.profile.contracts import (
    ApplicantProfile,
    CandidateStatus,
    ClaimCategory,
    SkillCategory,
    SkillItem,
)
from app.recruitment.profile.errors import InvalidDocumentError
from app.recruitment.profile.import_pipeline.extractor import CandidateExtractor
from app.recruitment.profile.import_pipeline.parser import DocumentParser, ParsedDocument


def test_document_parser_txt():
    sample_text = b"John Doe\njohn.doe@example.com\nSenior Python Engineer with 6 years experience in FastAPI and Docker."
    text, sha, meta = DocumentParser.parse_bytes(sample_text, "resume.txt")

    assert "John Doe" in text
    assert "john.doe@example.com" in text
    assert len(sha) == 64
    assert meta["extension"] == ".txt"
    assert meta["size_bytes"] == len(sample_text)


def test_document_parser_json():
    data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "skills": ["Rust", "Kubernetes", "PostgreSQL"],
    }
    json_bytes = json.dumps(data).encode("utf-8")
    text, sha, meta = DocumentParser.parse_bytes(json_bytes, "profile.json")

    assert "Jane Smith" in text
    assert meta["extension"] == ".json"
    assert "json_keys" in meta
    assert "skills" in meta["json_keys"]


def test_document_parser_invalid_extension():
    with pytest.raises(InvalidDocumentError, match="Unsupported file extension"):
        DocumentParser.parse_bytes(b"some binary data", "malicious.exe")


def test_document_parser_empty_file():
    with pytest.raises(InvalidDocumentError, match="is empty"):
        DocumentParser.parse_bytes(b"", "empty.txt")


@pytest.mark.asyncio
async def test_candidate_extractor_heuristics():
    raw_resume = """
    Jane Doe
    jane.doe@company.org
    +1 (555) 019-4820
    https://linkedin.com/in/janedoe
    https://github.com/janedoe

    EDUCATION:
    Stanford University, Bachelor of Science in Computer Science, 2016 - 2020

    EXPERIENCE:
    Acme Software Corp - Senior Backend Engineer (2020 - Present)
    Architected high-throughput message brokers in Python, Go, and Kafka.

    SKILLS:
    Python, Go, Docker, Kubernetes, AWS, PostgreSQL, React, TypeScript
    """

    profile = ApplicantProfile(
        id="prof_1",
        owner_id="u_1",
        display_label="Jane Doe Profile",
        status="active",
        version=1,
    )

    candidates = await CandidateExtractor.extract(raw_resume, "imp_1", profile)
    assert len(candidates) > 0

    # Verify contact extraction
    email_cand = next((c for c in candidates if c.field_name == "contact.primary_email"), None)
    assert email_cand is not None
    assert email_cand.proposed_value == "jane.doe@company.org"

    # Verify skills extraction
    skill_names = [c.proposed_value.get("name") for c in candidates if c.category == ClaimCategory.SKILL and isinstance(c.proposed_value, dict)]
    assert "Python" in skill_names
    assert "Docker" in skill_names

    # Verify education extraction
    edu_cands = [c for c in candidates if c.category == ClaimCategory.DEGREE]
    assert len(edu_cands) >= 1
    assert "stanford" in edu_cands[0].proposed_value.get("institution", "").lower()


@pytest.mark.asyncio
async def test_duplicate_detection_in_candidate_extractor():
    raw_text = "Experienced in Python and Docker."
    profile = ApplicantProfile(
        id="prof_1",
        owner_id="u_1",
        display_label="Existing Profile",
        status="active",
        version=1,
        skills=[
            SkillItem(id="sk_1", name="Python", canonical_name="python", category=SkillCategory.PROGRAMMING_LANGUAGES)
        ],
    )

    candidates = await CandidateExtractor.extract(raw_text, "imp_2", profile)

    python_cand = next(
        (c for c in candidates if isinstance(c.proposed_value, dict) and c.proposed_value.get("canonical_name") == "python"),
        None,
    )
    assert python_cand is not None
    assert python_cand.is_duplicate is True
    assert python_cand.status == CandidateStatus.REJECTED  # Automatically rejected duplicate
