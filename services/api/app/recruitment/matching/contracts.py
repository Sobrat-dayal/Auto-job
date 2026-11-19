"""Strongly-typed contracts, schemas, and enums for Applicant-to-Job Matching Engine (Stage 29)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field


def generate_uuid() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


# =============================================================================
# Enums
# =============================================================================

class MatchingOutcome(str, Enum):
    """Structured internal outcome classification of applicant-job match."""
    ELIGIBLE_AND_ALIGNED = "eligible_and_aligned"
    ELIGIBLE_BUT_LOWER_PRIORITY = "eligible_but_lower_priority"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    REQUIRES_APPLICANT_REVIEW = "requires_applicant_review"
    MISSING_CRITICAL_INFORMATION = "missing_critical_information"
    KNOWN_REQUIREMENT_NOT_MET = "known_requirement_not_met"
    REJECTED_BY_HARD_POLICY = "rejected_by_hard_policy"
    BLOCKED_BY_AUTHORIZATION = "blocked_by_authorization"
    JOB_UNAVAILABLE = "job_unavailable"
    MATCH_EVALUATION_FAILED = "match_evaluation_failed"
    NOT_EVALUATED = "not_evaluated"


class RequirementMatchCategory(str, Enum):
    """Evaluation state of an individual employer requirement against applicant evidence."""
    DIRECTLY_SATISFIED = "directly_satisfied"
    SATISFIED_BY_ALTERNATIVE = "satisfied_by_alternative"
    PARTIALLY_SUPPORTED = "partially_supported"
    RELATED_EXPERIENCE_ONLY = "related_experience_only"
    NOT_EVIDENCED = "not_evidenced"
    KNOWN_NOT_SATISFIED = "known_not_satisfied"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    CONFLICTED = "conflicted"


class GapSeverity(str, Enum):
    """Severity classification of an identified qualification gap."""
    BLOCKING = "blocking"
    CRITICAL_REVIEW = "critical_review"
    SIGNIFICANT = "significant"
    MODERATE = "moderate"
    MINOR = "minor"
    INFORMATIONAL = "informational"
    UNKNOWN = "unknown"


class GapType(str, Enum):
    """Category of deficiency or uncertainty."""
    MISSING_MANDATORY_SKILL = "missing_mandatory_skill"
    MISSING_PREFERRED_SKILL = "missing_preferred_skill"
    DURATION_DEFICIT = "duration_deficit"
    RELATED_ONLY = "related_only"
    MISSING_EVIDENCE = "missing_evidence"
    AMBIGUOUS_REQUIREMENT = "ambiguous_requirement"
    UNVERIFIED_CLAIM = "unverified_claim"


class ApplicationReadiness(str, Enum):
    """Operational readiness for downstream application preparation (NOT submission grant)."""
    READY_FOR_PREPARATION = "ready_for_preparation"
    REQUIRES_REVIEW = "requires_review"
    INELIGIBLE = "ineligible"
    HARD_POLICY_EXCLUDED = "hard_policy_excluded"
    UNAVAILABLE = "unavailable"
    NOT_EVALUATED = "not_evaluated"


class ReviewType(str, Enum):
    """Trigger reasons for routing to the Matching Human Review Queue."""
    UNKNOWN_WORK_AUTH = "unknown_work_auth"
    AMBIGUOUS_ALTERNATIVE = "ambiguous_alternative"
    CONFLICTING_CLAIMS = "conflicting_claims"
    UNVERIFIED_MANDATORY_SKILL = "unverified_mandatory_skill"
    COMPENSATION_UNCERTAINTY = "compensation_uncertainty"
    LOCATION_CONFLICT = "location_conflict"
    DUPLICATE_RISK = "duplicate_risk"
    STALE_JOB = "stale_job"


class ReviewStatus(str, Enum):
    """Resolution status of review items."""
    PENDING = "pending"
    RESOLVED = "resolved"
    DEFERRED = "deferred"
    DISMISSED = "dismissed"


# =============================================================================
# Snapshots & Input Data Contracts
# =============================================================================

class ApplicantSnapshotData(BaseModel):
    """Immutable snapshot of applicant profile facts used for matching."""
    model_config = ConfigDict(extra="ignore")

    profile_id: str
    version: int
    headline: str | None = None
    summary: str | None = None
    country: str | None = None
    city: str | None = None
    remote_preference: str | None = None
    authorized_countries: list[str] = Field(default_factory=list)
    requires_sponsorship: bool = False
    is_internship_eligible: bool = True
    available_start_date: str | None = None
    notice_period_days: int = 0
    skills: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)


class JobIntelligenceSnapshotData(BaseModel):
    """Structured requirements and metadata resolved from Stage 28 and Stage 27."""
    model_config = ConfigDict(extra="ignore")

    canonical_job_id: str
    canonical_job_version: int = 1
    job_title: str
    company_name: str
    job_location: str | None = None
    employment_type: str | None = None
    work_arrangement: str | None = None
    status: str = "active"
    discovered_at: str | None = None
    role_family: str | None = None
    seniority: str | None = None
    mandatory_requirements: list[dict[str, Any]] = Field(default_factory=list)
    preferred_requirements: list[dict[str, Any]] = Field(default_factory=list)
    optional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    conditional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    requirement_groups: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    employment_conditions: dict[str, Any] = Field(default_factory=dict)
    compensation: dict[str, Any] = Field(default_factory=dict)
    eligibility: dict[str, Any] = Field(default_factory=dict)
    deadlines: dict[str, Any] = Field(default_factory=dict)


class CareerStrategySnapshotData(BaseModel):
    """Career policy preferences and restrictions resolved from Stage 25."""
    model_config = ConfigDict(extra="ignore")

    strategy_id: str
    title: str = "Default Career Strategy"
    is_active: bool = True
    role_families: list[str] = Field(default_factory=list)
    target_locations: list[str] = Field(default_factory=list)
    excluded_locations: list[str] = Field(default_factory=list)
    work_arrangements: list[str] = Field(default_factory=list)
    relocation_preference: str = "not_willing"
    min_annual_salary: float | None = None
    target_annual_salary: float | None = None
    salary_currency: str = "USD"
    undisclosed_salary_handling: str = "review"
    blocked_employers: list[str] = Field(default_factory=list)
    preferred_employers: list[str] = Field(default_factory=list)
    allowed_employment_types: list[str] = Field(default_factory=list)


# =============================================================================
# Evaluation Detail Models
# =============================================================================

class RequirementEvaluationResult(BaseModel):
    """Evaluation result for an atomic employer requirement."""
    model_config = ConfigDict(extra="ignore")

    requirement_id: str
    name: str
    category: str  # mandatory, preferred, optional, conditional
    match_category: RequirementMatchCategory
    applicant_claim_ref: str | None = None
    applicant_evidence_snippet: str | None = None
    job_evidence_snippet: str | None = None
    confidence: float = 1.0
    explanation: str
    is_satisfied: bool = False


class GroupEvaluationResult(BaseModel):
    """Evaluation result for a logical requirement group (AND/OR/AtLeastN)."""
    model_config = ConfigDict(extra="ignore")

    group_id: str
    operator: str
    target_count: int = 1
    satisfied_count: int = 0
    is_satisfied: bool = False
    is_unknown: bool = False
    explanation: str


class SkillMatchDetail(BaseModel):
    """Detailed matching breakdown for an individual skill requirement."""
    model_config = ConfigDict(extra="ignore")

    skill_name: str
    canonical_name: str
    category: str
    priority: str
    required_years: float | None = None
    applicant_years: float | None = None
    applicant_proficiency: str | None = None
    match_status: RequirementMatchCategory
    is_alias_match: bool = False
    is_related_match: bool = False
    explanation: str


class EducationMatchDetail(BaseModel):
    """Detailed evaluation of educational prerequisites."""
    model_config = ConfigDict(extra="ignore")

    degree_level: str
    field_of_study: str
    applicant_degree: str | None = None
    applicant_field: str | None = None
    applicant_status: str | None = None
    status_compatible: bool = False
    field_compatible: bool = False
    match_status: RequirementMatchCategory
    explanation: str


class ExperienceMatchDetail(BaseModel):
    """Detailed evaluation of professional employment duration and overlap."""
    model_config = ConfigDict(extra="ignore")

    required_min_years: float | None = None
    required_max_years: float | None = None
    required_domain: str | None = None
    calculated_professional_years: float = 0.0
    total_calendar_months_non_overlapping: int = 0
    has_overlapping_roles: bool = False
    internship_months: int = 0
    academic_project_count: int = 0
    match_status: RequirementMatchCategory
    explanation: str


class EligibilityConditionDetail(BaseModel):
    """Evaluation of work authorization, sponsorship, locations, and employer restrictions."""
    model_config = ConfigDict(extra="ignore")

    work_authorization_status: str
    sponsorship_status: str
    remote_compatibility: str
    location_compatibility: str
    relocation_compatibility: str
    compensation_compatibility: str
    employer_restriction_status: str
    hard_policy_passed: bool = True
    hard_policy_reason: str | None = None
    explanation: str


# =============================================================================
# Gap Intelligence & Remediation
# =============================================================================

class SkillGapItem(BaseModel):
    """Identified deficiency or missing qualification."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    requirement_id: str | None = None
    skill_or_qualification: str
    gap_type: GapType
    severity: GapSeverity
    description: str
    remediation_suggestion: str


class MissingInformationRequest(BaseModel):
    """Actionable request to applicant to supply unconfirmed information."""
    model_config = ConfigDict(extra="ignore")

    requirement_name: str
    missing_fact: str
    importance: str
    suggested_profile_field: str


# =============================================================================
# Ranking Rubric & Relevance Index
# =============================================================================

class DimensionScore(BaseModel):
    """Score for a single dimension in the explainable relevance index rubric."""
    model_config = ConfigDict(extra="ignore")

    dimension_id: str
    name: str
    raw_score: float  # 0.0 to 1.0
    weight: float  # 0.0 to 1.0
    weighted_score: float
    max_possible_weighted_score: float
    is_observed: bool = True
    explanation: str


class RelevanceIndexBreakdown(BaseModel):
    """Transparent, deterministic 0–100 relevance index calculation."""
    model_config = ConfigDict(extra="ignore")

    relevance_index: float = 0.0
    total_weight_observed: float = 1.0
    dimensions: list[DimensionScore] = Field(default_factory=list)
    missing_dimensions: list[str] = Field(default_factory=list)
    formula_explanation: str = "Weighted average of observed dimensions normalized to a 0–100 scale."


class RubricConfig(BaseModel):
    """Configurable weights and policies for ranking."""
    model_config = ConfigDict(extra="ignore")

    id: str = "rubric_default_v1"
    version: int = 1
    name: str = "Standard AUTONOM Recruitment Rubric"
    description: str = "Balances mandatory qualifications, preferred skills, compensation, and location."
    is_default: bool = True
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "qualification_alignment": 0.25,
            "preferred_skills": 0.15,
            "role_family": 0.15,
            "experience_duration": 0.10,
            "work_arrangement": 0.10,
            "compensation": 0.10,
            "employer_preference": 0.05,
            "posting_freshness": 0.10,
        }
    )
    missing_data_policy: str = "conservative"


class CounterfactualScenario(BaseModel):
    """Hypothetical simulation scenario explaining what changes would alter the outcome."""
    model_config = ConfigDict(extra="ignore")

    scenario_name: str
    hypothetical_change: str
    current_state: str
    simulated_state: str
    impact_summary: str


# =============================================================================
# Top-Level Evaluation & Reporting Record
# =============================================================================

class JobMatchEvaluation(BaseModel):
    """Comprehensive explainable match evaluation record for a canonical job."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=generate_uuid)
    profile_id: str
    canonical_job_id: str
    job_title: str
    company_name: str
    job_location: str | None = None
    employment_type: str | None = None
    work_arrangement: str | None = None
    career_strategy_id: str | None = None
    rubric_id: str = "rubric_default_v1"
    version: int = 1
    is_current: bool = True
    status: str = "completed"
    eligibility_outcome: MatchingOutcome = MatchingOutcome.NOT_EVALUATED
    relevance_index: float = 0.0
    mandatory_coverage_ratio: float = 0.0
    preferred_coverage_ratio: float = 0.0
    evidence_completeness_ratio: float = 0.0
    ranking_uncertainty_ratio: float = 0.0
    application_readiness: ApplicationReadiness = ApplicationReadiness.NOT_EVALUATED
    hard_policy_passed: bool = True
    hard_policy_reason: str | None = None
    summary_explanation: str = ""
    requirement_results: list[RequirementEvaluationResult] = Field(default_factory=list)
    group_results: list[GroupEvaluationResult] = Field(default_factory=list)
    skill_details: list[SkillMatchDetail] = Field(default_factory=list)
    education_detail: EducationMatchDetail | None = None
    experience_detail: ExperienceMatchDetail | None = None
    eligibility_detail: EligibilityConditionDetail = Field(
        default_factory=lambda: EligibilityConditionDetail(
            work_authorization_status="unknown",
            sponsorship_status="unknown",
            remote_compatibility="unknown",
            location_compatibility="unknown",
            relocation_compatibility="unknown",
            compensation_compatibility="unknown",
            employer_restriction_status="allowed",
            hard_policy_passed=True,
            hard_policy_reason=None,
            explanation="Initial state",
        )
    )
    score_breakdown: RelevanceIndexBreakdown = Field(default_factory=RelevanceIndexBreakdown)
    gaps: list[SkillGapItem] = Field(default_factory=list)
    missing_information: list[MissingInformationRequest] = Field(default_factory=list)
    review_requests: list[dict[str, Any]] = Field(default_factory=list)
    counterfactuals: list[CounterfactualScenario] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# =============================================================================
# API Request & Response Contracts
# =============================================================================

class MatchEvaluationRequest(BaseModel):
    """Request payload to evaluate an applicant against a canonical job."""
    model_config = ConfigDict(extra="ignore")

    profile_id: str | None = None
    canonical_job_id: str
    career_strategy_id: str | None = None
    rubric_id: str | None = None
    force: bool = False
    use_ai: bool = False


class BatchMatchEvaluationRequest(BaseModel):
    """Request payload to batch evaluate multiple jobs."""
    model_config = ConfigDict(extra="ignore")

    profile_id: str | None = None
    job_ids: list[str]
    career_strategy_id: str | None = None
    rubric_id: str | None = None
    force: bool = False


class RankedOpportunityItem(BaseModel):
    """Compact summary of a ranked opportunity for explorer tables."""
    model_config = ConfigDict(extra="ignore")

    rank: int
    evaluation_id: str
    canonical_job_id: str
    job_title: str
    company_name: str
    location: str | None = None
    work_arrangement: str | None = None
    employment_type: str | None = None
    eligibility_outcome: MatchingOutcome
    relevance_index: float
    mandatory_coverage_ratio: float
    preferred_coverage_ratio: float
    critical_gaps_count: int
    unknowns_count: int
    application_readiness: ApplicationReadiness
    posting_discovered_at: str | None = None
    last_evaluated_at: str


class RankingOverview(BaseModel):
    """High-level statistics for matching dashboard."""
    model_config = ConfigDict(extra="ignore")

    total_evaluated: int = 0
    eligible_and_aligned: int = 0
    conditionally_eligible: int = 0
    requires_review: int = 0
    known_unmet: int = 0
    hard_policy_excluded: int = 0
    average_relevance_index: float = 0.0
    latest_evaluation_at: str | None = None


class JobComparisonMatrix(BaseModel):
    """Side-by-side comparison of candidate jobs."""
    model_config = ConfigDict(extra="ignore")

    canonical_job_ids: list[str]
    items: list[dict[str, Any]]


class SimulationRequest(BaseModel):
    """What-If scenario simulation request."""
    model_config = ConfigDict(extra="ignore")

    evaluation_id: str
    scenario_name: str
    hypothetical_skills: list[str] = Field(default_factory=list)
    hypothetical_min_salary: float | None = None
    hypothetical_work_arrangement: str | None = None
    hypothetical_confirm_work_auth: bool | None = None
    hypothetical_graduation_status: str | None = None


class SimulationResponse(BaseModel):
    """Result of What-If simulation without persisting changes."""
    model_config = ConfigDict(extra="ignore")

    simulation_id: str = Field(default_factory=generate_uuid)
    evaluation_id: str
    scenario_name: str
    original_relevance_index: float
    simulated_relevance_index: float
    original_eligibility: MatchingOutcome
    simulated_eligibility: MatchingOutcome
    diff_explanation: str
    dimension_diffs: list[dict[str, Any]] = Field(default_factory=list)
    remaining_gaps: list[SkillGapItem] = Field(default_factory=list)


class ReviewResolutionRequest(BaseModel):
    """Payload to resolve or defer a matching review request."""
    model_config = ConfigDict(extra="ignore")

    resolution_notes: str
    decision: str  # resolved, deferred, dismissed
    reviewer_id: str = "user"
