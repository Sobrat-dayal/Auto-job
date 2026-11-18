"""Deterministic Answer Validation Engine (Stage 24)."""

from __future__ import annotations

import logging
import re
from typing import Any
from app.recruitment.writing.contracts import (
    AnswerState,
    AnswerType,
    ApplicationAnswer,
    ApplicationQuestionRecord,
)

logger = logging.getLogger("autonom.recruitment.writing.answers.validation")


class AnswerValidator:
    """Performs deterministic validation on candidate answers against question constraints."""

    @classmethod
    def validate_answer(
        cls,
        answer: ApplicationAnswer,
        question: ApplicationQuestionRecord,
    ) -> dict[str, Any]:
        issues: list[str] = []

        # 1. Attestation Validation
        if question.requires_attestation:
            if not answer.user_attestation_timestamp:
                issues.append("Question requires explicit human user attestation; cannot be submitted or approved automatically.")

        # 2. Required Field Check
        if question.is_required:
            if not answer.answer_text.strip() and answer.boolean_value is None and answer.numeric_value is None and not answer.selected_options:
                issues.append("Question is mandatory but no answer value was provided.")

        # 3. Character Limit Validation
        if question.max_characters and answer.answer_text:
            char_count = len(answer.answer_text)
            if char_count > question.max_characters:
                issues.append(f"Answer exceeds character limit ({char_count} / {question.max_characters} max characters).")

        # 4. Word Limit Validation
        if question.max_words and answer.answer_text:
            word_count = len(answer.answer_text.split())
            if word_count > question.max_words:
                issues.append(f"Answer exceeds word limit ({word_count} / {question.max_words} max words).")

        # 5. Allowed Options Validation (for Single Choice, Multi Choice, Dropdown)
        if question.answer_type in (AnswerType.SINGLE_CHOICE, AnswerType.MULTIPLE_CHOICE, AnswerType.DROPDOWN) and question.allowed_options:
            allowed_set = {opt.lower().strip() for opt in question.allowed_options}
            for sel in answer.selected_options:
                if sel.lower().strip() not in allowed_set:
                    issues.append(f"Selected option '{sel}' is not an allowed choice for this question.")

        # 6. Numeric Value Validation
        if question.answer_type == AnswerType.NUMERIC:
            if answer.numeric_value is not None:
                if question.min_numeric_value is not None and answer.numeric_value < question.min_numeric_value:
                    issues.append(f"Numeric value {answer.numeric_value} is below the minimum allowed ({question.min_numeric_value}).")
                if question.max_numeric_value is not None and answer.numeric_value > question.max_numeric_value:
                    issues.append(f"Numeric value {answer.numeric_value} exceeds the maximum allowed ({question.max_numeric_value}).")

        # 7. Date Format Validation
        if question.answer_type == AnswerType.DATE:
            if answer.date_value:
                clean_date = answer.date_value.strip()
                if not re.match(r"^\d{4}(?:-\d{2})?(?:-\d{2})?$", clean_date):
                    issues.append(f"Date '{clean_date}' is not in a recognized ISO format (YYYY, YYYY-MM, or YYYY-MM-DD).")

        is_valid = len(issues) == 0
        return {
            "is_valid": is_valid,
            "issues": issues,
            "character_count": len(answer.answer_text),
            "word_count": len(answer.answer_text.split()),
        }
