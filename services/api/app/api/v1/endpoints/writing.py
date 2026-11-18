"""FastAPI Endpoints for Recruitment Writing & Application Intelligence (Stage 24)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query, status
from app.api.dependencies import AuthDep
from app.core.security import AuthContext
from app.recruitment.writing.contracts import (
    AnswerLibraryCreateRequest,
    AnswerLibraryEntry,
    AnswerLibraryUpdateRequest,
    AnswerReusePreviewRequest,
    AnswerUpdateRequest,
    ApplicationAnswer,
    ApplicationQuestionRecord,
    ApplicationQuestionSet,
    ApplicationWritingPackage,
    ConflictItem,
    CoverLetterCreateRequest,
    CoverLetterDocument,
    CoverLetterExportRequest,
    CoverLetterGenerateRequest,
    CoverLetterTemplateDefinition,
    CoverLetterUpdateRequest,
    CoverLetterVersionRecord,
    MissingInformationItem,
    ParagraphRewriteRequest,
    QuestionCategory,
    QuestionParseRequest,
    QuestionSetCreateRequest,
    SensitiveDecisionItem,
    UserAttestationRequest,
    WritingOverviewStats,
    WritingPackageCreateRequest,
)
from app.recruitment.writing.cover_letters.templates import CoverLetterTemplateRegistry
from app.recruitment.writing.errors import (
    CoverLetterNotFoundError,
    QuestionNotFoundError,
    QuestionSetNotFoundError,
    WritingDomainError,
)
from app.recruitment.writing.service import writing_service

logger = logging.getLogger("autonom.api.writing")
router = APIRouter(tags=["Recruitment Writing"])


# =============================================================================
# 1. Overview & Statistics
# =============================================================================

@router.get("/recruitment/writing/overview", response_model=WritingOverviewStats)
async def get_writing_overview(
    auth: AuthDep,
) -> WritingOverviewStats:
    """Returns aggregated metrics for cover letters, question sets, and reusable answers."""
    return writing_service.get_overview_stats(owner_id=auth.client_id)


# =============================================================================
# 2. Cover Letter Endpoints
# =============================================================================

@router.get("/cover-letters", response_model=list[CoverLetterDocument])
async def list_cover_letters(
    auth: AuthDep,
) -> list[CoverLetterDocument]:
    """Lists all cover letter documents owned by the active applicant."""
    return writing_service.list_cover_letters(owner_id=auth.client_id)


@router.post("/cover-letters", response_model=CoverLetterDocument, status_code=status.HTTP_201_CREATED)
async def create_cover_letter(
    req: CoverLetterCreateRequest,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Creates a new evidence-grounded cover letter draft."""
    try:
        return writing_service.create_cover_letter(req, auth=auth)
    except Exception as e:
        logger.error(f"Failed to create cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/cover-letters/{letter_id}", response_model=CoverLetterDocument)
async def get_cover_letter(
    letter_id: str,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Retrieves cover letter detail by ID."""
    try:
        return writing_service.get_cover_letter(letter_id)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/cover-letters/{letter_id}", response_model=CoverLetterDocument)
async def update_cover_letter(
    letter_id: str,
    req: CoverLetterUpdateRequest,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Updates mutable fields or content blocks of a cover letter."""
    try:
        return writing_service.update_cover_letter(letter_id, req)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/cover-letters/{letter_id}")
async def delete_cover_letter(
    letter_id: str,
    auth: AuthDep,
) -> dict[str, str]:
    """Deletes a cover letter document."""
    writing_service.delete_cover_letter(letter_id)
    return {"status": "deleted", "id": letter_id}


@router.post("/cover-letters/{letter_id}/generate", response_model=CoverLetterDocument)
async def regenerate_cover_letter(
    letter_id: str,
    req: CoverLetterGenerateRequest,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Regenerates grounded cover letter blocks with updated role or tone preferences."""
    try:
        return writing_service.regenerate_cover_letter(letter_id, req)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/cover-letters/{letter_id}/rewrite-paragraph", response_model=CoverLetterDocument)
async def rewrite_paragraph(
    letter_id: str,
    req: ParagraphRewriteRequest,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Rewrites a single paragraph block with specified tone or conciseness adjustments."""
    try:
        return writing_service.rewrite_paragraph(letter_id, req)
    except WritingDomainError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/cover-letters/{letter_id}/validate")
async def validate_cover_letter(
    letter_id: str,
    auth: AuthDep,
) -> dict[str, Any]:
    """Audits cover letter factual claims against verified profile facts."""
    try:
        return writing_service.validate_cover_letter(letter_id)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/cover-letters/{letter_id}/approve", response_model=CoverLetterVersionRecord)
async def approve_cover_letter(
    letter_id: str,
    auth: AuthDep,
) -> CoverLetterVersionRecord:
    """Approves cover letter and captures an immutable version snapshot with SHA-256 digest."""
    try:
        return writing_service.approve_cover_letter(letter_id, actor_id=auth.client_id)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/cover-letters/{letter_id}/versions", response_model=list[CoverLetterVersionRecord])
async def list_cover_letter_versions(
    letter_id: str,
    auth: AuthDep,
) -> list[CoverLetterVersionRecord]:
    """Lists historical immutable snapshots of a cover letter."""
    return writing_service.list_cover_letter_versions(letter_id)


@router.post("/cover-letters/{letter_id}/versions/{version_number}/restore", response_model=CoverLetterDocument)
async def restore_cover_letter_version(
    letter_id: str,
    version_number: int,
    auth: AuthDep,
) -> CoverLetterDocument:
    """Restores a historical version snapshot into a fresh editable draft revision."""
    try:
        return writing_service.restore_cover_letter_version(letter_id, version_number)
    except WritingDomainError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/cover-letters/{letter_id}/preview")
async def preview_cover_letter(
    letter_id: str,
    auth: AuthDep,
) -> dict[str, str]:
    """Generates a responsive HTML preview of the cover letter."""
    try:
        return writing_service.preview_cover_letter_html(letter_id)
    except CoverLetterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/cover-letters/{letter_id}/export")
async def export_cover_letter(
    letter_id: str,
    req: CoverLetterExportRequest,
    auth: AuthDep,
) -> dict[str, Any]:
    """Compiles and exports cover letter to Word .docx or selectable .pdf with validation."""
    try:
        return writing_service.export_cover_letter(letter_id, req)
    except Exception as e:
        logger.error(f"Failed to export cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/cover-letter-templates", response_model=list[CoverLetterTemplateDefinition])
async def list_cover_letter_templates() -> list[CoverLetterTemplateDefinition]:
    """Lists all 6 registered professional cover letter templates."""
    return CoverLetterTemplateRegistry.list_templates()


# =============================================================================
# 3. Application Questions & Answers
# =============================================================================

@router.post("/application-questions/analyze", response_model=list[ApplicationQuestionRecord])
async def analyze_questions(
    req: QuestionParseRequest,
    auth: AuthDep,
) -> list[ApplicationQuestionRecord]:
    """Parses raw question blocks, detects constraints, and classifies categories."""
    return writing_service.parse_questions(req)


@router.get("/application-question-sets", response_model=list[ApplicationQuestionSet])
async def list_question_sets(
    auth: AuthDep,
) -> list[ApplicationQuestionSet]:
    """Lists saved application question sets."""
    return writing_service.list_question_sets(owner_id=auth.client_id)


@router.post("/application-question-sets", response_model=ApplicationQuestionSet, status_code=status.HTTP_201_CREATED)
async def create_question_set(
    req: QuestionSetCreateRequest,
    auth: AuthDep,
) -> ApplicationQuestionSet:
    """Creates a new structured question set for an application."""
    return writing_service.create_question_set(req, owner_id=auth.client_id)


@router.get("/application-question-sets/{set_id}", response_model=ApplicationQuestionSet)
async def get_question_set(
    set_id: str,
    auth: AuthDep,
) -> ApplicationQuestionSet:
    """Retrieves question set detail with parsed questions and answers."""
    try:
        return writing_service.get_question_set(set_id)
    except QuestionSetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/application-question-sets/{set_id}/generate-answers", response_model=ApplicationQuestionSet)
async def generate_answers(
    set_id: str,
    auth: AuthDep,
    profile_id: Optional[str] = Query(default="prof_primary_applicant"),
) -> ApplicationQuestionSet:
    """Generates grounded draft answers for all eligible questions in the set."""
    try:
        return writing_service.generate_answers_for_set(set_id, profile_id=profile_id)
    except QuestionSetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/application-questions/{question_id}/answer", response_model=ApplicationAnswer)
async def answer_question(
    question_id: str,
    req: AnswerUpdateRequest,
    auth: AuthDep,
) -> ApplicationAnswer:
    """Updates an application answer with user modifications or selected choices."""
    try:
        return writing_service.answer_question(
            question_id=question_id,
            answer_text=req.answer_text,
            numeric_value=req.numeric_value,
            boolean_value=req.boolean_value,
            date_value=req.date_value,
            selected_options=req.selected_options,
        )
    except QuestionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/application-questions/{question_id}/attest", response_model=ApplicationAnswer)
async def attest_question(
    question_id: str,
    req: UserAttestationRequest,
    auth: AuthDep,
) -> ApplicationAnswer:
    """Records explicit human user attestation for legal certification questions."""
    try:
        return writing_service.attest_question(question_id, req)
    except QuestionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# =============================================================================
# 4. Answer Library Endpoints
# =============================================================================

@router.get("/application-answer-library", response_model=list[AnswerLibraryEntry])
async def list_answer_library(
    auth: AuthDep,
    category: Optional[QuestionCategory] = Query(default=None),
) -> list[AnswerLibraryEntry]:
    """Lists reusable answer templates with optional category filter."""
    return writing_service.library_mgr.list_entries(owner_id=auth.client_id, category=category)


@router.post("/application-answer-library", response_model=AnswerLibraryEntry, status_code=status.HTTP_201_CREATED)
async def create_library_entry(
    req: AnswerLibraryCreateRequest,
    auth: AuthDep,
) -> AnswerLibraryEntry:
    """Creates a reusable parameterized answer template in the library."""
    return writing_service.library_mgr.create_entry(
        title=req.title,
        category=req.category,
        parameterized_template=req.parameterized_template,
        sample_resolved_text=req.sample_resolved_text,
        answer_type=req.answer_type,
        applicable_technologies=req.applicable_technologies,
        associated_project_ids=req.associated_project_ids,
        owner_id=auth.client_id,
    )


@router.get("/application-answer-library/{entry_id}", response_model=AnswerLibraryEntry)
async def get_library_entry(
    entry_id: str,
    auth: AuthDep,
) -> AnswerLibraryEntry:
    """Retrieves reusable answer template detail."""
    try:
        return writing_service.library_mgr.get_entry(entry_id)
    except WritingDomainError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/application-answer-library/{entry_id}", response_model=AnswerLibraryEntry)
async def update_library_entry(
    entry_id: str,
    req: AnswerLibraryUpdateRequest,
    auth: AuthDep,
) -> AnswerLibraryEntry:
    """Updates reusable answer template text or status."""
    try:
        return writing_service.library_mgr.update_entry(
            entry_id,
            title=req.title,
            parameterized_template=req.parameterized_template,
            sample_resolved_text=req.sample_resolved_text,
            state=req.state,
        )
    except WritingDomainError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/application-answer-library/{entry_id}/reuse-preview")
async def preview_answer_reuse(
    entry_id: str,
    req: AnswerReusePreviewRequest,
    auth: AuthDep,
) -> dict[str, str]:
    """Previews template parameter resolution for a target application question."""
    entry = writing_service.library_mgr.get_entry(entry_id)
    resolved_text = writing_service.library_mgr.resolve_template(entry, req.parameters)
    return {
        "entry_id": entry_id,
        "question_text": req.question_text,
        "resolved_text": resolved_text,
    }


@router.get("/application-answer-library/freshness-check")
async def check_library_freshness(
    auth: AuthDep,
) -> dict[str, Any]:
    """Checks answer templates against canonical profile facts and flags outdated answers."""
    try:
        profile = writing_service._cover_letters  # access profile
        from app.recruitment.profile.service import applicant_profile_service
        prof = applicant_profile_service.get_primary_profile()
    except Exception:
        prof = None

    if prof:
        return writing_service.library_mgr.check_freshness(prof)
    return {"total_entries": 0, "outdated_count": 0}


# =============================================================================
# 5. Missing Information & Sensitive Decisions
# =============================================================================

@router.get("/recruitment/writing/missing-information", response_model=list[MissingInformationItem])
async def get_missing_information(
    auth: AuthDep,
) -> list[MissingInformationItem]:
    """Returns queue of unanswered requirements requiring candidate profile details."""
    return writing_service.get_missing_information(owner_id=auth.client_id)


@router.get("/recruitment/writing/sensitive-decisions", response_model=list[SensitiveDecisionItem])
async def get_sensitive_decisions(
    auth: AuthDep,
) -> list[SensitiveDecisionItem]:
    """Returns sensitive questions requiring explicit human user review and election."""
    return writing_service.get_sensitive_decisions(owner_id=auth.client_id)


@router.get("/recruitment/writing/conflicts", response_model=list[ConflictItem])
async def get_writing_conflicts(
    auth: AuthDep,
) -> list[ConflictItem]:
    """Detects contradictions between candidate profile facts and application answers."""
    return writing_service.get_conflicts(owner_id=auth.client_id)


# =============================================================================
# 6. Application Writing Packages
# =============================================================================

@router.get("/application-writing-packages", response_model=list[ApplicationWritingPackage])
async def list_writing_packages(
    auth: AuthDep,
) -> list[ApplicationWritingPackage]:
    """Lists assembled application writing packages."""
    return writing_service.package_mgr.list_packages(owner_id=auth.client_id)


@router.post("/application-writing-packages", response_model=ApplicationWritingPackage, status_code=status.HTTP_201_CREATED)
async def create_writing_package(
    req: WritingPackageCreateRequest,
    auth: AuthDep,
) -> ApplicationWritingPackage:
    """Assembles a new Application Writing Package binding resume, cover letter, and Q&A."""
    return writing_service.package_mgr.create_package(
        target_job_title=req.target_job_title,
        target_employer=req.target_employer,
        profile_snapshot_id=f"snap_{uuid4().hex[:8]}",
        job_description_raw=req.job_description_raw,
        resume_id=req.resume_id,
        cover_letter_id=req.cover_letter_id,
        question_set_id=req.question_set_id,
        owner_id=auth.client_id,
    )


@router.get("/application-writing-packages/{package_id}", response_model=ApplicationWritingPackage)
async def get_writing_package(
    package_id: str,
    auth: AuthDep,
) -> ApplicationWritingPackage:
    """Retrieves writing package detail and readiness status."""
    try:
        return writing_service.package_mgr.get_package(package_id)
    except WritingDomainError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/application-writing-packages/{package_id}/validate")
async def validate_writing_package(
    package_id: str,
    auth: AuthDep,
) -> dict[str, Any]:
    """Audits package cross-document consistency and checks pending attestations."""
    pkg = writing_service.package_mgr.get_package(package_id)
    from app.recruitment.profile.service import applicant_profile_service
    profile = applicant_profile_service.get_primary_profile()

    cl = writing_service._cover_letters.get(pkg.cover_letter_id) if pkg.cover_letter_id else None
    qs = writing_service._question_sets.get(pkg.question_set_id) if pkg.question_set_id else None

    return writing_service.package_mgr.validate_package(pkg, profile, cover_letter=cl, question_set=qs)


@router.post("/application-writing-packages/{package_id}/approve", response_model=ApplicationWritingPackage)
async def approve_writing_package(
    package_id: str,
    auth: AuthDep,
) -> ApplicationWritingPackage:
    """Approves application writing package for future form attachment (does not submit externally)."""
    try:
        return writing_service.package_mgr.approve_package(package_id, actor_id=auth.client_id)
    except WritingDomainError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
