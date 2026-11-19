"""Data contracts, enums, and Pydantic schemas for Job Intelligence Engine (Stage 28)."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class AnalysisStatus(str, Enum):
    NOT_ANALYZED = "NotAnalyzed"
    QUEUED = "Queued"
    LOADING_SOURCES = "LoadingSources"
    PARSING = "Parsing"
    EXTRACTING = "Extracting"
    VALIDATING = "Validating"
    NEEDS_REVIEW = "NeedsReview"
    PARTIALLY_ANALYZED = "PartiallyAnalyzed"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    OUTDATED = "Outdated"


class RequirementCategory(str, Enum):
    MANDATORY = "Mandatory"
    PREFERRED = "Preferred"
    OPTIONAL = "Optional"
    CONDITIONAL = "Conditional"
    INFORMATIONAL = "Informational"
    EMPLOYER_DESCRIPTION = "EmployerDescription"
    APPLICANT_BENEFIT = "ApplicantBenefit"
    UNKNOWN = "Unknown"


class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    AT_LEAST_N = "AtLeastN"
    ALL = "ALL"
    ANY = "ANY"
    CONDITIONAL = "Conditional"
    EQUIVALENT_ALTERNATIVE = "EquivalentAlternative"
    UNKNOWN_RELATION = "UnknownRelation"


class QualificationType(str, Enum):
    TECHNICAL_SKILL = "TECHNICAL_SKILL"
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    CERTIFICATION = "CERTIFICATION"
    LICENSE = "LICENSE"
    SECURITY_CLEARANCE = "SECURITY_CLEARANCE"
    WORK_AUTHORIZATION = "WORK_AUTHORIZATION"
    LANGUAGE = "LANGUAGE"
    SOFT_SKILL = "SOFT_SKILL"


class DegreeLevel(str, Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    ASSOCIATE = "ASSOCIATE"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTORATE = "DOCTORATE"
    PROFESSIONAL = "PROFESSIONAL"
    EQUIVALENT = "EQUIVALENT"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN = "UNKNOWN"


class DegreeStatus(str, Enum):
    COMPLETED = "COMPLETED"
    CURRENTLY_ENROLLED = "CURRENTLY_ENROLLED"
    FINAL_YEAR = "FINAL_YEAR"
    GRADUATED_RECENTLY = "GRADUATED_RECENTLY"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNKNOWN = "UNKNOWN"


class WorkplaceType(str, Enum):
    REMOTE_GLOBAL = "REMOTE_GLOBAL"
    REMOTE_COUNTRY_ONLY = "REMOTE_COUNTRY_ONLY"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    FLEXIBLE = "FLEXIBLE"
    UNKNOWN = "UNKNOWN"


class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    TEMPORARY = "TEMPORARY"
    UNKNOWN = "UNKNOWN"


class PayPeriod(str, Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"
    STIPEND = "STIPEND"
    PROJECT = "PROJECT"
    UNKNOWN = "UNKNOWN"


class EvidenceConfidence(str, Enum):
    EXPLICIT_VERIFIED_SOURCE = "EXPLICIT_VERIFIED_SOURCE"
    EXPLICIT_UNVERIFIED = "EXPLICIT_UNVERIFIED"
    STRONGLY_SUPPORTED = "STRONGLY_SUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"
    WEAK_INFERENCE = "WEAK_INFERENCE"
    NO_EVIDENCE = "NO_EVIDENCE"


class ExtractionMethod(str, Enum):
    DETERMINISTIC_RULES = "DETERMINISTIC_RULES"
    STRUCTURED_SCHEMA_ORG = "STRUCTURED_SCHEMA_ORG"
    AI_EXTRACTION = "AI_EXTRACTION"
    HYBRID = "HYBRID"
    MANUAL_ENTRY = "MANUAL_ENTRY"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    NOT_NEEDED = "NOT_NEEDED"


class ConflictType(str, Enum):
    DEGREE_REQUIREMENT = "DEGREE_REQUIREMENT"
    WORK_ARRANGEMENT = "WORK_ARRANGEMENT"
    SALARY_RANGE = "SALARY_RANGE"
    VISA_SPONSORSHIP = "VISA_SPONSORSHIP"
    EXPERIENCE_DURATION = "EXPERIENCE_DURATION"
    OTHER = "OTHER"


class ResolutionStrategy(str, Enum):
    PENDING = "PENDING"
    HIGHER_AUTHORITY_ACCEPTED = "HIGHER_AUTHORITY_ACCEPTED"
    NEWER_SOURCE_ACCEPTED = "NEWER_SOURCE_ACCEPTED"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK_LIBRARY = "FRAMEWORK_LIBRARY"
    DATABASE = "DATABASE"
    CLOUD_DEVOPS = "CLOUD_DEVOPS"
    AI_ML = "AI_ML"
    TOOLS_PLATFORMS = "TOOLS_PLATFORMS"
    METHODOLOGY = "METHODOLOGY"
    NON_TECHNICAL = "NON_TECHNICAL"


# ---------------------------------------------------------------------------
# Pydantic Schemas / DTOs
# ---------------------------------------------------------------------------
class RequirementEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    requirement_id: str | None = None
    section_name: str = "MINIMUM_QUALIFICATIONS"
    supporting_text: str
    start_char: int = 0
    end_char: int = 0
    quote_hash: str = ""
    extraction_method: ExtractionMethod = ExtractionMethod.DETERMINISTIC_RULES
    verified_in_source: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class AtomicRequirement(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    category: RequirementCategory = RequirementCategory.MANDATORY
    qualification_type: QualificationType = QualificationType.TECHNICAL_SKILL
    name: str
    normalized_value: str
    raw_text: str
    min_years: float | None = None
    max_years: float | None = None
    is_negated: bool = False
    confidence: EvidenceConfidence = EvidenceConfidence.STRONGLY_SUPPORTED
    confidence_score: float = 1.0
    evidence: list[RequirementEvidence] = Field(default_factory=list)
    needs_review: bool = False
    review_notes: str | None = None


class RequirementGroup(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    parent_group_id: str | None = None
    operator: LogicalOperator = LogicalOperator.AND
    min_count: int | None = None
    description: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)
    child_group_ids: list[str] = Field(default_factory=list)


class StructuredSkill(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    normalized_name: str
    category: SkillCategory = SkillCategory.PROGRAMMING_LANGUAGE
    min_years: float | None = None
    is_mandatory: bool = True
    version_requirement: str | None = None
    evidence: RequirementEvidence | None = None


class EducationRequirement(BaseModel):
    model_config = ConfigDict(extra="ignore")

    degree_level: DegreeLevel = DegreeLevel.BACHELOR
    fields_of_study: list[str] = Field(default_factory=list)
    degree_status: DegreeStatus = DegreeStatus.COMPLETED
    minimum_gpa: float | None = None
    alternative_experience_years: float | None = None
    is_mandatory: bool = True
    raw_text: str = ""
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class ExperienceRequirement(BaseModel):
    model_config = ConfigDict(extra="ignore")

    minimum_years: float | None = None
    maximum_years: float | None = None
    domain_categories: list[str] = Field(default_factory=list)
    is_mandatory: bool = True
    raw_text: str = ""
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class EmploymentConditions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    workplace_type: WorkplaceType = WorkplaceType.UNKNOWN
    primary_location: str | None = None
    allowed_countries: list[str] = Field(default_factory=list)
    office_days_per_week: int | None = None
    travel_percentage: float | None = None
    working_hours: str | None = None
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    contract_duration: str | None = None
    is_relocation_offered: bool | None = None
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class CompensationIntelligence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    base_min: float | None = None
    base_max: float | None = None
    currency: str = "USD"
    pay_period: PayPeriod = PayPeriod.ANNUAL
    has_bonus: bool = False
    bonus_details: str | None = None
    has_equity: bool = False
    equity_details: str | None = None
    benefits: list[str] = Field(default_factory=list)
    original_text: str = ""
    is_disclosed: bool = False
    is_ambiguous: bool = False
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class EligibilityConditions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    work_authorization_required: bool = True
    visa_sponsorship_offered: bool | None = None
    visa_sponsorship_refused: bool | None = None
    citizenship_restrictions: list[str] = Field(default_factory=list)
    security_clearance_required: str | None = None
    is_ambiguous: bool = False
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class ApplicationInstructions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    deadline_utc: datetime | None = None
    is_rolling: bool = False
    start_date_utc: datetime | None = None
    application_url: str = ""
    required_documents: list[str] = Field(default_factory=list)
    instructions_text: str = ""
    evidence: list[RequirementEvidence] = Field(default_factory=list)


class ConflictRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    conflict_type: ConflictType = ConflictType.OTHER
    source_a_id: str | None = None
    source_a_text: str = ""
    source_b_id: str | None = None
    source_b_text: str = ""
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.PENDING
    resolved_text: str | None = None
    is_resolved: bool = False
    resolved_by: str | None = None
    resolved_at: datetime | None = None


class ReviewQueueItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    intelligence_id: str
    requirement_id: str | None = None
    conflict_id: str | None = None
    review_type: str = "AMBIGUOUS_REQUIREMENT"
    reason: str
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_decision: str | None = None
    reviewer_notes: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class JobIntelligenceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    canonical_job_id: str
    canonical_job_version: int = 1
    description_hash: str
    extractor_version: str = "1.0.0"
    analysis_status: AnalysisStatus = AnalysisStatus.NOT_ANALYZED
    job_title: str
    role_family: str | None = None
    seniority: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    mandatory_requirements: list[AtomicRequirement] = Field(default_factory=list)
    preferred_requirements: list[AtomicRequirement] = Field(default_factory=list)
    optional_requirements: list[AtomicRequirement] = Field(default_factory=list)
    conditional_requirements: list[AtomicRequirement] = Field(default_factory=list)
    requirement_groups: list[RequirementGroup] = Field(default_factory=list)
    skills: list[StructuredSkill] = Field(default_factory=list)
    education: list[EducationRequirement] = Field(default_factory=list)
    experience: list[ExperienceRequirement] = Field(default_factory=list)
    employment_conditions: EmploymentConditions = Field(default_factory=EmploymentConditions)
    compensation: CompensationIntelligence = Field(default_factory=CompensationIntelligence)
    eligibility: EligibilityConditions = Field(default_factory=EligibilityConditions)
    application_instructions: ApplicationInstructions = Field(default_factory=ApplicationInstructions)
    conflicts: list[ConflictRecord] = Field(default_factory=list)
    review_items: list[ReviewQueueItem] = Field(default_factory=list)
    data_quality_warnings: list[str] = Field(default_factory=list)
    overall_confidence: float = 1.0
    review_status: ReviewStatus = ReviewStatus.NOT_NEEDED
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
