"""Domain contracts, enums, and Pydantic schemas for Recruitment Policy & Career Preferences (Stage 25)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class RoleFamily(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULL_STACK = "full_stack"
    AI_ML = "ai_ml"
    DATA_ENGINEERING = "data_engineering"
    DATA_SCIENCE = "data_science"
    CLOUD_DEVOPS = "cloud_devops"
    CYBERSECURITY = "cybersecurity"
    RESEARCH = "research"
    MOBILE = "mobile"
    SYSTEMS = "systems"
    PRODUCT_MANAGEMENT = "product_management"
    OTHER = "other"


class SeniorityLevel(StrEnum):
    INTERNSHIP = "internship"
    APPRENTICE = "apprentice"
    GRADUATE_TRAINEE = "graduate_trainee"
    ENTRY_LEVEL = "entry_level"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    MANAGEMENT = "management"
    RESEARCH_FELLOWSHIP = "research_fellowship"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    APPRENTICESHIP = "apprenticeship"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    FREELANCE = "freelance"
    GRADUATE_PROGRAM = "graduate_program"
    RESEARCH_ROLE = "research_role"


class WorkArrangement(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"
    UNKNOWN = "unknown"


class RelocationPreference(StrEnum):
    WILLING = "willing"
    CONDITIONAL = "conditional"
    NOT_WILLING = "not_willing"
    UNDECIDED = "undecided"


class CompensationUnit(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    FIXED_CONTRACT = "fixed_contract"
    STIPEND = "stipend"


class CompensationMatchStatus(StrEnum):
    MEETS_MINIMUM = "meets_minimum"
    WITHIN_PREFERRED_RANGE = "within_preferred_range"
    BELOW_MINIMUM = "below_minimum"
    ABOVE_PREFERRED_RANGE = "above_preferred_range"
    COMPENSATION_UNKNOWN = "compensation_unknown"
    NOT_COMPARABLE = "not_comparable"


class UndisclosedSalaryHandling(StrEnum):
    CONSIDER = "consider"
    REQUIRE_REVIEW = "require_review"
    EXCLUDE = "exclude"


class AllowlistMode(StrEnum):
    NO_ALLOWLIST = "no_allowlist"
    PREFER_ALLOWLIST = "prefer_allowlist"
    STRICT_ALLOWLIST = "strict_allowlist"


class CompanySize(StrEnum):
    STARTUP = "startup"
    SMALL_BUSINESS = "small_business"
    MEDIUM_ENTERPRISE = "medium_enterprise"
    LARGE_ENTERPRISE = "large_enterprise"
    ANY_SIZE = "any_size"
    UNKNOWN = "unknown"


class EligibilityOutcome(StrEnum):
    MEETS_KNOWN_REQUIREMENTS = "meets_known_requirements"
    DOES_NOT_MEET_REQUIREMENT = "does_not_meet_requirement"
    UNKNOWN = "unknown"
    NEEDS_USER_CONFIRMATION = "needs_user_confirmation"
    CONFLICTING_INFORMATION = "conflicting_information"
    NOT_EVALUATED = "not_evaluated"


class SkillMatchCategory(StrEnum):
    DIRECT_MATCH = "direct_match"
    RELATED_EXPERIENCE = "related_experience"
    NOT_EVIDENCED = "not_evidenced"
    UNKNOWN = "unknown"


class PolicyDecisionOutcome(StrEnum):
    PROCEED = "proceed"
    PROCEED_WITH_CONDITIONS = "proceed_with_conditions"
    NEEDS_REVIEW = "needs_review"
    REJECTED_BY_PREFERENCE = "rejected_by_preference"
    INELIGIBLE = "ineligible"
    PROHIBITED_BY_POLICY = "prohibited_by_policy"
    INSUFFICIENT_INFORMATION = "insufficient_information"
    EVALUATION_FAILED = "evaluation_failed"


class AutonomyMode(StrEnum):
    RESEARCH_ONLY = "research_only"
    PREPARE_AND_REVIEW = "prepare_and_review"
    PREAUTHORIZED_PREPARATION = "preauthorized_preparation"
    BOUNDED_AUTONOMOUS_APPLICATIONS = "bounded_autonomous_applications"


class ReviewTrigger(StrEnum):
    SENSITIVE_ATTESTATION = "sensitive_attestation"
    WORK_AUTH_UNCERTAIN = "work_auth_uncertain"
    SPONSORSHIP_UNCERTAIN = "sponsorship_uncertain"
    COMPENSATION_BELOW_MIN = "compensation_below_min"
    COMPENSATION_UNDISCLOSED = "compensation_undisclosed"
    EMPLOYER_IDENTITY_UNCERTAIN = "employer_identity_uncertain"
    EMPLOYER_NEW = "employer_new"
    UNVERIFIED_QUALIFICATION = "unverified_qualification"
    SOURCE_RESTRICTION = "source_restriction"
    OUTCOME_UNCERTAIN = "outcome_uncertain"
    MISSING_APPROVED_RESUME = "missing_approved_resume"
    FACT_CONFLICT = "fact_conflict"


class ConflictSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"
    BLOCKING = "blocking"


# =============================================================================
# Models: Preferences & Strategies
# =============================================================================

class TargetRoleItem(BaseModel):
    id: str = Field(default_factory=lambda: f"role_{uuid4().hex[:8]}")
    title: str = Field(description="Normalized or preferred role title")
    role_family: RoleFamily = Field(default=RoleFamily.BACKEND)
    seniority: SeniorityLevel = Field(default=SeniorityLevel.MID_LEVEL)
    is_excluded: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=10, description="1 is highest priority")
    alternate_titles: list[str] = Field(default_factory=list)


class SeniorityPreference(BaseModel):
    allowed_levels: list[SeniorityLevel] = Field(default_factory=lambda: [SeniorityLevel.ENTRY_LEVEL, SeniorityLevel.JUNIOR, SeniorityLevel.MID_LEVEL])
    min_years: Optional[float] = Field(default=0.0, ge=0)
    max_years: Optional[float] = Field(default=None, ge=0)
    accept_academic_as_experience: bool = Field(default=False)


class WorkArrangementPreference(BaseModel):
    allowed_arrangements: list[WorkArrangement] = Field(default_factory=lambda: [WorkArrangement.REMOTE, WorkArrangement.HYBRID])
    preferred_arrangement: WorkArrangement = Field(default=WorkArrangement.REMOTE)
    is_hard_constraint: bool = Field(default=False, description="If True, disallowed arrangements are strictly blocked")


class GeographicPreference(BaseModel):
    country: str = Field(default="United States")
    allowed_countries: list[str] = Field(default_factory=lambda: ["United States"])
    allowed_states: list[str] = Field(default_factory=list)
    allowed_cities: list[str] = Field(default_factory=list)
    excluded_locations: list[str] = Field(default_factory=list)
    remote_within_country_only: bool = Field(default=True)
    relocation: RelocationPreference = Field(default=RelocationPreference.UNDECIDED)
    preferred_time_zone: str = Field(default="America/New_York")
    max_hour_offset: int = Field(default=3, ge=0, le=24)
    min_overlap_hours: int = Field(default=4, ge=0, le=12)


class CompensationPolicy(BaseModel):
    currency: str = Field(default="USD")
    unit: CompensationUnit = Field(default=CompensationUnit.ANNUAL)
    min_acceptable_amount: Decimal = Field(default=Decimal("80000.00"), ge=0)
    preferred_min: Decimal = Field(default=Decimal("100000.00"), ge=0)
    preferred_max: Optional[Decimal] = Field(default=Decimal("150000.00"), ge=0)
    undisclosed_handling: UndisclosedSalaryHandling = Field(default=UndisclosedSalaryHandling.REQUIRE_REVIEW)
    is_hard_minimum: bool = Field(default=True, description="Strictly rejects positions offering below min_acceptable_amount")
    hours_per_week_assumption: int = Field(default=40, ge=1, le=80)
    weeks_per_year_assumption: int = Field(default=52, ge=1, le=52)


class BlockedEmployerItem(BaseModel):
    id: str = Field(default_factory=lambda: f"blk_{uuid4().hex[:8]}")
    employer_name: str
    domain: Optional[str] = None
    reason: Optional[str] = None
    effective_from: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmployerRestrictions(BaseModel):
    allowlist_mode: AllowlistMode = Field(default=AllowlistMode.NO_ALLOWLIST)
    allowed_employers: list[str] = Field(default_factory=list)
    blocked_employers: list[BlockedEmployerItem] = Field(default_factory=list)
    company_sizes: list[CompanySize] = Field(default_factory=lambda: [CompanySize.STARTUP, CompanySize.MEDIUM_ENTERPRISE, CompanySize.LARGE_ENTERPRISE])
    preferred_industries: list[str] = Field(default_factory=lambda: ["Software", "AI/ML", "Fintech"])
    acceptable_industries: list[str] = Field(default_factory=list)
    excluded_industries: list[str] = Field(default_factory=list)


class SourceRestrictions(BaseModel):
    allowed_sources: list[str] = Field(default_factory=lambda: ["company_website", "greenhouse", "lever", "workday", "ashby"])
    blocked_sources: list[str] = Field(default_factory=list)
    review_required_sources: list[str] = Field(default_factory=lambda: ["unverified_job_board"])


class CareerStrategy(BaseModel):
    id: str = Field(default_factory=lambda: f"strat_{uuid4().hex[:8]}")
    owner_id: str = Field(default="usr_01")
    profile_id: str = Field(default="prof_01")
    title: str = Field(description="Strategy name (e.g. 'Backend Systems Focus')")
    description: Optional[str] = None
    is_active: bool = Field(default=False)
    target_roles: list[TargetRoleItem] = Field(default_factory=list)
    seniority: SeniorityPreference = Field(default_factory=SeniorityPreference)
    employment_types: list[EmploymentType] = Field(default_factory=lambda: [EmploymentType.FULL_TIME])
    work_arrangement: WorkArrangementPreference = Field(default_factory=WorkArrangementPreference)
    geography: GeographicPreference = Field(default_factory=GeographicPreference)
    compensation: CompensationPolicy = Field(default_factory=CompensationPolicy)
    employers: EmployerRestrictions = Field(default_factory=EmployerRestrictions)
    sources: SourceRestrictions = Field(default_factory=SourceRestrictions)
    max_posting_age_days: int = Field(default=30, ge=1, le=180)
    autonomy_mode: AutonomyMode = Field(default=AutonomyMode.PREPARE_AND_REVIEW)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CareerPreferenceProfile(BaseModel):
    id: str = Field(default_factory=lambda: f"cprof_{uuid4().hex[:8]}")
    owner_id: str
    applicant_profile_id: str
    active_strategy_id: Optional[str] = None
    strategies: list[CareerStrategy] = Field(default_factory=list)
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Models: Job Input & Eligibility
# =============================================================================

class JobOpportunityContext(BaseModel):
    """Synthetic or discovered job record submitted for policy and eligibility evaluation."""
    id: str = Field(default_factory=lambda: f"job_{uuid4().hex[:8]}")
    title: str
    employer_name: str
    employer_domain: Optional[str] = None
    role_family: Optional[RoleFamily] = None
    seniority: Optional[SeniorityLevel] = None
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    work_arrangement: WorkArrangement = Field(default=WorkArrangement.HYBRID)
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: str = Field(default="United States")
    remote_country_restriction: Optional[str] = None
    compensation_min: Optional[Decimal] = None
    compensation_max: Optional[Decimal] = None
    compensation_currency: Optional[str] = "USD"
    compensation_unit: Optional[CompensationUnit] = CompensationUnit.ANNUAL
    required_education_level: Optional[str] = None  # e.g. "Bachelor's", "Master's"
    degree_must_be_completed: bool = False
    required_field_of_study: Optional[str] = None
    requires_current_student_enrollment: bool = False
    required_experience_years: Optional[float] = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    required_certifications: list[str] = Field(default_factory=list)
    work_authorization_required: bool = True
    visa_sponsorship_offered: bool = False
    earliest_start_date: Optional[str] = None
    industry: Optional[str] = None
    company_size: CompanySize = Field(default=CompanySize.UNKNOWN)
    source_platform: str = Field(default="company_website")
    posted_date: Optional[datetime] = None
    is_duplicate: bool = False
    already_applied: bool = False


class EligibilityCategoryResult(BaseModel):
    category: str
    outcome: EligibilityOutcome
    explanation: str
    matched_facts: list[str] = Field(default_factory=list)
    missing_facts: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class JobEligibilityAssessment(BaseModel):
    is_eligible_known: bool
    has_blocking_disqualification: bool
    categories: dict[str, EligibilityCategoryResult] = Field(default_factory=dict)
    summary_explanation: str
    unknown_items: list[str] = Field(default_factory=list)
    review_triggers: list[ReviewTrigger] = Field(default_factory=list)


# =============================================================================
# Models: Rules, Precedence & Decisions
# =============================================================================

class HardConstraintEvaluation(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    reason: str
    failure_outcome: PolicyDecisionOutcome = Field(default=PolicyDecisionOutcome.PROHIBITED_BY_POLICY)


class SoftPreferenceEvaluation(BaseModel):
    preference_name: str
    weight: float = 1.0
    score: float = 100.0  # 0 to 100
    matched_elements: list[str] = Field(default_factory=list)
    explanation: str


class PolicyConflictItem(BaseModel):
    id: str = Field(default_factory=lambda: f"cfl_{uuid4().hex[:8]}")
    title: str
    description: str
    rules_involved: list[str]
    severity: ConflictSeverity = Field(default=ConflictSeverity.ERROR)
    suggested_resolution: str


class RecruitmentDecision(BaseModel):
    id: str = Field(default_factory=lambda: f"dec_{uuid4().hex[:8]}")
    job_id: str
    job_title: str
    employer: str
    strategy_id: str
    policy_version: int
    decision: PolicyDecisionOutcome
    overall_score: float = Field(default=0.0, ge=0.0, le=100.0)
    eligibility_assessment: JobEligibilityAssessment
    hard_constraints: list[HardConstraintEvaluation] = Field(default_factory=list)
    soft_preferences: list[SoftPreferenceEvaluation] = Field(default_factory=list)
    precedence_rule_applied: str
    review_triggers: list[ReviewTrigger] = Field(default_factory=list)
    permitted_future_actions: list[str] = Field(default_factory=list)
    denied_future_actions: list[str] = Field(default_factory=list)
    explanation: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Models: Budgets, Review Queue, Autonomy & Standing Grants
# =============================================================================

class RecruitmentBudget(BaseModel):
    id: str = Field(default_factory=lambda: f"bud_{uuid4().hex[:8]}")
    owner_id: str
    strategy_id: Optional[str] = None
    max_daily_applications: int = Field(default=25, ge=1, le=500)
    max_weekly_applications: int = Field(default=100, ge=1, le=2000)
    max_monthly_applications: int = Field(default=350, ge=1, le=8000)
    max_simultaneous_applications: int = Field(default=5, ge=1, le=50)
    max_per_employer_period: int = Field(default=3, ge=1, le=20)
    max_per_platform_period: int = Field(default=15, ge=1, le=200)

    # State counters (managed transactionally)
    daily_reserved: int = Field(default=0, ge=0)
    daily_confirmed: int = Field(default=0, ge=0)
    weekly_confirmed: int = Field(default=0, ge=0)
    monthly_confirmed: int = Field(default=0, ge=0)
    employer_counts: dict[str, int] = Field(default_factory=dict)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    last_reset_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def remaining_daily(self) -> int:
        return max(0, self.max_daily_applications - (self.daily_reserved + self.daily_confirmed))

    @property
    def remaining_weekly(self) -> int:
        return max(0, self.max_weekly_applications - self.weekly_confirmed)

    @property
    def remaining_monthly(self) -> int:
        return max(0, self.max_monthly_applications - self.monthly_confirmed)


class ReviewQueueItem(BaseModel):
    id: str = Field(default_factory=lambda: f"rev_{uuid4().hex[:8]}")
    job_id: str
    job_title: str
    employer: str
    trigger: ReviewTrigger
    reason: str
    is_mandatory: bool = True
    status: str = Field(default="pending", description="pending, confirmed, dismissed, overridden")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class StandingGrantRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"grant_{uuid4().hex[:8]}")
    grantee_agent: str
    action_type: str = Field(default="recruitment.application.prepare")
    target_employers: list[str] = Field(default_factory=list)
    target_platforms: list[str] = Field(default_factory=list)
    allowed_locations: list[str] = Field(default_factory=list)
    max_operations: int = Field(default=50, ge=1)
    operations_used: int = Field(default=0, ge=0)
    is_revoked: bool = False
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PolicyVersionSnapshot(BaseModel):
    version: int
    strategy_id: str
    sha256_hash: str
    changelog: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    author_id: str = "usr_01"
    strategy_snapshot: dict[str, Any]


# =============================================================================
# Request / Response DTOs
# =============================================================================

class CareerStrategyCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = False
    target_roles: list[TargetRoleItem] = Field(default_factory=list)
    seniority: Optional[SeniorityPreference] = None
    employment_types: Optional[list[EmploymentType]] = None
    work_arrangement: Optional[WorkArrangementPreference] = None
    geography: Optional[GeographicPreference] = None
    compensation: Optional[CompensationPolicy] = None
    employers: Optional[EmployerRestrictions] = None
    sources: Optional[SourceRestrictions] = None
    max_posting_age_days: int = 30
    autonomy_mode: AutonomyMode = AutonomyMode.PREPARE_AND_REVIEW


class CareerStrategyUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    target_roles: Optional[list[TargetRoleItem]] = None
    seniority: Optional[SeniorityPreference] = None
    employment_types: Optional[list[EmploymentType]] = None
    work_arrangement: Optional[WorkArrangementPreference] = None
    geography: Optional[GeographicPreference] = None
    compensation: Optional[CompensationPolicy] = None
    employers: Optional[EmployerRestrictions] = None
    sources: Optional[SourceRestrictions] = None
    max_posting_age_days: Optional[int] = None
    autonomy_mode: Optional[AutonomyMode] = None


class JobPolicyEvaluationRequest(BaseModel):
    job: JobOpportunityContext
    strategy_id: Optional[str] = None
    profile_id: Optional[str] = None


class PolicySimulationRequest(BaseModel):
    synthetic_job: JobOpportunityContext
    strategy_id: Optional[str] = None
    profile_id: Optional[str] = None
    override_policy: Optional[CareerStrategyUpdateRequest] = None


class PolicySimulationResponse(BaseModel):
    decision: RecruitmentDecision
    strategy_title: str
    policy_version: int
    detected_conflicts: list[PolicyConflictItem] = Field(default_factory=list)
    simulation_notes: str


class BudgetReservationRequest(BaseModel):
    job_id: str
    employer: str
    platform: str
    agent_id: str


class BudgetReservationResponse(BaseModel):
    reservation_id: str
    is_reserved: bool
    remaining_daily: int
    remaining_weekly: int
    remaining_monthly: int
    failure_reason: Optional[str] = None


class ReviewResolutionRequest(BaseModel):
    status: str = Field(description="confirmed, dismissed, overridden")
    notes: Optional[str] = None
