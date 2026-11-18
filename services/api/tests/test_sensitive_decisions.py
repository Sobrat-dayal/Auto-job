"""Unit Tests for Sensitive Decisions & Legal Attestation Protection Guards (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    EmploymentEligibility,
)
from app.recruitment.writing.answers.generation import AnswerGenerator
from app.recruitment.writing.answers.validation import AnswerValidator
from app.recruitment.writing.contracts import (
    AnswerState,
    AnswerType,
    ApplicationQuestionRecord,
    QuestionCategory,
)
from app.recruitment.writing.sensitive.guards import SensitiveDecisionGuard


def test_attestation_guard_blocks_auto_approval():
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="I certify that all statements in this application are accurate and true.",
        normalized_question="i certify that all statements in this application are accurate and true",
        category=QuestionCategory.ATTESTATION,
        answer_type=AnswerType.BOOLEAN,
        requires_attestation=True,
    )
    profile = ApplicantProfile(contact=ContactInfo(legal_name="Alex Mercer"))

    # 1. Answer Generator creates un-attested draft
    ans = AnswerGenerator.generate_answer(q, profile)
    assert ans.state == AnswerState.REQUIRES_USER_ATTESTATION
    assert ans.user_attestation_timestamp is None

    # 2. Validator rejects un-attested answer
    val = AnswerValidator.validate_answer(ans, q)
    assert not val["is_valid"]
    assert any("attestation" in iss.lower() for iss in val["issues"])

    # 3. Explicit human attestation accepts
    ans_attested = SensitiveDecisionGuard.apply_user_attestation(ans, actor_id="user_admin", accepted=True)
    assert ans_attested.user_attestation_timestamp is not None
    assert ans_attested.user_attestation_actor == "user_admin"
    assert ans_attested.boolean_value is True

    # 4. Validator now passes
    val2 = AnswerValidator.validate_answer(ans_attested, q)
    assert val2["is_valid"]


def test_work_eligibility_unconfirmed_requires_review():
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="Are you authorized to work in the United States?",
        normalized_question="are you authorized to work in the united states",
        category=QuestionCategory.WORK_ELIGIBILITY,
        answer_type=AnswerType.BOOLEAN,
        is_sensitive=True,
    )

    # Profile without confirmed eligibility
    profile = ApplicantProfile(
        contact=ContactInfo(legal_name="Alex Mercer"),
        eligibility=None,
    )

    ans = AnswerGenerator.generate_answer(q, profile)
    assert ans.state == AnswerState.REQUIRES_USER_CONFIRMATION
    assert ans.answer_text == ""
    assert any("confirmation" in iss.lower() for iss in ans.validation_issues)


def test_voluntary_disclosure_is_protected():
    q = ApplicationQuestionRecord(
        set_id="qset_01",
        exact_question_text="Voluntary self-identification of disability status",
        normalized_question="voluntary self-identification of disability status",
        category=QuestionCategory.SENSITIVE_DISCLOSURE,
        answer_type=AnswerType.SINGLE_CHOICE,
        is_sensitive=True,
        allowed_options=["Yes", "No", "Prefer not to answer"],
    )
    profile = ApplicantProfile(contact=ContactInfo(legal_name="Alex Mercer"))

    ans = AnswerGenerator.generate_answer(q, profile)
    assert ans.state == AnswerState.SENSITIVE_OPTIONAL
    assert ans.answer_text == ""
