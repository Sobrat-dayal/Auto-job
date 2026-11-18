"""Master Recruitment Writing & Application Intelligence Service (Stage 24)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4
from app.core.security import AuthContext
from app.recruitment.profile.contracts import (
    AcademicStatus,
    ApplicantProfile,
)
from app.recruitment.profile.service import applicant_profile_service
from app.recruitment.writing.answer_library.manager import AnswerLibraryManager
from app.recruitment.writing.answers.generation import AnswerGenerator
from app.recruitment.writing.answers.validation import AnswerValidator
from app.recruitment.writing.contracts import (
    AnswerType,
    ApplicationAnswer,
    ApplicationQuestionRecord,
    ApplicationQuestionSet,
    ApplicationWritingPackage,
    ConflictItem,
    CoverLetterContentBlock,
    CoverLetterCreateRequest,
    CoverLetterDocument,
    CoverLetterExportRequest,
    CoverLetterGenerateRequest,
    CoverLetterTemplateDefinition,
    CoverLetterType,
    CoverLetterUpdateRequest,
    CoverLetterVersionRecord,
    MissingInformationItem,
    ParagraphRewriteRequest,
    QuestionCategory,
    QuestionParseRequest,
    QuestionSetCreateRequest,
    SensitiveDecisionItem,
    UserAttestationRequest,
    WritingDocumentStatus,
    WritingLength,
    WritingOverviewStats,
    WritingPackageCreateRequest,
    WritingTone,
)
from app.recruitment.writing.cover_letters.exports import CoverLetterExportManager
from app.recruitment.writing.cover_letters.generation import CoverLetterGenerator
from app.recruitment.writing.cover_letters.templates import CoverLetterTemplateRegistry
from app.recruitment.writing.cover_letters.validation import CoverLetterValidator
from app.recruitment.writing.cover_letters.versions import CoverLetterVersionManager
from app.recruitment.writing.errors import (
    CoverLetterNotFoundError,
    QuestionNotFoundError,
    QuestionSetNotFoundError,
    WritingDomainError,
)
from app.recruitment.writing.packages.manager import WritingPackageManager
from app.recruitment.writing.questions.parsing import QuestionParser
from app.recruitment.writing.sensitive.guards import SensitiveDecisionGuard

logger = logging.getLogger("autonom.recruitment.writing.service")


class RecruitmentWritingService:
    """Master orchestrator for Cover Letter Generation, Application Question Intelligence,
    Answer Library, Sensitive Decisions, and Writing Packages."""

    def __init__(self) -> None:
        self.version_mgr = CoverLetterVersionManager()
        self.library_mgr = AnswerLibraryManager()
        self.package_mgr = WritingPackageManager()

        self._cover_letters: dict[str, CoverLetterDocument] = {}
        self._question_sets: dict[str, ApplicationQuestionSet] = {}
        self._init_samples()

    def _init_samples(self) -> None:
        """Seeds initial synthetic cover letter and screening questions for local testing."""
        sample_cl = CoverLetterDocument(
            id="cl_sample_01",
            owner_id="default_user",
            profile_id="prof_primary_applicant",
            profile_snapshot_id="snap_sample_01",
            title="Systems Engineer Cover Letter - TechGlobal",
            letter_type=CoverLetterType.ROLE_SPECIFIC,
            target_role="Systems Software Engineer",
            employer_name="TechGlobal Inc.",
            template_id="classic_professional",
            tone=WritingTone.PROFESSIONAL,
            length_preference=WritingLength.STANDARD,
            blocks=[
                CoverLetterContentBlock(
                    id="blk_sample_hdr",
                    block_type="header",
                    title="Header",
                    text="Alex Mercer\nalex.mercer@example.com | +1 (555) 234-5678 | San Francisco, CA",
                    ordering=0,
                    word_count=12,
                ),
                CoverLetterContentBlock(
                    id="blk_sample_sal",
                    block_type="salutation",
                    title="Salutation",
                    text="Dear Hiring Team at TechGlobal Inc.,",
                    ordering=1,
                    word_count=6,
                ),
                CoverLetterContentBlock(
                    id="blk_sample_opn",
                    block_type="opening",
                    title="Opening",
                    text="I am writing to express my strong interest in the Systems Software Engineer position at TechGlobal Inc. With verified technical foundations in Python, Rust, and distributed systems, I am confident in my ability to deliver immediate value to your platform architecture initiatives.",
                    ordering=2,
                    word_count=42,
                ),
                CoverLetterContentBlock(
                    id="blk_sample_cls",
                    block_type="closing",
                    title="Closing",
                    text="Thank you for your time and consideration. I welcome the opportunity to discuss how my technical background aligns with your team's objectives.",
                    ordering=3,
                    word_count=23,
                ),
                CoverLetterContentBlock(
                    id="blk_sample_sig",
                    block_type="signature",
                    title="Sign-off",
                    text="Sincerely,\nAlex Mercer",
                    ordering=4,
                    word_count=3,
                ),
            ],
            status=WritingDocumentStatus.DRAFT,
        )
        self._cover_letters[sample_cl.id] = sample_cl

        # Sample Question Set
        sample_qset = ApplicationQuestionSet(
            id="qset_sample_01",
            owner_id="default_user",
            job_title="Systems Software Engineer",
            employer="TechGlobal Inc.",
            title="TechGlobal Engineering Application Screening",
            questions=[
                ApplicationQuestionRecord(
                    id="qst_s1",
                    set_id="qset_sample_01",
                    exact_question_text="How many years of professional experience do you have with Python?",
                    normalized_question="how many years of professional experience do you have with python",
                    category=QuestionCategory.EXPERIENCE,
                    answer_type=AnswerType.NUMERIC,
                    is_required=True,
                ),
                ApplicationQuestionRecord(
                    id="qst_s2",
                    set_id="qset_sample_01",
                    exact_question_text="Describe a challenging technical project you implemented and the technologies used.",
                    normalized_question="describe a challenging technical project you implemented and the technologies used",
                    category=QuestionCategory.PROJECTS,
                    answer_type=AnswerType.PARAGRAPH,
                    is_required=True,
                ),
                ApplicationQuestionRecord(
                    id="qst_s3",
                    set_id="qset_sample_01",
                    exact_question_text="Are you legally authorized to work in the United States?",
                    normalized_question="are you legally authorized to work in the united states",
                    category=QuestionCategory.WORK_ELIGIBILITY,
                    answer_type=AnswerType.BOOLEAN,
                    is_required=True,
                    is_sensitive=True,
                ),
                ApplicationQuestionRecord(
                    id="qst_s4",
                    set_id="qset_sample_01",
                    exact_question_text="I certify that all information submitted in this application is true and complete.",
                    normalized_question="i certify that all information submitted in this application is true and complete",
                    category=QuestionCategory.ATTESTATION,
                    answer_type=AnswerType.BOOLEAN,
                    is_required=True,
                    requires_attestation=True,
                ),
            ],
        )
        self._question_sets[sample_qset.id] = sample_qset

    # =========================================================================
    # 1. Overview & Statistics
    # =========================================================================

    def get_overview_stats(self, owner_id: str = "default_user") -> WritingOverviewStats:
        user_cls = [c for c in self._cover_letters.values() if c.owner_id == owner_id]
        approved_cls = [c for c in user_cls if c.status == WritingDocumentStatus.APPROVED]

        user_qsets = [q for q in self._question_sets.values() if q.owner_id == owner_id]
        total_questions = sum(len(q.questions) for q in user_qsets)

        approved_answers = len([a for a in self.library_mgr.list_entries(owner_id) if a.state == "approved"])
        missing_count = len(self.get_missing_information(owner_id))
        sensitive_count = len(self.get_sensitive_decisions(owner_id))
        pkgs_count = len(self.package_mgr.list_packages(owner_id))

        return WritingOverviewStats(
            total_cover_letters=len(user_cls),
            approved_cover_letters=len(approved_cls),
            total_question_sets=len(user_qsets),
            total_screening_questions=total_questions,
            approved_library_answers=approved_answers,
            pending_reviews=missing_count + sensitive_count,
            missing_info_count=missing_count,
            sensitive_decisions_count=sensitive_count,
            writing_packages_count=pkgs_count,
        )

    # =========================================================================
    # 2. Cover Letter Management
    # =========================================================================

    def list_cover_letters(self, owner_id: str = "default_user") -> list[CoverLetterDocument]:
        return [c for c in self._cover_letters.values() if c.owner_id == owner_id]

    def get_cover_letter(self, letter_id: str) -> CoverLetterDocument:
        cl = self._cover_letters.get(letter_id)
        if not cl:
            raise CoverLetterNotFoundError(f"Cover letter '{letter_id}' not found.")
        return cl

    def create_cover_letter(
        self,
        req: CoverLetterCreateRequest,
        auth: Optional[AuthContext] = None,
    ) -> CoverLetterDocument:
        owner = auth.client_id if auth else "default_user"
        prof_id = req.profile_id or "prof_primary_applicant"

        # Load profile
        try:
            profile = applicant_profile_service.get_profile(prof_id, auth=auth)
        except Exception:
            profile = applicant_profile_service.get_primary_profile(auth=auth)

        # Generate initial grounded blocks
        blocks = CoverLetterGenerator.generate_blocks(
            profile=profile,
            target_role=req.target_role,
            letter_type=req.letter_type,
            employer_name=req.employer_name,
            job_description_raw=req.job_description_raw,
            tone=req.tone,
            length_preference=req.length_preference,
            max_words=req.max_words,
        )

        doc = CoverLetterDocument(
            id=f"cl_{uuid4().hex[:8]}",
            owner_id=owner,
            profile_id=profile.id,
            profile_snapshot_id=f"snap_{uuid4().hex[:8]}",
            resume_id=req.resume_id,
            title=req.title,
            letter_type=req.letter_type,
            target_role=req.target_role,
            employer_name=req.employer_name,
            job_description_raw=req.job_description_raw,
            template_id=req.template_id,
            tone=req.tone,
            length_preference=req.length_preference,
            max_words=req.max_words,
            recipient_name=req.recipient_name,
            recipient_title=req.recipient_title,
            recipient_organization=req.recipient_organization or req.employer_name,
            blocks=blocks,
            status=WritingDocumentStatus.DRAFT,
        )

        self._cover_letters[doc.id] = doc
        logger.info(f"Created CoverLetterDocument '{doc.id}' ('{doc.title}')")
        return doc

    def update_cover_letter(
        self,
        letter_id: str,
        req: CoverLetterUpdateRequest,
    ) -> CoverLetterDocument:
        doc = self.get_cover_letter(letter_id)
        if req.title is not None:
            doc.title = req.title
        if req.target_role is not None:
            doc.target_role = req.target_role
        if req.employer_name is not None:
            doc.employer_name = req.employer_name
        if req.template_id is not None:
            doc.template_id = req.template_id
        if req.tone is not None:
            doc.tone = req.tone
        if req.length_preference is not None:
            doc.length_preference = req.length_preference
        if req.max_words is not None:
            doc.max_words = req.max_words
        if req.recipient_name is not None:
            doc.recipient_name = req.recipient_name
        if req.recipient_title is not None:
            doc.recipient_title = req.recipient_title
        if req.recipient_organization is not None:
            doc.recipient_organization = req.recipient_organization
        if req.blocks is not None:
            doc.blocks = req.blocks

        doc.updated_at = datetime.now(UTC)
        return doc

    def delete_cover_letter(self, letter_id: str) -> None:
        if letter_id in self._cover_letters:
            del self._cover_letters[letter_id]

    def regenerate_cover_letter(
        self,
        letter_id: str,
        req: CoverLetterGenerateRequest,
    ) -> CoverLetterDocument:
        doc = self.get_cover_letter(letter_id)
        try:
            profile = applicant_profile_service.get_profile(doc.profile_id)
        except Exception:
            profile = applicant_profile_service.get_primary_profile()

        target_role = req.target_role or doc.target_role
        employer = req.employer_name or doc.employer_name
        tone = req.tone or doc.tone
        length_pref = req.length_preference or doc.length_preference
        max_words = req.max_words or doc.max_words
        job_raw = req.job_description_raw or doc.job_description_raw

        doc.blocks = CoverLetterGenerator.generate_blocks(
            profile=profile,
            target_role=target_role,
            letter_type=doc.letter_type,
            employer_name=employer,
            job_description_raw=job_raw,
            tone=tone,
            length_preference=length_pref,
            max_words=max_words,
        )
        doc.target_role = target_role
        doc.employer_name = employer
        doc.tone = tone
        doc.length_preference = length_pref
        doc.updated_at = datetime.now(UTC)
        return doc

    def rewrite_paragraph(
        self,
        letter_id: str,
        req: ParagraphRewriteRequest,
    ) -> CoverLetterDocument:
        doc = self.get_cover_letter(letter_id)
        block = next((b for b in doc.blocks if b.id == req.block_id), None)
        if not block:
            raise WritingDomainError(f"Block '{req.block_id}' not found in cover letter '{letter_id}'.")

        # Deterministic paragraph styling / adjustments
        instruction_lower = req.instruction.lower()
        if "concise" in instruction_lower:
            # Tighten sentences
            sentences = [s.strip() for s in block.text.split(".") if s.strip()]
            block.text = ". ".join(sentences[:2]) + "."
        elif "technical" in instruction_lower:
            block.text += " I place strong emphasis on rigorous unit testing, automated CI/CD pipelines, and defensive coding."
        elif "more enthusiastic" in instruction_lower or "friendly" in instruction_lower:
            block.text = block.text.replace("I am writing to", "I am very pleased to")

        block.is_user_edited = True
        block.word_count = len(block.text.split())
        doc.updated_at = datetime.now(UTC)
        return doc

    def validate_cover_letter(self, letter_id: str) -> dict[str, Any]:
        doc = self.get_cover_letter(letter_id)
        try:
            profile = applicant_profile_service.get_profile(doc.profile_id)
        except Exception:
            profile = applicant_profile_service.get_primary_profile()
        return CoverLetterValidator.validate_cover_letter(doc, profile)

    def approve_cover_letter(self, letter_id: str, actor_id: str = "default_user") -> CoverLetterVersionRecord:
        doc = self.get_cover_letter(letter_id)
        return self.version_mgr.snapshot_version(doc, actor_id=actor_id)

    def list_cover_letter_versions(self, letter_id: str) -> list[CoverLetterVersionRecord]:
        return self.version_mgr.list_versions(letter_id)

    def restore_cover_letter_version(self, letter_id: str, version_number: int) -> CoverLetterDocument:
        doc = self.get_cover_letter(letter_id)
        restored = self.version_mgr.restore_version(letter_id, version_number, doc)
        self._cover_letters[letter_id] = restored
        return restored

    def preview_cover_letter_html(self, letter_id: str) -> dict[str, str]:
        doc = self.get_cover_letter(letter_id)
        tpl = CoverLetterTemplateRegistry.get_template(doc.template_id)
        html = CoverLetterExportManager.render_html(doc, tpl)
        return {"cover_letter_id": letter_id, "html": html}

    def export_cover_letter(self, letter_id: str, req: CoverLetterExportRequest) -> dict[str, Any]:
        doc = self.get_cover_letter(letter_id)
        return CoverLetterExportManager.export(doc, req)

    # =========================================================================
    # 3. Application Questions & Answers
    # =========================================================================

    def list_question_sets(self, owner_id: str = "default_user") -> list[ApplicationQuestionSet]:
        return [q for q in self._question_sets.values() if q.owner_id == owner_id]

    def get_question_set(self, set_id: str) -> ApplicationQuestionSet:
        qs = self._question_sets.get(set_id)
        if not qs:
            raise QuestionSetNotFoundError(f"Question set '{set_id}' not found.")
        return qs

    def parse_questions(self, req: QuestionParseRequest) -> list[ApplicationQuestionRecord]:
        dummy_set_id = f"qset_{uuid4().hex[:6]}"
        return QuestionParser.parse_raw_text(req.raw_text, set_id=dummy_set_id)

    def create_question_set(self, req: QuestionSetCreateRequest, owner_id: str = "default_user") -> ApplicationQuestionSet:
        set_id = f"qset_{uuid4().hex[:8]}"
        questions: list[ApplicationQuestionRecord] = []
        if req.questions_raw:
            questions = QuestionParser.parse_question_list(req.questions_raw, set_id=set_id)

        qset = ApplicationQuestionSet(
            id=set_id,
            owner_id=owner_id,
            job_title=req.job_title,
            employer=req.employer,
            title=req.title,
            questions=questions,
        )
        self._question_sets[qset.id] = qset
        logger.info(f"Created ApplicationQuestionSet '{qset.id}' with {len(questions)} questions")
        return qset

    def generate_answers_for_set(
        self,
        set_id: str,
        profile_id: Optional[str] = "prof_primary_applicant",
    ) -> ApplicationQuestionSet:
        qset = self.get_question_set(set_id)
        try:
            profile = applicant_profile_service.get_profile(profile_id or "prof_primary_applicant")
        except Exception:
            profile = applicant_profile_service.get_primary_profile()

        for q in qset.questions:
            ans = AnswerGenerator.generate_answer(q, profile)
            # Validate answer
            val = AnswerValidator.validate_answer(ans, q)
            if not val["is_valid"]:
                ans.validation_issues.extend(val["issues"])
            q.current_answer = ans

        qset.updated_at = datetime.now(UTC)
        return qset

    def answer_question(
        self,
        question_id: str,
        answer_text: Optional[str] = None,
        numeric_value: Optional[float] = None,
        boolean_value: Optional[bool] = None,
        date_value: Optional[str] = None,
        selected_options: Optional[list[str]] = None,
    ) -> ApplicationAnswer:
        # Find question across sets
        target_q: Optional[ApplicationQuestionRecord] = None
        for qs in self._question_sets.values():
            for q in qs.questions:
                if q.id == question_id:
                    target_q = q
                    break
            if target_q:
                break

        if not target_q:
            raise QuestionNotFoundError(f"Question '{question_id}' not found.")

        ans = target_q.current_answer or ApplicationAnswer(
            id=f"ans_{uuid4().hex[:8]}",
            question_id=question_id,
            profile_id="prof_primary_applicant",
            profile_version=1,
            answer_text="",
        )

        if answer_text is not None:
            ans.answer_text = answer_text
        if numeric_value is not None:
            ans.numeric_value = numeric_value
            if not ans.answer_text:
                ans.answer_text = str(numeric_value)
        if boolean_value is not None:
            ans.boolean_value = boolean_value
            if not ans.answer_text:
                ans.answer_text = "Yes" if boolean_value else "No"
        if date_value is not None:
            ans.date_value = date_value
            if not ans.answer_text:
                ans.answer_text = date_value
        if selected_options is not None:
            ans.selected_options = selected_options
            if not ans.answer_text:
                ans.answer_text = ", ".join(selected_options)

        ans.is_user_overridden = True
        ans.updated_at = datetime.now(UTC)

        # Validate
        val = AnswerValidator.validate_answer(ans, target_q)
        ans.validation_issues = val["issues"]
        target_q.current_answer = ans
        return ans

    def attest_question(
        self,
        question_id: str,
        req: UserAttestationRequest,
    ) -> ApplicationAnswer:
        target_q: Optional[ApplicationQuestionRecord] = None
        for qs in self._question_sets.values():
            for q in qs.questions:
                if q.id == question_id:
                    target_q = q
                    break
            if target_q:
                break

        if not target_q:
            raise QuestionNotFoundError(f"Question '{question_id}' not found.")

        ans = target_q.current_answer or ApplicationAnswer(
            id=f"ans_{uuid4().hex[:8]}",
            question_id=question_id,
            profile_id="prof_primary_applicant",
            profile_version=1,
            answer_text="",
        )

        SensitiveDecisionGuard.apply_user_attestation(ans, actor_id=req.actor_id, accepted=req.attestation_accepted)
        target_q.current_answer = ans
        return ans

    # =========================================================================
    # 4. Missing Information & Sensitive Decisions Queue
    # =========================================================================

    def get_missing_information(self, owner_id: str = "default_user") -> list[MissingInformationItem]:
        items: list[MissingInformationItem] = []
        user_qsets = [q for q in self._question_sets.values() if q.owner_id == owner_id]

        for qs in user_qsets:
            for q in qs.questions:
                ans = q.current_answer
                if not ans or not ans.answer_text.strip():
                    if q.is_required and not q.is_sensitive and not q.requires_attestation:
                        items.append(
                            MissingInformationItem(
                                id=f"msg_{uuid4().hex[:6]}",
                                question_id=q.id,
                                question_text=q.exact_question_text,
                                required_field=q.category.value,
                                field_description=f"Requires {q.category.value} details from candidate profile",
                                is_mandatory=q.is_required,
                            )
                        )
        return items

    def get_sensitive_decisions(self, owner_id: str = "default_user") -> list[SensitiveDecisionItem]:
        items: list[SensitiveDecisionItem] = []
        user_qsets = [q for q in self._question_sets.values() if q.owner_id == owner_id]

        for qs in user_qsets:
            for q in qs.questions:
                decision = SensitiveDecisionGuard.evaluate_question_sensitivity(q)
                if decision:
                    ans = q.current_answer
                    if ans:
                        decision.user_decision = ans.answer_text
                        decision.attestation_accepted = bool(ans.user_attestation_timestamp)
                    items.append(decision)
        return items

    def get_conflicts(self, owner_id: str = "default_user") -> list[ConflictItem]:
        """Detects contradictions between profile facts, resume records, and answer sets."""
        conflicts: list[ConflictItem] = []
        try:
            profile = applicant_profile_service.get_profile("prof_primary_applicant")
        except Exception:
            profile = applicant_profile_service.get_primary_profile()

        # Check education conflicts: e.g. currently enrolled vs claiming completed in answers
        if profile.education:
            edu = profile.education[0]
            status = getattr(edu, "academic_status", getattr(edu, "status", None))
            is_enrolled = status in (AcademicStatus.CURRENTLY_ENROLLED, "currently_enrolled", "in_progress")

            for qs in self._question_sets.values():
                for q in qs.questions:
                    ans = q.current_answer
                    if ans and "graduated" in ans.answer_text.lower() and is_enrolled:
                        conflicts.append(
                            ConflictItem(
                                id=f"cfl_{uuid4().hex[:6]}",
                                title="Academic Graduation Status Conflict",
                                description="Answer text asserts graduation has occurred, while canonical profile marks candidate as currently enrolled.",
                                source_a="Canonical Profile (EducationRecord)",
                                source_b=f"Screening Question Answer ({q.id})",
                                claim_a_value=f"Status: {status}",
                                claim_b_value=ans.answer_text[:60],
                            )
                        )

        return conflicts


# Singleton instance
writing_service = RecruitmentWritingService()
