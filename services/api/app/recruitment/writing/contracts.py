"""Recruitment Writing & Application Intelligence Domain Contracts (Stage 24)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class CoverLetterType(StrEnum):
    GENERAL = "general"
    ROLE_SPECIFIC = "role_specific"
    INTERNSHIP = "internship"
    EXPERIENCED = "experienced"
    RESEARCH = "research"
    SHORT = "short"


class WritingTone(StrEnum):
    PROFESSIONAL = "professional"
    CONCISE = "concise"
    FORMAL = "formal"
    FRIENDLY_PROFESSIONAL = "friendly_professional"
    TECHNICAL = "technical"
    RESEARCH_FOCUSED = "research_focused"
    EARLY_CAREER = "early_career"
    EXECUTIVE = "executive"


class WritingLength(StrEnum):
    SHORT = "short"
    STANDARD = "standard"
    DETAILED = "detailed"
    CUSTOM = "custom"


class WritingDocumentStatus(StrEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    NEEDS_REVIEW = "needs_review"
    VALIDATING = "validating"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"


class QuestionCategory(StrEnum):
    CONTACT = "contact"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    PROJECTS = "projects"
    WORK_ELIGIBILITY = "work_eligibility"
    AVAILABILITY = "availability"
    COMPENSATION = "compensation"
    MOTIVATION = "motivation"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    PORTFOLIO = "portfolio"
    REFERENCES = "references"
    SENSITIVE_DISCLOSURE = "sensitive_disclosure"
    ATTESTATION = "attestation"
    UNKNOWN = "unknown"


class AnswerType(StrEnum):
    FREE_TEXT = "free_text"
    SHORT_TEXT = "short_text"
    PARAGRAPH = "paragraph"
    NUMERIC = "numeric"
    DATE = "date"
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    DROPDOWN = "dropdown"
    MULTI_PART = "multi_part"
    CONDITIONAL = "conditional"


class AnswerState(StrEnum):
    AVAILABLE_CONFIRMED = "available_confirmed"
    AVAILABLE_EVIDENCE_SUPPORTED = "available_evidence_supported"
    AVAILABLE_USER_REPORTED = "available_user_reported"
    DRAFT_GENERATED = "draft_generated"
    REQUIRES_USER_CONFIRMATION = "requires_user_confirmation"
    REQUIRES_USER_ATTESTATION = "requires_user_attestation"
    MISSING_INFORMATION = "missing_information"
    CONFLICTING_INFORMATION = "conflicting_information"
    SENSITIVE_OPTIONAL = "sensitive_optional"
    NOT_APPLICABLE = "not_applicable"
    UNSUPPORTED = "unsupported"
    REJECTED = "rejected"
    APPROVED = "approved"


class AnswerFreshnessStatus(StrEnum):
    FRESH = "fresh"
    OUTDATED = "outdated"
    SUPERSEDED = "superseded"
    REQUIRES_REVALIDATION = "requires_revalidation"


class WritingPackageStatus(StrEnum):
    CREATED = "created"
    GATHERING_CONTEXT = "gathering_context"
    GENERATING = "generating"
    NEEDS_REVIEW = "needs_review"
    INCOMPLETE = "incomplete"
    VALIDATING = "validating"
    READY_FOR_APPROVAL = "ready_for_approval"
    APPROVED = "approved"
    ARCHIVED = "archived"
    FAILED = "failed"


# =============================================================================
# Provenance & Source Anchors
# =============================================================================

class WritingSourceReference(BaseModel):
    source_entity_id: str
    source_type: str = Field(description="claim, education, experience, project, skill, github_repo, resume_bullet")
    claim_id: Optional[str] = None
    verification_status: str = "user_confirmed"
    attribution_text: Optional[str] = None
    evidence_url: Optional[str] = None


# =============================================================================
# Cover Letter Models
# =============================================================================

class CoverLetterContentBlock(BaseModel):
    id: str = Field(default_factory=lambda: f"blk_{uuid4().hex[:8]}")
    block_type: str = Field(description="header, salutation, opening, qualifications, evidence_example, motivation, closing, signature")
    title: Optional[str] = None
    text: str
    ordering: int = 0
    source_refs: list[WritingSourceReference] = Field(default_factory=list)
    word_count: int = 0
    is_user_edited: bool = False


class CoverLetterDocument(BaseModel):
    id: str = Field(default_factory=lambda: f"cl_{uuid4().hex[:8]}")
    owner_id: str = "default_user"
    profile_id: str
    profile_snapshot_id: str
    resume_id: Optional[str] = None
    resume_version: Optional[int] = None
    title: str
    letter_type: CoverLetterType = CoverLetterType.ROLE_SPECIFIC
    target_role: str
    employer_name: Optional[str] = None
    job_description_raw: Optional[str] = None
    template_id: str = "classic_professional"
    tone: WritingTone = WritingTone.PROFESSIONAL
    length_preference: WritingLength = WritingLength.STANDARD
    max_words: Optional[int] = 400
    recipient_name: Optional[str] = None
    recipient_title: Optional[str] = None
    recipient_organization: Optional[str] = None
    recipient_address: Optional[str] = None
    status: WritingDocumentStatus = WritingDocumentStatus.DRAFT
    current_version: int = 1
    content_hash: str = ""
    blocks: list[CoverLetterContentBlock] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approved_at: Optional[datetime] = None


class CoverLetterTemplateDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: str = "professional"
    version: str = "1.0.0"
    primary_font: str = "Helvetica"
    heading_font: str = "Helvetica-Bold"
    base_font_size_pt: float = 10.5
    heading_font_size_pt: float = 13.0
    margin_top_in: float = 0.8
    margin_bottom_in: float = 0.8
    margin_left_in: float = 0.8
    margin_right_in: float = 0.8
    primary_color: str = "#1e293b"
    accent_color: str = "#0284c7"
    text_color: str = "#0f172a"
    line_spacing: float = 1.15
    layout_style: str = "classic"


class CoverLetterVersionRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"clv_{uuid4().hex[:8]}")
    cover_letter_id: str
    version_number: int
    profile_snapshot_id: str
    content_hash: str
    changelog: str = "Initial approved version"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_id: str = "default_user"
    is_published: bool = True
    document_snapshot: dict[str, Any] = Field(default_factory=dict)
    export_artifact_ids: list[str] = Field(default_factory=list)


# =============================================================================
# Application Question & Answer Models
# =============================================================================

class ApplicationAnswer(BaseModel):
    id: str = Field(default_factory=lambda: f"ans_{uuid4().hex[:8]}")
    question_id: str
    profile_id: str
    profile_version: int = 1
    answer_text: str = ""
    numeric_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    date_value: Optional[str] = None
    selected_options: list[str] = Field(default_factory=list)
    state: AnswerState = AnswerState.DRAFT_GENERATED
    freshness_status: AnswerFreshnessStatus = AnswerFreshnessStatus.FRESH
    source_refs: list[WritingSourceReference] = Field(default_factory=list)
    confidence_score: float = 1.0
    is_user_overridden: bool = False
    user_attestation_timestamp: Optional[datetime] = None
    user_attestation_actor: Optional[str] = None
    validation_issues: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApplicationQuestionRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"qst_{uuid4().hex[:8]}")
    set_id: str
    exact_question_text: str
    normalized_question: str
    category: QuestionCategory = QuestionCategory.UNKNOWN
    answer_type: AnswerType = AnswerType.FREE_TEXT
    is_required: bool = True
    allowed_options: list[str] = Field(default_factory=list)
    max_characters: Optional[int] = None
    max_words: Optional[int] = None
    min_numeric_value: Optional[float] = None
    max_numeric_value: Optional[float] = None
    numeric_unit: Optional[str] = None
    conditional_parent_id: Optional[str] = None
    conditional_trigger_value: Optional[str] = None
    is_sensitive: bool = False
    requires_attestation: bool = False
    current_answer: Optional[ApplicationAnswer] = None


class ApplicationQuestionSet(BaseModel):
    id: str = Field(default_factory=lambda: f"qset_{uuid4().hex[:8]}")
    owner_id: str = "default_user"
    job_title: str
    employer: Optional[str] = None
    job_description_id: Optional[str] = None
    title: str
    questions: list[ApplicationQuestionRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Answer Library Models
# =============================================================================

class AnswerLibraryEntry(BaseModel):
    id: str = Field(default_factory=lambda: f"lib_{uuid4().hex[:8]}")
    owner_id: str = "default_user"
    title: str
    category: QuestionCategory = QuestionCategory.TECHNICAL
    parameterized_template: str
    sample_resolved_text: str
    answer_type: AnswerType = AnswerType.FREE_TEXT
    applicable_technologies: list[str] = Field(default_factory=list)
    associated_project_ids: list[str] = Field(default_factory=list)
    state: str = "approved"  # candidate, draft, needs_review, approved, outdated, deprecated
    version_number: int = 1
    reuse_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Review Queue Items: Missing Info, Sensitive, Conflicts
# =============================================================================

class MissingInformationItem(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:8]}")
    question_id: str
    question_text: str
    required_field: str
    field_description: str
    is_mandatory: bool = True
    suggested_profile_destination: Optional[str] = None
    user_input_provided: Optional[str] = None
    resolved: bool = False


class SensitiveDecisionItem(BaseModel):
    id: str = Field(default_factory=lambda: f"sns_{uuid4().hex[:8]}")
    question_id: str
    question_text: str
    category: str = Field(description="work_authorization, visa_sponsorship, compensation_expectation, voluntary_disclosure, legal_attestation")
    allowed_choices: list[str] = Field(default_factory=list)
    is_voluntary: bool = False
    user_decision: Optional[str] = None
    attestation_accepted: bool = False
    decided_at: Optional[datetime] = None


class ConflictItem(BaseModel):
    id: str = Field(default_factory=lambda: f"cfl_{uuid4().hex[:8]}")
    title: str
    description: str
    source_a: str
    source_b: str
    claim_a_value: str
    claim_b_value: str
    resolved: bool = False
    resolution_note: Optional[str] = None


# =============================================================================
# Writing Package
# =============================================================================

class ApplicationWritingPackage(BaseModel):
    id: str = Field(default_factory=lambda: f"pkg_{uuid4().hex[:8]}")
    owner_id: str = "default_user"
    target_job_title: str
    target_employer: str
    job_description_raw: Optional[str] = None
    profile_snapshot_id: str
    resume_id: Optional[str] = None
    resume_version: Optional[int] = None
    cover_letter_id: Optional[str] = None
    cover_letter_version: Optional[int] = None
    question_set_id: Optional[str] = None
    status: WritingPackageStatus = WritingPackageStatus.CREATED
    version_number: int = 1
    total_questions: int = 0
    answered_questions: int = 0
    pending_sensitive_decisions: int = 0
    pending_attestations: int = 0
    missing_information_count: int = 0
    conflicts_count: int = 0
    is_ready_for_approval: bool = False
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Overview Statistics
# =============================================================================

class WritingOverviewStats(BaseModel):
    total_cover_letters: int = 0
    approved_cover_letters: int = 0
    total_question_sets: int = 0
    total_screening_questions: int = 0
    approved_library_answers: int = 0
    pending_reviews: int = 0
    missing_info_count: int = 0
    sensitive_decisions_count: int = 0
    writing_packages_count: int = 0


# =============================================================================
# Request DTOs
# =============================================================================

class CoverLetterCreateRequest(BaseModel):
    profile_id: Optional[str] = "prof_primary_applicant"
    title: str
    letter_type: CoverLetterType = CoverLetterType.ROLE_SPECIFIC
    target_role: str
    employer_name: Optional[str] = None
    job_description_raw: Optional[str] = None
    resume_id: Optional[str] = None
    template_id: str = "classic_professional"
    tone: WritingTone = WritingTone.PROFESSIONAL
    length_preference: WritingLength = WritingLength.STANDARD
    max_words: Optional[int] = 400
    recipient_name: Optional[str] = None
    recipient_title: Optional[str] = None
    recipient_organization: Optional[str] = None


class CoverLetterUpdateRequest(BaseModel):
    title: Optional[str] = None
    target_role: Optional[str] = None
    employer_name: Optional[str] = None
    template_id: Optional[str] = None
    tone: Optional[WritingTone] = None
    length_preference: Optional[WritingLength] = None
    max_words: Optional[int] = None
    recipient_name: Optional[str] = None
    recipient_title: Optional[str] = None
    recipient_organization: Optional[str] = None
    blocks: Optional[list[CoverLetterContentBlock]] = None


class CoverLetterGenerateRequest(BaseModel):
    job_description_raw: Optional[str] = None
    target_role: Optional[str] = None
    employer_name: Optional[str] = None
    tone: Optional[WritingTone] = None
    length_preference: Optional[WritingLength] = None
    max_words: Optional[int] = None


class ParagraphRewriteRequest(BaseModel):
    block_id: str
    instruction: str = Field(description="e.g. 'more concise', 'highlight metrics', 'more technical'")
    target_tone: Optional[WritingTone] = None


class CoverLetterExportRequest(BaseModel):
    format: str = "pdf"  # "pdf" | "docx" | "html"
    custom_filename: Optional[str] = None
    validate_extraction: bool = True


class QuestionParseRequest(BaseModel):
    raw_text: str
    job_title: Optional[str] = "Software Engineer"
    employer: Optional[str] = None


class QuestionSetCreateRequest(BaseModel):
    job_title: str
    employer: Optional[str] = None
    title: str
    questions_raw: Optional[list[str]] = None


class AnswerUpdateRequest(BaseModel):
    answer_text: Optional[str] = None
    numeric_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    date_value: Optional[str] = None
    selected_options: Optional[list[str]] = None


class UserAttestationRequest(BaseModel):
    attestation_accepted: bool = True
    actor_id: str = "default_user"


class AnswerLibraryCreateRequest(BaseModel):
    title: str
    category: QuestionCategory = QuestionCategory.TECHNICAL
    parameterized_template: str
    sample_resolved_text: str
    answer_type: AnswerType = AnswerType.FREE_TEXT
    applicable_technologies: list[str] = Field(default_factory=list)
    associated_project_ids: list[str] = Field(default_factory=list)


class AnswerLibraryUpdateRequest(BaseModel):
    title: Optional[str] = None
    parameterized_template: Optional[str] = None
    sample_resolved_text: Optional[str] = None
    state: Optional[str] = None


class AnswerReusePreviewRequest(BaseModel):
    question_text: str
    parameters: dict[str, str] = Field(default_factory=dict)


class WritingPackageCreateRequest(BaseModel):
    target_job_title: str
    target_employer: str
    job_description_raw: Optional[str] = None
    profile_id: Optional[str] = "prof_primary_applicant"
    resume_id: Optional[str] = None
    cover_letter_id: Optional[str] = None
    question_set_id: Optional[str] = None
