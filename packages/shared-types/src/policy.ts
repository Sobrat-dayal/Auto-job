/**
 * AUTONOM Career Preferences, Job Eligibility & Recruitment Policy Shared Types (Stage 25)
 */

export type RoleFamily =
  | 'software_engineering'
  | 'backend'
  | 'frontend'
  | 'fullstack'
  | 'mobile'
  | 'cloud_devops'
  | 'ai_ml_engineering'
  | 'ai_research'
  | 'data_engineering'
  | 'data_science'
  | 'cybersecurity'
  | 'systems_embedded'
  | 'product_management'
  | 'engineering_management'
  | 'other';

export type SeniorityLevel =
  | 'internship'
  | 'entry_level'
  | 'junior'
  | 'mid_level'
  | 'senior'
  | 'staff'
  | 'principal'
  | 'lead'
  | 'manager'
  | 'director';

export type EmploymentType =
  | 'full_time'
  | 'part_time'
  | 'contract'
  | 'internship'
  | 'co_op'
  | 'freelance';

export type WorkArrangement =
  | 'remote'
  | 'hybrid'
  | 'onsite'
  | 'flexible';

export type RelocationPreference =
  | 'not_willing'
  | 'willing_domestic'
  | 'willing_international'
  | 'remote_only'
  | 'open';

export type CompensationUnit =
  | 'hourly'
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'annual'
  | 'stipend';

export type CompensationMatchStatus =
  | 'meets_or_exceeds'
  | 'below_target'
  | 'below_hard_floor'
  | 'undisclosed'
  | 'not_comparable';

export type UndisclosedSalaryHandling =
  | 'consider'
  | 'require_review'
  | 'exclude';

export type AllowlistMode =
  | 'no_allowlist'
  | 'prefer_allowlist'
  | 'strict_allowlist';

export type CompanySize =
  | 'startup_seed'
  | 'early_stage'
  | 'growth'
  | 'mid_market'
  | 'enterprise'
  | 'faang_big_tech';

export type EligibilityOutcome =
  | 'eligible'
  | 'ineligible'
  | 'needs_review'
  | 'insufficient_evidence';

export type PolicyDecisionOutcome =
  | 'proceed'
  | 'proceed_with_conditions'
  | 'needs_review'
  | 'rejected_by_preference'
  | 'ineligible'
  | 'prohibited_by_policy';

export type AutonomyMode =
  | 'mode_1_research_only'
  | 'mode_2_prepare_and_review'
  | 'mode_3_preauthorized_preparation'
  | 'mode_4_bounded_autonomous_applications';

export type ReviewTrigger =
  | 'compensation_undisclosed'
  | 'compensation_below_floor'
  | 'employer_ambiguous'
  | 'work_auth_uncertain'
  | 'experience_below_threshold'
  | 'unverified_qualifications_requested'
  | 'sensitive_question_detected'
  | 'mode_2_default_review'
  | 'budget_threshold_warning'
  | 'policy_conflict_detected'
  | 'custom_user_rule';

export interface TargetRoleItem {
  title: string;
  role_family: RoleFamily;
  seniority: SeniorityLevel;
  keywords: string[];
  excluded_keywords: string[];
  is_primary: boolean;
  priority_weight: number;
}

export interface SeniorityPreference {
  target_levels: SeniorityLevel[];
  minimum_level?: SeniorityLevel;
  maximum_level?: SeniorityLevel;
  strict_enforcement: boolean;
}

export interface WorkArrangementPreference {
  allowed_arrangements: WorkArrangement[];
  preferred_arrangement: WorkArrangement;
  max_commute_miles?: number;
  max_hybrid_days_onsite?: number;
  strict_enforcement: boolean;
}

export interface GeographicPreference {
  preferred_countries: string[];
  preferred_states_provinces: string[];
  preferred_cities: string[];
  excluded_countries: string[];
  excluded_states_provinces: string[];
  excluded_cities: string[];
  relocation: RelocationPreference;
  allowed_timezones: string[];
  max_timezone_offset_hours?: number;
  strict_enforcement: boolean;
}

export interface CompensationPolicy {
  target_amount?: number;
  hard_floor_amount?: number;
  currency: string;
  unit: CompensationUnit;
  undisclosed_handling: UndisclosedSalaryHandling;
  equity_required: boolean;
  benefits_required: string[];
  strict_enforcement: boolean;
}

export interface BlockedEmployerItem {
  name: string;
  normalized_name?: string;
  domain?: string;
  reason: string;
  blocked_at: string;
}

export interface AllowedEmployerItem {
  name: string;
  domain?: string;
  priority_tier: number;
  notes?: string;
}

export interface EmployerRestrictions {
  allowlist_mode: AllowlistMode;
  allowed_employers: AllowedEmployerItem[];
  blocked_employers: BlockedEmployerItem[];
  blocked_industries: string[];
  blocked_parent_companies: string[];
  target_company_sizes: CompanySize[];
  require_review_on_ambiguous: boolean;
}

export interface SourceRestrictions {
  allowed_job_boards: string[];
  blocked_job_boards: string[];
  allow_direct_employer_sites: boolean;
  allow_third_party_recruiters: boolean;
  allow_sponsored_listings: boolean;
  require_review_on_unknown_source: boolean;
}

export interface EligibilityRulesConfig {
  enforce_degree_requirements: boolean;
  allow_enrolled_for_future_grads: boolean;
  enforce_work_authorization: boolean;
  enforce_minimum_experience: boolean;
  enforce_required_certifications: boolean;
  minimum_skill_match_percentage: number;
  require_evidenced_skills: boolean;
}

export interface CareerStrategy {
  id: string;
  owner_id: string;
  title: string;
  description?: string;
  is_active: boolean;
  target_roles: TargetRoleItem[];
  seniority: SeniorityPreference;
  employment_types: EmploymentType[];
  work_arrangement: WorkArrangementPreference;
  geography: GeographicPreference;
  compensation: CompensationPolicy;
  employers: EmployerRestrictions;
  sources: SourceRestrictions;
  eligibility_rules: EligibilityRulesConfig;
  max_posting_age_days?: number;
  autonomy_mode: AutonomyMode;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface StandingGrantRecord {
  id: string;
  owner_id: string;
  grantee_role: string;
  scope: string;
  max_actions_per_day: number;
  actions_taken_today: number;
  conditions: Record<string, any>;
  issued_at: string;
  expires_at?: string;
  is_revoked: boolean;
  revocation_reason?: string;
}

export interface CareerPreferenceProfile {
  applicant_id: string;
  active_strategy_id: string;
  strategies: CareerStrategy[];
  standing_grants: StandingGrantRecord[];
  global_employer_blocklist: BlockedEmployerItem[];
  updated_at: string;
}

export interface JobOpportunityContext {
  id: string;
  title: string;
  employer_name: string;
  employer_domain?: string;
  job_board_source?: string;
  role_family?: RoleFamily;
  seniority?: SeniorityLevel;
  employment_type?: EmploymentType;
  work_arrangement: WorkArrangement;
  location_city?: string;
  location_state?: string;
  location_country?: string;
  timezone?: string;
  compensation_min?: number;
  compensation_max?: number;
  compensation_currency?: string;
  compensation_unit?: CompensationUnit;
  required_skills: string[];
  preferred_skills: string[];
  required_degree?: string;
  required_experience_years?: number;
  work_authorization_required: boolean;
  requires_sponsorship?: boolean;
  url?: string;
  raw_description?: string;
  posted_date?: string;
}

export interface JobEligibilityAssessment {
  job_id: string;
  outcome: EligibilityOutcome;
  overall_score: number;
  education_matched: boolean;
  education_notes?: string;
  experience_years_required: number;
  experience_years_verified: number;
  experience_matched: boolean;
  experience_notes?: string;
  skills_required_count: number;
  skills_matched_count: number;
  skills_evidenced_count: number;
  skill_match_percentage: number;
  missing_critical_skills: string[];
  certifications_matched: boolean;
  work_authorization_valid: boolean;
  work_auth_notes?: string;
  evaluated_at: string;
}

export interface RecruitmentDecision {
  id: string;
  job_id: string;
  job_title: string;
  employer_name: string;
  decision: PolicyDecisionOutcome;
  precedence_level: number;
  primary_rationale: string;
  reasons: string[];
  violations: string[];
  review_triggers: ReviewTrigger[];
  soft_preference_score: number;
  eligibility_assessment?: JobEligibilityAssessment;
  compensation_match_status: CompensationMatchStatus;
  normalized_annual_salary?: number;
  recommended_action: string;
  evaluated_at: string;
}

export interface RecruitmentBudget {
  daily_application_limit: number;
  weekly_application_limit: number;
  monthly_application_limit: number;
  daily_applications_count: number;
  weekly_applications_count: number;
  monthly_applications_count: number;
  active_reservations_count: number;
  daily_discovery_limit: number;
  daily_preparations_limit: number;
  daily_discoveries_count: number;
  daily_preparations_count: number;
  last_daily_reset: string;
  last_weekly_reset: string;
  last_monthly_reset: string;
}

export interface ReviewQueueItem {
  id: string;
  job_id: string;
  job_title: string;
  employer_name: string;
  triggers: ReviewTrigger[];
  decision_summary: string;
  context_payload: Record<string, any>;
  status: 'pending' | 'approved' | 'rejected' | 'dismissed';
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
  user_notes?: string;
}

export interface PolicyVersionSnapshot {
  version: number;
  strategy_id: string;
  owner_id: string;
  snapshot_hash: string;
  strategy_payload: Record<string, any>;
  change_summary: string;
  created_at: string;
}

// DTOs & API Contracts
export interface CareerStrategyCreateRequest {
  title: string;
  description?: string;
  is_active?: boolean;
  target_roles?: TargetRoleItem[];
  seniority?: SeniorityPreference;
  employment_types?: EmploymentType[];
  work_arrangement?: WorkArrangementPreference;
  geography?: GeographicPreference;
  compensation?: CompensationPolicy;
  employers?: EmployerRestrictions;
  sources?: SourceRestrictions;
  eligibility_rules?: EligibilityRulesConfig;
  max_posting_age_days?: number;
  autonomy_mode?: AutonomyMode;
}

export interface CareerStrategyUpdateRequest {
  title?: string;
  description?: string;
  is_active?: boolean;
  target_roles?: TargetRoleItem[];
  seniority?: SeniorityPreference;
  employment_types?: EmploymentType[];
  work_arrangement?: WorkArrangementPreference;
  geography?: GeographicPreference;
  compensation?: CompensationPolicy;
  employers?: EmployerRestrictions;
  sources?: SourceRestrictions;
  eligibility_rules?: EligibilityRulesConfig;
  max_posting_age_days?: number;
  autonomy_mode?: AutonomyMode;
}

export interface PolicySimulationRequest {
  synthetic_job: Partial<JobOpportunityContext> & { title: string; employer_name: string };
  strategy_override?: Partial<CareerStrategy>;
  applicant_profile_id?: string;
}

export interface PolicySimulationResponse {
  synthetic_job: Partial<JobOpportunityContext>;
  decision: RecruitmentDecision;
  simulated_at: string;
}

export interface PolicyConflictCheckRequest {
  strategy?: CareerStrategy;
}

export interface PolicyConflictReport {
  has_conflicts: boolean;
  conflicts: string[];
  warnings: string[];
  recommendations: string[];
}

export interface BudgetReservationRequest {
  agent_id: string;
  job_id: string;
  ttl_seconds?: number;
}

export interface BudgetReservationResponse {
  success: boolean;
  reservation_id?: string;
  reason?: string;
  remaining_daily: number;
}

export interface BudgetConfirmationRequest {
  reservation_id: string;
  agent_id: string;
  job_id: string;
}

export interface BudgetReleaseRequest {
  reservation_id: string;
  reason?: string;
}

export interface StandingGrantCreateRequest {
  grantee_role: string;
  scope: string;
  max_actions_per_day: number;
  conditions?: Record<string, any>;
  expires_in_hours?: number;
}

export interface AutonomyStatusResponse {
  active_autonomy_mode: AutonomyMode;
  active_strategy_id?: string;
  active_strategy_title?: string;
  standing_grants_count: number;
  pending_review_queue_count: number;
  capabilities: Record<string, boolean>;
}

export interface ReviewQueueResolutionRequest {
  action: 'approve' | 'reject' | 'dismiss';
  user_notes?: string;
}

export interface PolicyDiagnosticsResponse {
  status: string;
  total_strategies: number;
  active_strategy_id?: string;
  active_autonomy_mode: AutonomyMode;
  total_decisions_logged: number;
  standing_grants_active: number;
  pending_reviews: number;
  budget_status: {
    daily_applications_count: number;
    daily_application_limit: number;
    active_reservations: number;
  };
}
