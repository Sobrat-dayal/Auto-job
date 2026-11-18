"""Unit Tests for Recruitment Writing & Application Intelligence Models (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.writing.contracts import (
    AnswerFreshnessStatus,
    AnswerState,
    AnswerType,
    ApplicationAnswer,
    ApplicationQuestionRecord,
    ApplicationQuestionSet,
    ApplicationWritingPackage,
    CoverLetterContentBlock,
    CoverLetterDocument,
    CoverLetterType,
    QuestionCategory,
    WritingDocumentStatus,
    WritingLength,
    WritingPackageStatus,
    WritingTone,
)


def test_cover_letter_document_instantiation():
    doc = CoverLetterDocument(
        owner_id="user_test",
        profile_id="prof_123",
        profile_snapshot_id="snap_123",
        title="Software Engineer Letter",
        letter_type=CoverLetterType.ROLE_SPECIFIC,
        target_role="Software Engineer",
        employer_name="Acme Corp",
        tone=WritingTone.PROFESSIONAL,
        length_preference=WritingLength.STANDARD,
        blocks=[
            CoverLetterContentBlock(
                block_type="opening",
                text="I am writing to express my interest in the Software Engineer position.",
                ordering=0,
                word_count=12,
            )
        ],
    )
    assert doc.id.startswith("cl_")
    assert doc.status == WritingDocumentStatus.DRAFT
    assert len(doc.blocks) == 1
    assert doc.blocks[0].word_count == 12


def test_application_question_and_answer_contracts():
    question = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="How many years of Python experience do you have?",
        normalized_question="how many years of python experience do you have",
        category=QuestionCategory.EXPERIENCE,
        answer_type=AnswerType.NUMERIC,
        is_required=True,
    )
    assert question.id.startswith("qst_")
    assert question.answer_type == AnswerType.NUMERIC

    answer = ApplicationAnswer(
        question_id=question.id,
        profile_id="prof_123",
        profile_version=1,
        answer_text="3.5 years",
        numeric_value=3.5,
        state=AnswerState.AVAILABLE_CONFIRMED,
        freshness_status=AnswerFreshnessStatus.FRESH,
    )
    assert answer.numeric_value == 3.5
    assert answer.state == AnswerState.AVAILABLE_CONFIRMED
    assert not answer.is_user_overridden


def test_writing_package_contract():
    pkg = ApplicationWritingPackage(
        owner_id="user_test",
        target_job_title="Backend Engineer",
        target_employer="GlobalTech",
        profile_snapshot_id="snap_01",
        status=WritingPackageStatus.CREATED,
    )
    assert pkg.id.startswith("pkg_")
    assert pkg.status == WritingPackageStatus.CREATED
    assert not pkg.is_ready_for_approval
