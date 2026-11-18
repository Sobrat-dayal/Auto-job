"""Strongly-typed contracts, schemas, and enums for Applicant Profile Intelligence (Stage 21)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator


# =============================================================================
# Enums
# =============================================================================

class AcademicStatus(StrEnum):
    CURRENTLY_ENROLLED = "currently_enrolled"
    COMPLETED = "completed"
    GRADUATED = "graduated"
    ON_LEAVE = "on_leave"
    DISCONTINUED = "discontinued"
    UNKNOWN = "unknown"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    VOLUNTEER = "volunteer"


class WorkArrangement(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class SkillCategory(StrEnum):
    PROGRAMMING_LANGUAGES = "programming_languages"
    AI_ML = "ai_ml"
    WEB_DEVELOPMENT = "web_development"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASES = "databases"
    CLOUD_DEVOPS = "cloud_devops"
    CYBERSECURITY = "cybersecurity"
    TESTING = "testing"
    DEVELOPMENT_TOOLS = "development_tools"
    NON_TECHNICAL = "non_technical"
    OTHER = "other"


class ProficiencyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


SkillProficiency = ProficiencyLevel


class ProjectCategory(StrEnum):
    ACADEMIC = "academic"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    OPEN_SOURCE = "open_source"
    RESEARCH = "research"


class PublicationStatus(StrEnum):
    PUBLISHED = "published"
    ACCEPTED = "accepted"
    SUBMITTED = "submitted"
    PREPRINT = "preprint"
    UNDER_REVIEW = "under_review"
    DRAFT = "draft"


class ClaimCategory(StrEnum):
    DEGREE = "degree"
    SKILL = "skill"
    EMPLOYMENT = "employment"
    ACHIEVEMENT = "achievement"
    CONTRIBUTION = "contribution"
    CERTIFICATION = "certification"
    PUBLICATION = "publication"
    AWARD = "award"
    ELIGIBILITY = "eligibility"
    GENERAL = "general"


class VerificationStatus(StrEnum):
    USER_REPORTED = "UserReported"
    USER_CONFIRMED = "UserConfirmed"
    EVIDENCE_SUPPORTED = "EvidenceSupported"
    EXTERNALLY_VERIFIED = "ExternallyVerified"
    UNVERIFIED = "Unverified"
    CONFLICTED = "Conflicted"
    SUPERSEDED = "Superseded"
    REJECTED = "Rejected"


ClaimVerificationStatus = VerificationStatus


class PrivacyClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ImportStatus(StrEnum):
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING = "extracting"
    REVIEW_READY = "review_ready"
    COMMITTED = "committed"
    FAILED = "failed"


class CandidateStatus(StrEnum):
    EXTRACTED = "extracted"
    AWAITING_REVIEW = "awaiting_review"
    ACCEPTED = "accepted"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class QualitySeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# =============================================================================
# Sub-Entities
# =============================================================================

class ContactInfo(BaseModel):
    legal_name: Optional[str] = Field(default=None, description="Full legal name of the applicant")
    preferred_name: Optional[str] = Field(default=None, description="Preferred display/calling name")
    primary_email: Optional[str] = Field(default=None, description="Primary email address")
    additional_emails: list[str] = Field(default_factory=list, description="Secondary verified emails")
    phone: Optional[str] = Field(default=None, description="Phone number with area code")
    country_code: Optional[str] = Field(default=None, description="ISO country dialing prefix (e.g., +1, +91)")
    preferred_contact_method: str = Field(default="email", description="email, phone, or messaging")
    website_url: Optional[str] = Field(default=None, description="Personal or professional homepage")
    portfolio_url: Optional[str] = Field(default=None, description="Portfolio or showcase site")


class LocationInfo(BaseModel):
    country: Optional[str] = Field(default=None, description="Country of residence")
    state_province: Optional[str] = Field(default=None, description="State, province, or region")
    city: Optional[str] = Field(default=None, description="City of residence")
    postal_code: Optional[str] = Field(default=None, description="Postal code or ZIP")
    remote_preference: str = Field(default="flexible", description="remote_only, hybrid, on_site, or flexible")


class EmploymentEligibility(BaseModel):
    authorized_countries: list[str] = Field(default_factory=list, description="Countries authorized to work in without sponsorship")
    requires_sponsorship: bool = Field(default=False, description="Whether visa sponsorship is required")
    is_internship_eligible: bool = Field(default=True, description="Eligible for internship programs")
    available_start_date: Optional[str] = Field(default=None, description="Earliest availability (YYYY-MM-DD)")
    notice_period_days: int = Field(default=0, description="Notice period required in current role")
    confirmed_by_user: bool = Field(default=False, description="Whether explicitly attested by the user")


class AchievementItem(BaseModel):
    id: str = Field(default_factory=lambda: f"ach_{uuid4().hex[:8]}")
    statement: str = Field(description="Impactful accomplishment description")
    metric_value: Optional[str] = Field(default=None, description="Quantitative metric value (e.g. '35%', '10k')")
    metric_unit: Optional[str] = Field(default=None, description="Metric dimension (e.g. 'percent', 'users')")
    measurement_source: Optional[str] = Field(default=None, description="Data source proving the metric")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)


class EducationRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"edu_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    institution: str = Field(description="Name of university, college, or school")
    degree: str = Field(description="Degree type (e.g., Bachelor of Science, Master of Science)")
    field_of_study: str = Field(description="Major or discipline (e.g., Computer Science)")
    specialization: Optional[str] = Field(default=None, description="Track, minor, or concentration")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY or YYYY-MM)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY or YYYY-MM)")
    expected_completion: Optional[str] = Field(default=None, description="Expected completion date if ongoing")
    academic_status: AcademicStatus = Field(default=AcademicStatus.COMPLETED)
    gpa: Optional[float] = Field(default=None, description="Cumulative grade point average")
    gpa_scale: Optional[float] = Field(default=4.0, description="Scale maximum (e.g., 4.0, 10.0)")
    coursework: list[str] = Field(default_factory=list, description="Notable coursework topics")
    distinctions: list[str] = Field(default_factory=list, description="Honors, Dean's List, Cum Laude")
    evidence_refs: list[str] = Field(default_factory=list, description="IDs of linked evidence documents")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmploymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    employer: str = Field(description="Company or organization name")
    job_title: str = Field(description="Job title or role designation")
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    start_date: str = Field(description="Start date (YYYY-MM or YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date or None if current")
    is_current: bool = Field(default=False, description="Whether currently working in this role")
    location: Optional[str] = Field(default=None, description="Job location (City, Country)")
    work_arrangement: WorkArrangement = Field(default=WorkArrangement.HYBRID)
    responsibilities: list[str] = Field(default_factory=list, description="Key job responsibilities")
    technologies: list[str] = Field(default_factory=list, description="Tools and technologies leveraged")
    achievements: list[AchievementItem] = Field(default_factory=list, description="Measured achievements")
    evidence_refs: list[str] = Field(default_factory=list, description="Linked evidence document IDs")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SkillItem(BaseModel):
    id: str = Field(default_factory=lambda: f"skl_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    name: str = Field(description="Skill name as entered")
    canonical_name: str = Field(description="Normalized taxonomy identifier (e.g. 'python', 'react')")
    category: SkillCategory = Field(default=SkillCategory.PROGRAMMING_LANGUAGES)
    proficiency: ProficiencyLevel = Field(default=ProficiencyLevel.INTERMEDIATE)
    years_experience: Optional[float] = Field(default=None, ge=0)
    last_used: Optional[str] = Field(default=None, description="Year last actively practiced (YYYY)")
    evidence_refs: list[str] = Field(default_factory=list, description="Linked projects or certs")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"prj_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    title: str = Field(description="Project name or title")
    description: str = Field(description="Project overview and problem statement")
    category: ProjectCategory = Field(default=ProjectCategory.PERSONAL)
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="Completion date")
    is_ongoing: bool = Field(default=False)
    technologies: list[str] = Field(default_factory=list, description="Tech stack components")
    applicant_contribution: str = Field(default="", description="Specific modules or features authored by applicant")
    team_context: Optional[str] = Field(default=None, description="Solo, team size, role in team")
    responsibilities: list[str] = Field(default_factory=list)
    results: list[str] = Field(default_factory=list, description="Live deployment, stars, users, metrics")
    repo_url: Optional[str] = Field(default=None, description="Source repository link")
    demo_url: Optional[str] = Field(default=None, description="Live demonstration or production link")
    evidence_refs: list[str] = Field(default_factory=list, description="Screenshots, code archives")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CertificationRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"crt_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    title: str = Field(description="Certification title")
    issuing_org: str = Field(description="Certifying entity (e.g. AWS, Google Cloud, Microsoft)")
    issue_date: str = Field(description="Date granted (YYYY-MM or YYYY-MM-DD)")
    expiration_date: Optional[str] = Field(default=None, description="Expiration date if time-bounded")
    credential_id: Optional[str] = Field(default=None, description="License or cert serial number")
    verification_url: Optional[str] = Field(default=None, description="Public verification link")
    skills: list[str] = Field(default_factory=list, description="Associated skill competencies")
    evidence_ref: Optional[str] = Field(default=None, description="Evidence document ID")
    is_expired: bool = Field(default=False)
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PublicationRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"pub_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    title: str = Field(description="Paper or article title")
    authors: list[str] = Field(default_factory=list, description="List of co-authors")
    applicant_position: int = Field(default=1, description="1 for first author, 2 for second, etc.")
    journal_conference: Optional[str] = Field(default=None, description="Venue name")
    publication_date: Optional[str] = Field(default=None, description="Date published")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier or stable URL")
    status: PublicationStatus = Field(default=PublicationStatus.PUBLISHED)
    evidence_ref: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AwardRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"awd_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    title: str = Field(description="Award or honor title")
    issuer: str = Field(description="Granting entity")
    issue_date: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default="academic", description="academic, competition, professional")
    description: Optional[str] = Field(default=None)
    evidence_ref: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProfessionalLink(BaseModel):
    id: str = Field(default_factory=lambda: f"lnk_{uuid4().hex[:8]}")
    profile_id: Optional[str] = None
    platform: str = Field(description="github, linkedin, portfolio, gitlab, google_scholar, other")
    url: str = Field(description="Valid web link")
    display_label: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Claims & Evidence
# =============================================================================

class ApplicantClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"clm_{uuid4().hex[:12]}")
    profile_id: str
    category: ClaimCategory
    normalized_value: str = Field(description="Canonical normalized statement (e.g. 'Skill: Python', 'Degree: BS CS')")
    original_text: str = Field(description="Raw source statement or resume excerpt")
    evidence_refs: list[str] = Field(default_factory=list)
    source_category: str = Field(default="user_entered", description="user_entered, document_extracted, evidence_derived")
    source_ref: Optional[str] = Field(default=None, description="Filename or import job ID")
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_REPORTED)
    version: int = Field(default=1)
    effective_date: Optional[str] = Field(default=None)
    supersedes_claim_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceMetadata(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"evd_{uuid4().hex[:12]}")
    profile_id: str
    filename: str
    file_type: str = Field(description="pdf, docx, txt, png, jpg")
    file_size_bytes: int = Field(ge=0)
    content_hash: str = Field(description="SHA-256 digest of file payload")
    storage_path: str = Field(description="Internal protected artifact location")
    source_category: str = Field(default="resume", description="resume, transcript, certificate, publication, other")
    privacy_classification: PrivacyClassification = Field(default=PrivacyClassification.CONFIDENTIAL)
    linked_claim_ids: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = Field(default=VerificationStatus.USER_CONFIRMED)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Import Pipeline & Candidate Review
# =============================================================================

class ExtractionCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"cnd_{uuid4().hex[:8]}")
    import_id: str
    category: ClaimCategory
    field_name: str = Field(description="e.g. 'education.institution', 'skills.technical'")
    proposed_value: Any = Field(description="Parsed structured or scalar value")
    raw_excerpt: str = Field(default="", description="Source text snippet proving extraction")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    status: CandidateStatus = Field(default=CandidateStatus.AWAITING_REVIEW)
    matched_existing_id: Optional[str] = Field(default=None, description="ID of conflicting or duplicate existing record")
    is_duplicate: bool = Field(default=False)
    conflict_warning: Optional[str] = Field(default=None)


class ImportJob(BaseModel):
    import_id: str = Field(default_factory=lambda: f"imp_{uuid4().hex[:12]}")
    profile_id: str
    filename: str
    file_type: str
    status: ImportStatus = Field(default=ImportStatus.PENDING)
    extracted_candidates: list[ExtractionCandidate] = Field(default_factory=list)
    raw_text_preview: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = Field(default=None)


class ProfileConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: f"cfl_{uuid4().hex[:8]}")
    profile_id: str
    claim_id_a: str
    claim_id_b: str
    category: ClaimCategory
    field_name: str
    description: str
    resolution_status: str = Field(default="pending", description="pending, resolved, dismissed")
    resolved_claim_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: Optional[datetime] = None


# =============================================================================
# Quality & Completeness
# =============================================================================

class DataQualityIssue(BaseModel):
    code: str = Field(description="e.g. 'MISSING_EMAIL', 'FUTURE_GRADUATION_NOT_MARKED_ENROLLED'")
    severity: QualitySeverity
    category: str
    message: str
    field_ref: Optional[str] = None
    suggested_fix: Optional[str] = None


class DataQualityReport(BaseModel):
    profile_id: str
    completeness_score: float = Field(ge=0.0, le=100.0, description="Percentage of recommended fields confirmed")
    is_recruitment_ready: bool = Field(description="True if minimum identity, contact, education, and skills are present")
    issues: list[DataQualityIssue] = Field(default_factory=list)
    category_breakdown: dict[str, float] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Versioning & Snapshots
# =============================================================================

class ProfileVersionRecord(BaseModel):
    version: int
    changed_fields: list[str] = Field(default_factory=list)
    actor_id: str = Field(default="user")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reason: Optional[str] = None


class ProfileSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: f"snp_{uuid4().hex[:12]}")
    profile_id: str
    version: int
    target_agent: str = Field(description="e.g. 'job_matching_agent', 'resume_agent'")
    authorized_scopes: list[str] = Field(default_factory=list)
    filtered_data: dict[str, Any] = Field(description="Sanitized data conforming to agent scope")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Top-Level Canonical Applicant Profile
# =============================================================================

class ApplicantProfile(BaseModel):
    id: str = Field(default_factory=lambda: f"prof_{uuid4().hex[:12]}")
    owner_id: str = Field(default="default_user", description="Owner user ID for tenant isolation")
    display_label: str = Field(default="Primary Career Profile")
    headline: Optional[str] = Field(default=None, description="e.g. 'Senior Full-Stack Engineer'")
    summary: Optional[str] = Field(default=None, description="Executive narrative summary")
    status: str = Field(default="active", description="active, draft, archived")
    version: int = Field(default=1)
    preferred_language: str = Field(default="en")

    contact: ContactInfo = Field(default_factory=ContactInfo)
    location: LocationInfo = Field(default_factory=LocationInfo)
    eligibility: Optional[EmploymentEligibility] = Field(default=None)

    education: list[EducationRecord] = Field(default_factory=list)
    experience: list[EmploymentRecord] = Field(default_factory=list)
    skills: list[SkillItem] = Field(default_factory=list)
    projects: list[ProjectRecord] = Field(default_factory=list)
    certifications: list[CertificationRecord] = Field(default_factory=list)
    publications: list[PublicationRecord] = Field(default_factory=list)
    awards: list[AwardRecord] = Field(default_factory=list)
    professional_links: list[ProfessionalLink] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# API Request / Response Wrappers
# =============================================================================

class ProfileCreateRequest(BaseModel):
    display_label: str = "Primary Career Profile"
    headline: Optional[str] = None
    summary: Optional[str] = None
    contact: Optional[ContactInfo] = None
    location: Optional[LocationInfo] = None
    eligibility: Optional[EmploymentEligibility] = None


class ProfileUpdateRequest(BaseModel):
    display_label: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    preferred_language: Optional[str] = None
    contact: Optional[ContactInfo] = None
    location: Optional[LocationInfo] = None
    eligibility: Optional[EmploymentEligibility] = None
    reason: Optional[str] = None


class CandidateReviewActionRequest(BaseModel):
    candidate_id: str
    action: str = Field(description="accept, correct, reject")
    corrected_value: Optional[Any] = None


class CreateSnapshotRequest(BaseModel):
    target_agent: str = "job_matching_agent"
    scopes: list[str] = Field(default_factory=lambda: ["skills", "education", "experience", "projects"])
