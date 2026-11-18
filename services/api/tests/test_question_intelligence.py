"""Unit Tests for Application Question Parsing, Classification & Intent Analysis (Stage 24)."""

from __future__ import annotations

import pytest
from app.recruitment.writing.contracts import AnswerType, QuestionCategory
from app.recruitment.writing.questions.classification import QuestionClassifier
from app.recruitment.writing.questions.parsing import QuestionParser


def test_question_classifier_categories():
    # 1. Attestation
    cat, ans_type, sensitive, attestation = QuestionClassifier.classify(
        "I certify that all statements in this application are accurate and true."
    )
    assert cat == QuestionCategory.ATTESTATION
    assert attestation is True

    # 2. Work Eligibility
    cat, ans_type, sensitive, attestation = QuestionClassifier.classify(
        "Are you legally authorized to work in the country of employment without visa sponsorship?"
    )
    assert cat == QuestionCategory.WORK_ELIGIBILITY
    assert ans_type == AnswerType.BOOLEAN
    assert sensitive is True
    assert attestation is False

    # 3. Numeric Experience
    cat, ans_type, sensitive, attestation = QuestionClassifier.classify(
        "How many years of professional experience do you have with Python?"
    )
    assert cat == QuestionCategory.EXPERIENCE
    assert ans_type == AnswerType.NUMERIC

    # 4. Projects
    cat, ans_type, sensitive, attestation = QuestionClassifier.classify(
        "Describe a relevant project where you built a backend service and deployed it."
    )
    assert cat == QuestionCategory.PROJECTS
    assert ans_type == AnswerType.PARAGRAPH

    # 5. Compensation
    cat, ans_type, sensitive, attestation = QuestionClassifier.classify(
        "What is your expected salary range for this role?"
    )
    assert cat == QuestionCategory.COMPENSATION
    assert sensitive is True


def test_question_parser_extracts_constraints():
    raw_form = """
    1. What is your highest completed qualification?
    2. When do you expect to graduate? (YYYY-MM)
    3. How many years of Python experience do you have? (max 50 chars)
    4. Are you authorized to work in the United States? (Yes/No)
    5. Which of the following technologies have you used?
    [ ] Python
    [ ] Docker
    [ ] Kubernetes
    6. I certify that all information submitted is true and complete.
    """
    records = QuestionParser.parse_raw_text(raw_form, set_id="qset_test")
    assert len(records) >= 6

    # Q3 constraint check
    q3 = next(r for r in records if "how many years" in r.exact_question_text.lower())
    assert q3.max_characters == 50
    assert q3.answer_type == AnswerType.NUMERIC

    # Q4 boolean check
    q4 = next(r for r in records if "authorized to work" in r.exact_question_text.lower())
    assert q4.answer_type == AnswerType.BOOLEAN
    assert q4.is_sensitive is True

    # Q5 multiple choice check
    q5 = next(r for r in records if "technologies have you used" in r.exact_question_text.lower())
    assert len(q5.allowed_options) == 3
    assert "Python" in q5.allowed_options

    # Q6 attestation check
    q6 = next(r for r in records if "certify" in r.exact_question_text.lower())
    assert q6.requires_attestation is True
