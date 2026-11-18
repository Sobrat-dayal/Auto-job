"""Application Question Parser & Constraints Extractor (Stage 24)."""

from __future__ import annotations

import logging
import re
from typing import Optional
from uuid import uuid4
from app.recruitment.writing.contracts import (
    AnswerType,
    ApplicationQuestionRecord,
    QuestionCategory,
)
from app.recruitment.writing.questions.classification import QuestionClassifier

logger = logging.getLogger("autonom.recruitment.writing.questions.parsing")


class QuestionParser:
    """Parses raw screening questions from forms, text blocks, or lists into typed records."""

    @classmethod
    def parse_raw_text(
        cls,
        raw_text: str,
        set_id: str,
    ) -> list[ApplicationQuestionRecord]:
        records: list[ApplicationQuestionRecord] = []
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        current_q = ""
        current_options: list[str] = []

        for line in lines:
            # Check if line looks like a question start (e.g. "1. ...", "Q1: ...", or ends with "?")
            is_new_q = (
                re.match(r"^(?:\d+[\.\)]|Q\d+[:\.]|[-*•])\s+", line)
                or line.endswith("?")
                or (not current_q and len(line) > 5)
            )

            # Check if line looks like an option (e.g. "[ ] Python", "(A) Yes", "- Option")
            is_opt = bool(re.match(r"^(?:\[[ x]?\]|\([a-zA-Z0-9]\)|[a-zA-Z]\))\s+", line))

            if is_opt and current_q:
                opt_clean = re.sub(r"^(?:\[[ x]?\]|\([a-zA-Z0-9]\)|[a-zA-Z]\))\s*", "", line).strip()
                current_options.append(opt_clean)
            elif is_new_q:
                if current_q:
                    records.append(cls._build_record(current_q, current_options, set_id))
                    current_options = []
                # Clean prefix from question
                current_q = re.sub(r"^(?:\d+[\.\)]|Q\d+[:\.]|[-*•])\s*", "", line).strip()
            else:
                if current_q:
                    # Append continuation line to current question
                    current_q += " " + line

        if current_q:
            records.append(cls._build_record(current_q, current_options, set_id))

        return records

    @classmethod
    def parse_question_list(
        cls,
        questions: list[str],
        set_id: str,
    ) -> list[ApplicationQuestionRecord]:
        return [cls._build_record(q, [], set_id) for q in questions if q.strip()]

    @classmethod
    def _build_record(
        cls,
        question_text: str,
        options: list[str],
        set_id: str,
    ) -> ApplicationQuestionRecord:
        # 1. Extract constraints
        max_chars = None
        char_match = re.search(r"\(?(?:max(?:imum)?\.?\s*)?(\d+)\s*(?:chars?|characters?)\)?", question_text, re.IGNORECASE)
        if char_match:
            max_chars = int(char_match.group(1))

        max_words = None
        word_match = re.search(r"\(?(?:max(?:imum)?\.?\s*)?(\d+)\s*words?\)?", question_text, re.IGNORECASE)
        if word_match:
            max_words = int(word_match.group(1))

        is_required = not bool(re.search(r"\b(optional|voluntary|if applicable)\b", question_text, re.IGNORECASE))

        # 2. Classify
        cat, ans_type, is_sensitive, requires_attestation = QuestionClassifier.classify(question_text)

        # 3. Detect options inside question text if not parsed line-by-line
        if not options:
            # Check for inline options like (Yes/No) or [Option A, Option B]
            inline_match = re.search(r"\(([^)]+/[^)]+)\)", question_text)
            if inline_match:
                opts = [o.strip() for o in inline_match.group(1).split("/")]
                if len(opts) >= 2:
                    options = opts
                    if len(opts) == 2 and any(o.lower() in ("yes", "no") for o in opts):
                        ans_type = AnswerType.BOOLEAN
                    else:
                        ans_type = AnswerType.SINGLE_CHOICE

        if options and ans_type in (AnswerType.FREE_TEXT, AnswerType.SHORT_TEXT):
            ans_type = AnswerType.SINGLE_CHOICE

        norm_q = re.sub(r"[^\w\s]", "", question_text.lower()).strip()

        return ApplicationQuestionRecord(
            id=f"qst_{uuid4().hex[:8]}",
            set_id=set_id,
            exact_question_text=question_text,
            normalized_question=norm_q,
            category=cat,
            answer_type=ans_type,
            is_required=is_required,
            allowed_options=options,
            max_characters=max_chars,
            max_words=max_words,
            is_sensitive=is_sensitive,
            requires_attestation=requires_attestation,
        )
