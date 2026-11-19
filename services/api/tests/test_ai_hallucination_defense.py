"""Unit tests for AI hallucination defense and verbatim quote provenance (Section 119)."""

import pytest

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    EvidenceConfidence,
    RequirementCategory,
    RequirementEvidence,
)
from app.recruitment.intelligence.validation.hallucination_defense import verify_requirement_provenance


def test_hallucination_defense_detects_fake_quote():
    source_text = "We are seeking a Python engineer with Docker experience."

    # Hallucinated evidence: quote does NOT exist in source text
    fake_evidence = RequirementEvidence(
        supporting_text="10+ years of Kubernetes and Rust architecture",
        start_char=0,
        end_char=0,
    )
    fake_req = AtomicRequirement(
        name="Kubernetes",
        normalized_value="kubernetes",
        raw_text="10+ years of Kubernetes",
        category=RequirementCategory.MANDATORY,
        evidence=[fake_evidence],
    )

    is_valid, reason = verify_requirement_provenance(fake_req, source_text)
    assert is_valid is False
    assert fake_evidence.verified_in_source is False
    assert fake_req.confidence == EvidenceConfidence.WEAK_INFERENCE
    assert fake_req.needs_review is True


def test_hallucination_defense_accepts_verbatim_quote():
    source_text = "We are seeking a Python engineer with Docker experience."

    real_evidence = RequirementEvidence(
        supporting_text="Python engineer with Docker experience",
        start_char=0,
        end_char=0,
    )
    real_req = AtomicRequirement(
        name="Python",
        normalized_value="python",
        raw_text="Python engineer",
        category=RequirementCategory.MANDATORY,
        evidence=[real_evidence],
    )

    is_valid, reason = verify_requirement_provenance(real_req, source_text)
    assert is_valid is True
    assert real_evidence.verified_in_source is True
    assert real_evidence.start_char == 17
    assert real_evidence.end_char == 55
