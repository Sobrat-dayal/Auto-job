"""Authoritative Domain Contracts for Resume Intelligence & Portfolio System (Stage 23)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


# =============================================================================
# Core Enums
# =============================================================================

class ResumeType(str, Enum):
    MASTER = "master"
    GENERAL = "general"
    JOB_TAILORED = "job_tailored"
    INTERNSHIP = "internship"
    EXPERIENCED = "experienced"
    ACADEMIC = "academic"
    MINIMALIST = "minimalist"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    NEEDS_REVIEW = "needs_review"
    VALIDATING = "validating"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"


class PageFormat(str, Enum):
    LETTER = "letter"
    A4 = "a4"


class SectionType(str, Enum):
    HEADER = "header"
    SUMMARY = "summary"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    INTERNSHIPS = "internships"
    SKILLS = "skills"
    PROJECTS = "projects"
    RESEARCH = "research"
    PUBLICATIONS = "publications"
    CERTIFICATIONS = "certifications"
    AWARDS = "awards"
    LEADERSHIP = "leadership"
    VOLUNTEERING = "volunteering"
    COURSEWORK = "coursework"
    CUSTOM = "custom"


class RequirementMatchCategory(str, Enum):
    DIRECTLY_SUPPORTED = "directly_supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    RELATED_EXPERIENCE = "related_experience"
    NOT_EVIDENCED = "not_evidenced"
    REQUIRES_REVIEW = "requires_review"


class ATSCheckStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"
    NOT_EVALUATED = "not_evaluated"


class ExportFormat(str, Enum):
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class TemplateCategory(str, Enum):
    ATS_CLASSIC = "ats_classic"
    MODERN_PROFESSIONAL = "modern_professional"
    TECHNICAL_ENGINEER = "technical_engineer"
    INTERNSHIP_GRADUATE = "internship_graduate"
    ACADEMIC_RESEARCH = "academic_research"
    MINIMALIST = "minimalist"


# =============================================================================
# Fact Reference & Evidence Models
# =============================================================================

class SourceFactReference(BaseModel):
    """Binds an atomic piece of resume text to its underlying canonical claim."""
    source_entity_id: str = Field(description="ID of EducationRecord, EmploymentRecord, SkillItem, or ProjectRecord")
    claim_id: Optional[str] = Field(default=None, description="Stage 21 Claim ID if registered")
    verification_status: str = Field(default="user_confirmed", description="e.g. evidence_backed, user_confirmed, user_reported")
    applicant_profile_version: int = Field(default=1)
    evidence_id: Optional[str] = Field(default=None, description="Stage 21/22 Evidence ID")
    attribution_level: Optional[str] = Field(default=None, description="Stage 22 attribution tier")
    source_excerpt: Optional[str] = Field(default=None, description="Verified quote or commit SHA")


# =============================================================================
# Resume Section & Entry Models
# =============================================================================

class ResumeEntry(BaseModel):
    """An individual item within a resume section (e.g. one job, one degree, one project)."""
    id: str = Field(default_factory=lambda: f"rent_{uuid4().hex[:8]}")
    entry_type: str = Field(default="standard", description="job, degree, project, skill_group, custom")
    title: str = Field(description="Job title, degree, project name, or skill category")
    subtitle: Optional[str] = Field(default=None, description="Company, institution, or project role")
    organization: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    is_current: bool = False
    description: Optional[str] = Field(default=None)
    bullet_points: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list, description="Technologies, skills, or keywords")
    source_refs: list[SourceFactReference] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict, description="Verified quantitative outcomes")
    is_visible: bool = True
    ordering: int = 0


class ResumeSection(BaseModel):
    """A distinct structural division of the resume."""
    id: str = Field(default_factory=lambda: f"rsec_{uuid4().hex[:8]}")
    section_type: SectionType
    display_title: str
    ordering: int = 0
    is_visible: bool = True
    entries: list[ResumeEntry] = Field(default_factory=list)
    source_references: list[SourceFactReference] = Field(default_factory=list)
    validation_state: str = Field(default="valid", description="valid, warning, unverified")


# =============================================================================
# Canonical Resume Document Model
# =============================================================================

class ResumeDocument(BaseModel):
    """The canonical, structured resume entity."""
    id: str = Field(default_factory=lambda: f"res_{uuid4().hex[:12]}")
    owner_id: str = Field(default="default_user")
    profile_id: str = Field(default="prof_primary_applicant")
    profile_snapshot_id: str = Field(default="", description="Immutable Stage 21 ProfileSnapshot ID")
    title: str = Field(description="Internal name, e.g. 'Backend Engineer 2026' or 'Master Resume'")
    resume_type: ResumeType = ResumeType.GENERAL
    target_role: Optional[str] = Field(default=None, description="Target job title or objective")
    job_ref: Optional[str] = Field(default=None, description="ID of associated JobDescriptionSnapshot")
    template_id: str = Field(default="ats_classic")
    template_version: str = Field(default="1.0.0")
    status: DocumentStatus = DocumentStatus.DRAFT
    current_version: int = Field(default=1)
    locale: str = Field(default="en-US")
    page_format: PageFormat = PageFormat.LETTER
    max_pages: int = Field(default=1, description="Target page budget: 1, 2, or 0 for flexible CV")
    header_contact: dict[str, Any] = Field(default_factory=dict, description="Name, email, phone, location, links")
    sections: list[ResumeSection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approved_at: Optional[datetime] = None
    approval_actor: Optional[str] = None


class ResumeCreateRequest(BaseModel):
    profile_id: str = "prof_primary_applicant"
    title: str
    resume_type: ResumeType = ResumeType.GENERAL
    target_role: Optional[str] = None
    template_id: str = "ats_classic"
    page_format: PageFormat = PageFormat.LETTER
    max_pages: int = 1
    job_description_text: Optional[str] = None
    selected_project_ids: Optional[list[str]] = None
    selected_skill_names: Optional[list[str]] = None


class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None
    target_role: Optional[str] = None
    template_id: Optional[str] = None
    page_format: Optional[PageFormat] = None
    max_pages: Optional[int] = None
    status: Optional[DocumentStatus] = None
    header_contact: Optional[dict[str, Any]] = None
    sections: Optional[list[ResumeSection]] = None


class ResumeVersionRecord(BaseModel):
    """Immutable record of an approved or published resume snapshot."""
    id: str = Field(default_factory=lambda: f"rver_{uuid4().hex[:10]}")
    resume_id: str
    version_number: int
    profile_snapshot_id: str
    job_ref: Optional[str] = None
    template_id: str
    template_version: str = "1.0.0"
    content_hash: str
    changelog: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_id: str = "user"
    is_published: bool = False
    document_snapshot: dict[str, Any] = Field(default_factory=dict)
    export_artifact_ids: list[str] = Field(default_factory=list)


# =============================================================================
# Job Tailoring & Requirements Models
# =============================================================================

class JobDescriptionSnapshot(BaseModel):
    """Captured job specification used for evidence-grounded tailoring."""
    id: str = Field(default_factory=lambda: f"job_{uuid4().hex[:10]}")
    owner_id: str = "default_user"
    job_title: str
    employer: Optional[str] = None
    raw_text: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_reqs: list[str] = Field(default_factory=list)
    education_reqs: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    location: Optional[str] = None
    work_arrangement: Optional[str] = None
    source_url: Optional[str] = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class JobDescriptionParseRequest(BaseModel):
    raw_text: str
    job_title: Optional[str] = None
    employer: Optional[str] = None
    source_url: Optional[str] = None


class RequirementEvidenceMapping(BaseModel):
    """Explicit mapping between a job requirement and verified applicant facts."""
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid4().hex[:8]}")
    requirement_text: str
    is_required: bool = True
    claim_id: Optional[str] = None
    claim_text: Optional[str] = None
    match_category: RequirementMatchCategory
    explanation: str
    uncertainty: float = Field(default=0.0, description="0.0 = certain, 1.0 = highly uncertain")


class ResumeTailorRequest(BaseModel):
    resume_id: str
    job_description_text: Optional[str] = None
    job_id: Optional[str] = None
    target_role: Optional[str] = None
    generate_summary: bool = True
    prioritize_skills: bool = True
    prioritize_projects: bool = True


# =============================================================================
# ATS Readability & Validation Models
# =============================================================================

class ATSCheckResult(BaseModel):
    check_name: str
    status: ATSCheckStatus
    observed_evidence: str
    impact_explanation: str
    suggested_remediation: Optional[str] = None
    location: Optional[str] = None


class ATSReadabilityReport(BaseModel):
    overall_status: ATSCheckStatus
    passed_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    checks: list[ATSCheckResult] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    document_id: str
    format: str = "internal_structure"
    notes: str = "AUTONOM internal deterministic structural audit. Does NOT guarantee interview outcomes or simulate proprietary third-party ATS parsers."


# =============================================================================
# Template Registry Models
# =============================================================================

class ResumeTemplateDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: TemplateCategory
    version: str = "1.0.0"
    supported_page_formats: list[PageFormat] = Field(default_factory=lambda: [PageFormat.LETTER, PageFormat.A4])
    supported_sections: list[SectionType] = Field(default_factory=list)
    primary_font: str = "Helvetica"
    heading_font: str = "Helvetica-Bold"
    base_font_size_pt: float = 10.0
    heading_font_size_pt: float = 12.0
    title_font_size_pt: float = 18.0
    margin_top_in: float = 0.5
    margin_bottom_in: float = 0.5
    margin_left_in: float = 0.5
    margin_right_in: float = 0.5
    primary_color: str = "#1A1A1A"
    accent_color: str = "#0055A5"
    has_header_border: bool = True
    is_two_column: bool = False
    ats_friendly: bool = True


# =============================================================================
# Export & Artifact Models
# =============================================================================

class ExportArtifact(BaseModel):
    export_id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:10]}")
    resume_id: str
    version_id: str
    format: ExportFormat
    filename: str
    file_path: str
    file_size_bytes: int = 0
    sha256_checksum: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "completed"
    validation_result: Optional[dict[str, Any]] = None


class ResumeExportRequest(BaseModel):
    format: ExportFormat
    output_directory: Optional[str] = None
    custom_filename: Optional[str] = None
    validate_extraction: bool = True


# =============================================================================
# Professional Portfolio Models
# =============================================================================

class PortfolioProjectEntry(BaseModel):
    project_id: str = Field(default_factory=lambda: f"pprj_{uuid4().hex[:8]}")
    title: str
    summary: str
    problem_addressed: Optional[str] = None
    tech_stack: list[str] = Field(default_factory=list)
    architecture_highlights: list[str] = Field(default_factory=list)
    individual_contribution: str
    deliverables: list[str] = Field(default_factory=list)
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    screenshot_path: Optional[str] = None
    attribution_level: str = "commit_author_evidence"
    is_public_eligible: bool = True
    ordering: int = 0


class PortfolioDocument(BaseModel):
    id: str = Field(default_factory=lambda: f"port_{uuid4().hex[:12]}")
    owner_id: str = "default_user"
    profile_id: str = "prof_primary_applicant"
    title: str = "Professional Technical Portfolio"
    professional_intro: str = ""
    selected_skills: list[str] = Field(default_factory=list)
    selected_projects: list[PortfolioProjectEntry] = Field(default_factory=list)
    publications: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)
    public_contact: dict[str, Any] = Field(default_factory=dict)
    template_id: str = "portfolio_modern"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: DocumentStatus = DocumentStatus.DRAFT


class PortfolioCreateRequest(BaseModel):
    title: str = "Professional Technical Portfolio"
    professional_intro: Optional[str] = None
    selected_project_ids: Optional[list[str]] = None
    selected_skills: Optional[list[str]] = None
    template_id: str = "portfolio_modern"


class PortfolioUpdateRequest(BaseModel):
    title: Optional[str] = None
    professional_intro: Optional[str] = None
    selected_skills: Optional[list[str]] = None
    selected_projects: Optional[list[PortfolioProjectEntry]] = None
    public_contact: Optional[dict[str, Any]] = None
    template_id: Optional[str] = None
    status: Optional[DocumentStatus] = None
