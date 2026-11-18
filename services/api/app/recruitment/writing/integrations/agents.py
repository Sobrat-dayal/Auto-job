"""Recruitment Specialist Agent Adapters & Multi-Agent Capabilities (Stage 24)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.writing.contracts import (
    ApplicationAnswer,
    ApplicationQuestionRecord,
    CoverLetterDocument,
    CoverLetterType,
    WritingDocumentStatus,
    WritingTone,
)
from app.recruitment.writing.cover_letters.generation import CoverLetterGenerator
from app.recruitment.writing.cover_letters.validation import CoverLetterValidator
from app.recruitment.writing.service import writing_service

logger = logging.getLogger("autonom.recruitment.writing.integrations.agents")


class WritingAgentAdapter:
    """Provides high-level actions for Supervisor and Specialist Recruitment Agents."""

    @classmethod
    def generate_cover_letter_for_agent(
        cls,
        profile: ApplicantProfile,
        target_role: str,
        employer_name: Optional[str] = None,
        job_description_raw: Optional[str] = None,
        letter_type: CoverLetterType = CoverLetterType.ROLE_SPECIFIC,
        tone: WritingTone = WritingTone.PROFESSIONAL,
    ) -> CoverLetterDocument:
        """Called by Recruitment Writing Agent to synthesize a grounded cover letter."""
        blocks = CoverLetterGenerator.generate_blocks(
            profile=profile,
            target_role=target_role,
            letter_type=letter_type,
            employer_name=employer_name,
            job_description_raw=job_description_raw,
            tone=tone,
        )

        doc = CoverLetterDocument(
            profile_id=profile.id,
            profile_snapshot_id=f"snap_{profile.version}",
            title=f"Cover Letter - {target_role} ({employer_name or 'Company'})",
            letter_type=letter_type,
            target_role=target_role,
            employer_name=employer_name,
            job_description_raw=job_description_raw,
            blocks=blocks,
            status=WritingDocumentStatus.DRAFT,
        )
        writing_service._cover_letters[doc.id] = doc
        return doc

    @classmethod
    def verify_document_for_agent(
        cls,
        doc: CoverLetterDocument,
        profile: ApplicantProfile,
    ) -> dict[str, Any]:
        """Called by Verification Agent to ensure zero hallucination and complete grounding."""
        return CoverLetterValidator.validate_cover_letter(doc, profile)

    @classmethod
    def answer_screening_questions_for_agent(
        cls,
        set_id: str,
        profile: ApplicantProfile,
    ) -> dict[str, Any]:
        """Called by Application Agent to prepare answers for form completion."""
        qset = writing_service.generate_answers_for_set(set_id, profile_id=profile.id)
        ready_answers = [q.current_answer for q in qset.questions if q.current_answer and q.current_answer.answer_text]
        sensitive_count = sum(1 for q in qset.questions if q.is_sensitive or q.requires_attestation)

        return {
            "set_id": set_id,
            "total_questions": len(qset.questions),
            "answered_count": len(ready_answers),
            "pending_sensitive_count": sensitive_count,
            "is_complete": len(ready_answers) == len(qset.questions) and sensitive_count == 0,
        }
