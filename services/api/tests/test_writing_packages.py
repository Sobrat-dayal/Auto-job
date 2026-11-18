"""Unit Tests for Application Writing Packages Assembly & Consistency Validation (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.profile.contracts import ApplicantProfile, ContactInfo
from app.recruitment.writing.contracts import (
    ApplicationAnswer,
    ApplicationQuestionRecord,
    ApplicationQuestionSet,
    CoverLetterContentBlock,
    CoverLetterDocument,
    WritingPackageStatus,
)
from app.recruitment.writing.errors import PackageNotReadyError
from app.recruitment.writing.packages.manager import WritingPackageManager


def test_writing_package_lifecycle():
    mgr = WritingPackageManager()
    profile = ApplicantProfile(contact=ContactInfo(legal_name="Alex Mercer"))

    pkg = mgr.create_package(
        target_job_title="Senior Platform Engineer",
        target_employer="Datadog",
        profile_snapshot_id="snap_01",
        resume_id="res_01",
        cover_letter_id="cl_01",
        question_set_id="qset_01",
    )
    assert pkg.status == WritingPackageStatus.CREATED
    assert not pkg.is_ready_for_approval

    cl = CoverLetterDocument(
        id="cl_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Cover Letter",
        target_role="Senior Platform Engineer",
        employer_name="Datadog",
        blocks=[
            CoverLetterContentBlock(
                block_type="opening",
                text="I am writing to express my interest in Datadog.",
            )
        ],
    )

    qset = ApplicationQuestionSet(
        id="qset_01",
        job_title="Senior Platform Engineer",
        employer="Datadog",
        title="Screening Questions",
        questions=[
            ApplicationQuestionRecord(
                id="q1",
                set_id="qset_01",
                exact_question_text="Are you willing to work hybrid?",
                normalized_question="are you willing to work hybrid",
                is_required=True,
                current_answer=ApplicationAnswer(
                    question_id="q1",
                    profile_id="prof_01",
                    profile_version=1,
                    answer_text="Yes, I am comfortable with hybrid work.",
                ),
            )
        ],
    )

    # 1. Validate package
    val = mgr.validate_package(pkg, profile, cover_letter=cl, question_set=qset)
    assert val["is_ready"] is True
    assert val["answered_questions"] == 1
    assert val["pending_attestations"] == 0

    # 2. Approve package
    approved = mgr.approve_package(pkg.id, actor_id="user_admin")
    assert approved.status == WritingPackageStatus.APPROVED
    assert approved.approved_at is not None


def test_package_approval_blocked_by_pending_attestation():
    mgr = WritingPackageManager()
    profile = ApplicantProfile(contact=ContactInfo(legal_name="Alex Mercer"))

    pkg = mgr.create_package(
        target_job_title="Site Reliability Engineer",
        target_employer="Google",
        profile_snapshot_id="snap_02",
        question_set_id="qset_02",
    )

    # Question set with pending attestation
    qset = ApplicationQuestionSet(
        id="qset_02",
        job_title="Site Reliability Engineer",
        employer="Google",
        title="Screening Questions",
        questions=[
            ApplicationQuestionRecord(
                id="q_att",
                set_id="qset_02",
                exact_question_text="I certify that all statements are true.",
                normalized_question="i certify that all statements are true",
                requires_attestation=True,
                current_answer=None,  # Not attested!
            )
        ],
    )

    mgr.validate_package(pkg, profile, question_set=qset)
    assert not pkg.is_ready_for_approval

    with pytest.raises(PackageNotReadyError):
        mgr.approve_package(pkg.id)
