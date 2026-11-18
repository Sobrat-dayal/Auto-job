"""Unit Tests for Reusable Answer Library, Parameterized Templates & Freshness (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    ProjectRecord,
    SkillCategory,
    SkillItem,
    VerificationStatus,
)
from app.recruitment.writing.answer_library.manager import AnswerLibraryManager
from app.recruitment.writing.contracts import AnswerType, QuestionCategory


@pytest.fixture
def library_mgr() -> AnswerLibraryManager:
    return AnswerLibraryManager()


@pytest.fixture
def profile_with_skills() -> ApplicantProfile:
    return ApplicantProfile(
        contact=ContactInfo(legal_name="Alex Mercer"),
        skills=[
            SkillItem(
                name="Python",
                canonical_name="python",
                category=SkillCategory.PROGRAMMING_LANGUAGES,
                verification_status=VerificationStatus.USER_CONFIRMED,
            )
        ],
        projects=[
            ProjectRecord(
                title="Distributed Cache",
                description="In-memory cache",
                applicant_contribution="implementing LRU eviction algorithms",
            )
        ],
    )


def test_answer_library_listing_and_creation(library_mgr: AnswerLibraryManager):
    entries = library_mgr.list_entries()
    assert len(entries) >= 3

    new_entry = library_mgr.create_entry(
        title="Custom Technical Architecture",
        category=QuestionCategory.TECHNICAL,
        parameterized_template="I architected {project} using {technology}, focusing on {contribution}.",
        sample_resolved_text="Sample text",
        applicable_technologies=["Python"],
    )
    assert new_entry.id.startswith("lib_")
    assert new_entry.title == "Custom Technical Architecture"
    assert library_mgr.get_entry(new_entry.id).id == new_entry.id


def test_answer_library_parameter_resolution(
    library_mgr: AnswerLibraryManager,
    profile_with_skills: ApplicantProfile,
):
    entry = library_mgr.get_entry("lib_tech_exp_01")
    params = {
        "technology": "Python",
        "project": "Cloud Event Ingestion",
        "contribution": "high-throughput partitioning",
    }
    resolved = library_mgr.resolve_template(entry, params, profile=profile_with_skills)
    assert "Python" in resolved
    assert "Cloud Event Ingestion" in resolved
    assert "high-throughput partitioning" in resolved
    assert "{" not in resolved and "}" not in resolved


def test_answer_library_freshness_detection(
    library_mgr: AnswerLibraryManager,
    profile_with_skills: ApplicantProfile,
):
    # Create an entry with an unverified technology
    library_mgr.create_entry(
        title="Kubernetes Experience",
        category=QuestionCategory.TECHNICAL,
        parameterized_template="My Kubernetes experience includes cluster management.",
        sample_resolved_text="Sample",
        applicable_technologies=["Kubernetes"],  # Not in profile_with_skills!
    )

    check = library_mgr.check_freshness(profile_with_skills)
    assert check["outdated_count"] >= 1
