"""Unit tests for Stage 21 Claim Registry, provenance tracking, and conflict resolution."""

import pytest

from app.recruitment.profile.claims.registry import ClaimRegistry
from app.recruitment.profile.contracts import (
    ApplicantClaim,
    ClaimCategory,
    VerificationStatus,
)
from app.recruitment.profile.errors import ClaimNotFoundError, ConflictResolutionError


def test_register_and_retrieve_claim():
    registry = ClaimRegistry()
    claim = ApplicantClaim(
        claim_id="clm_1",
        profile_id="prof_1",
        category=ClaimCategory.SKILL,
        normalized_value="Skill: Python (5 years)",
        original_text="Python for 5 years",
        source_category="document_extracted",
    )
    registered = registry.register_claim(claim)
    assert registered.claim_id == "clm_1"
    assert registered.verification_status == VerificationStatus.USER_REPORTED

    retrieved = registry.get_claim("clm_1")
    assert retrieved is not None
    assert retrieved.claim_id == "clm_1"


def test_claim_confirmation_and_rejection():
    registry = ClaimRegistry()
    claim = ApplicantClaim(
        claim_id="clm_edu_1",
        profile_id="prof_1",
        category=ClaimCategory.DEGREE,
        normalized_value="Degree: BS CS from MIT",
        original_text="BS in Computer Science from MIT",
    )
    registry.register_claim(claim)
    confirmed = registry.confirm_claim("clm_edu_1")
    assert confirmed.verification_status == VerificationStatus.USER_CONFIRMED

    claim2 = ApplicantClaim(
        claim_id="clm_sk_cobol",
        profile_id="prof_1",
        category=ClaimCategory.SKILL,
        normalized_value="Skill: COBOL",
        original_text="COBOL experience",
    )
    registry.register_claim(claim2)
    rejected = registry.reject_claim("clm_sk_cobol")
    assert rejected.verification_status == VerificationStatus.REJECTED


def test_conflict_detection_and_resolution():
    registry = ClaimRegistry()
    claim_a = ApplicantClaim(
        claim_id="clm_a",
        profile_id="prof_1",
        category=ClaimCategory.DEGREE,
        normalized_value="Degree: BS in CS from MIT (2016-2020)",
        original_text="BS in CS, MIT",
        source_ref="resume_v1.pdf",
    )
    claim_b = ApplicantClaim(
        claim_id="clm_b",
        profile_id="prof_1",
        category=ClaimCategory.DEGREE,
        normalized_value="Degree: MS in CS from MIT (2016-2020)",
        original_text="MS in CS, MIT",
        source_ref="resume_v1.pdf",
    )
    registry.register_claim(claim_a)
    registry.register_claim(claim_b)

    conflicts = registry.detect_conflicts("prof_1")
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.claim_id_a == "clm_a"
    assert conflict.claim_id_b == "clm_b"

    resolved = registry.resolve_conflict(conflict.conflict_id, "clm_a")
    assert resolved.resolution_status == "resolved"
    assert resolved.resolved_claim_id == "clm_a"
    assert registry.get_claim("clm_a").verification_status == VerificationStatus.USER_CONFIRMED
    assert registry.get_claim("clm_b").verification_status == VerificationStatus.REJECTED
