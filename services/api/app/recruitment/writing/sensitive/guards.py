"""Sensitive Decisions & Legal Attestation Protection Guards (Stage 24)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4
from app.recruitment.writing.contracts import (
    ApplicationAnswer,
    ApplicationQuestionRecord,
    QuestionCategory,
    SensitiveDecisionItem,
)
from app.recruitment.writing.errors import (
    AttestationRequiredError,
    SensitiveDecisionRequiredError,
)

logger = logging.getLogger("autonom.recruitment.writing.sensitive.guards")


class SensitiveDecisionGuard:
    """Enforces zero-auto-approval guards for work eligibility, protected disclosures, and legal certifications."""

    @classmethod
    def evaluate_question_sensitivity(
        cls,
        question: ApplicationQuestionRecord,
    ) -> Optional[SensitiveDecisionItem]:
        """Identifies sensitive questions requiring explicit human user review and election."""
        lower_q = question.exact_question_text.lower()

        if question.category == QuestionCategory.ATTESTATION or question.requires_attestation:
            return SensitiveDecisionItem(
                id=f"sns_att_{uuid4().hex[:6]}",
                question_id=question.id,
                question_text=question.exact_question_text,
                category="legal_attestation",
                allowed_choices=["I certify and agree", "Decline / Leave blank"],
                is_voluntary=False,
            )

        if question.category == QuestionCategory.WORK_ELIGIBILITY:
            is_sponsorship = "sponsorship" in lower_q
            return SensitiveDecisionItem(
                id=f"sns_wrk_{uuid4().hex[:6]}",
                question_id=question.id,
                question_text=question.exact_question_text,
                category="visa_sponsorship" if is_sponsorship else "work_authorization",
                allowed_choices=["Yes", "No"],
                is_voluntary=False,
            )

        if question.category == QuestionCategory.COMPENSATION:
            return SensitiveDecisionItem(
                id=f"sns_cmp_{uuid4().hex[:6]}",
                question_id=question.id,
                question_text=question.exact_question_text,
                category="compensation_expectation",
                allowed_choices=["Enter preferred salary range", "Negotiable / Standard market rate", "Decline to state"],
                is_voluntary=True,
            )

        if question.category == QuestionCategory.SENSITIVE_DISCLOSURE:
            return SensitiveDecisionItem(
                id=f"sns_dsc_{uuid4().hex[:6]}",
                question_id=question.id,
                question_text=question.exact_question_text,
                category="voluntary_disclosure",
                allowed_choices=question.allowed_options or ["Prefer not to answer", "Disclose voluntarily"],
                is_voluntary=True,
            )

        return None

    @classmethod
    def apply_user_attestation(
        cls,
        answer: ApplicationAnswer,
        actor_id: str,
        accepted: bool = True,
    ) -> ApplicationAnswer:
        """Applies explicit human user attestation to a legal certification question."""
        if not accepted:
            answer.user_attestation_timestamp = None
            answer.user_attestation_actor = None
            answer.answer_text = "Declined to certify"
            answer.boolean_value = False
            return answer

        answer.user_attestation_timestamp = datetime.now(UTC)
        answer.user_attestation_actor = actor_id
        answer.answer_text = "I certify that all statements provided in this application are true, complete, and accurate."
        answer.boolean_value = True
        answer.validation_issues = [iss for iss in answer.validation_issues if "attestation" not in iss.lower()]
        logger.info(f"User '{actor_id}' attested question '{answer.question_id}' at {answer.user_attestation_timestamp}")
        return answer
