/**
 * Strongly-typed contracts for Applicant-to-Job Matching Engine (Stage 29).
 */

export type MatchingOutcome =
  | 'eligible_and_aligned'
  | 'eligible_but_lower_priority'
  | 'conditionally_eligible'
  | 'requires_applicant_review'
  | 'missing_critical_information'
  | 'known_requirement_not_met'
  | 'rejected_by_hard_policy'
  | 'blocked_by_authorization'
  | 'job_unavailable'
  | 'match_evaluation_failed'
  | 'not_evaluated';

export type JobMatchRequirementCategory =
  | 'directly_satisfied'
  | 'satisfied_by_alternative'
  | 'partially_supported'
  | 'related_experience_only'
  | 'not_evidenced'
  | 'known_not_satisfied'
  | 'unknown'
  | 'not_applicable'
  | 'conflicted';

export type MatchCategory = JobMatchRequirementCategory;

export type GapSeverity =
  | 'blocking'
  | 'critical_review'
  | 'significant'
  | 'moderate'
  | 'minor'
  | 'informational'
  | 'unknown';

export type GapType =
  | 'missing_mandatory_skill'
  | 'missing_preferred_skill'
  | 'duration_deficit'
  | 'related_only'
  | 'missing_evidence'
  | 'ambiguous_requirement'
  | 'unverified_claim';

export type ApplicationReadiness =
  | 'ready_for_preparation'
  | 'requires_review'
  | 'ineligible'
  | 'hard_policy_excluded'
  | 'unavailable'
  | 'not_evaluated';

export type ReviewType =
  | 'unknown_work_auth'
  | 'ambiguous_alternative'
  | 'conflicting_claims'
  | 'unverified_mandatory_skill'
  | 'compensation_uncertainty'
  | 'location_conflict'
  | 'duplicate_risk'
  | 'stale_job';

export interface RequirementEvaluationResult {
  requirement_id: string;
  name: string;
  category: string;
  match_category: JobMatchRequirementCategory;
  applicant_claim_ref?: string | null;
  applicant_evidence_snippet?: string | null;
  job_evidence_snippet?: string | null;
  confidence: number;
  explanation: string;
  is_satisfied: boolean;
}

export interface GroupEvaluationResult {
  group_id: string;
  operator: string;
  target_count: number;
  satisfied_count: number;
  is_satisfied: boolean;
  is_unknown: boolean;
  explanation: string;
}

export interface SkillMatchDetail {
  skill_name: string;
  canonical_name: string;
  category: string;
  priority: string;
  required_years?: number | null;
  applicant_years?: number | null;
  applicant_proficiency?: string | null;
  match_status: JobMatchRequirementCategory;
  is_alias_match: boolean;
  is_related_match: boolean;
  explanation: string;
}

export interface EducationMatchDetail {
  degree_level: string;
  field_of_study: string;
  applicant_degree?: string | null;
  applicant_field?: string | null;
  applicant_status?: string | null;
  status_compatible: boolean;
  field_compatible: boolean;
  match_status: JobMatchRequirementCategory;
  explanation: string;
}

export interface ExperienceMatchDetail {
  required_min_years?: number | null;
  required_max_years?: number | null;
  required_domain?: string | null;
  calculated_professional_years: number;
  total_calendar_months_non_overlapping: number;
  has_overlapping_roles: boolean;
  internship_months: number;
  academic_project_count: number;
  match_status: JobMatchRequirementCategory;
  explanation: string;
}

export interface EligibilityConditionDetail {
  work_authorization_status: string;
  sponsorship_status: string;
  remote_compatibility: string;
  location_compatibility: string;
  relocation_compatibility: string;
  compensation_compatibility: string;
  employer_restriction_status: string;
  hard_policy_passed: boolean;
  hard_policy_reason?: string | null;
  explanation: string;
}

export interface SkillGapItem {
  id: string;
  requirement_id?: string | null;
  skill_or_qualification: string;
  gap_type: GapType;
  severity: GapSeverity;
  description: string;
  remediation_suggestion: string;
}

export interface MissingInformationRequest {
  requirement_name: string;
  missing_fact: string;
  importance: string;
  suggested_profile_field: string;
}

export interface DimensionScore {
  dimension_id: string;
  name: string;
  raw_score: number;
  weight: number;
  weighted_score: number;
  max_possible_weighted_score: number;
  is_observed: boolean;
  explanation: string;
}

export interface RelevanceIndexBreakdown {
  relevance_index: number;
  total_weight_observed: number;
  dimensions: DimensionScore[];
  missing_dimensions: string[];
  formula_explanation: string;
}

export interface RubricConfig {
  id: string;
  version: number;
  name: string;
  description?: string | null;
  is_default: boolean;
  weights: Record<string, number>;
  missing_data_policy: string;
}

export interface CounterfactualScenario {
  scenario_name: string;
  hypothetical_change: string;
  current_state: string;
  simulated_state: string;
  impact_summary: string;
}

export interface JobMatchEvaluation {
  id: string;
  profile_id: string;
  canonical_job_id: string;
  job_title: string;
  company_name: string;
  job_location?: string | null;
  employment_type?: string | null;
  work_arrangement?: string | null;
  career_strategy_id?: string | null;
  rubric_id: string;
  version: number;
  is_current: boolean;
  status: string;
  eligibility_outcome: MatchingOutcome;
  relevance_index: number;
  mandatory_coverage_ratio: number;
  preferred_coverage_ratio: number;
  evidence_completeness_ratio: number;
  ranking_uncertainty_ratio: number;
  application_readiness: ApplicationReadiness;
  hard_policy_passed: boolean;
  hard_policy_reason?: string | null;
  summary_explanation: string;
  requirement_results: RequirementEvaluationResult[];
  group_results: GroupEvaluationResult[];
  skill_details: SkillMatchDetail[];
  education_detail?: EducationMatchDetail | null;
  experience_detail?: ExperienceMatchDetail | null;
  eligibility_detail: EligibilityConditionDetail;
  score_breakdown: RelevanceIndexBreakdown;
  gaps: SkillGapItem[];
  missing_information: MissingInformationRequest[];
  review_requests: Array<Record<string, any>>;
  counterfactuals: CounterfactualScenario[];
  evaluated_at: string;
  updated_at: string;
}

export interface MatchEvaluationRequest {
  profile_id?: string | null;
  canonical_job_id: string;
  career_strategy_id?: string | null;
  rubric_id?: string | null;
  force?: boolean;
  use_ai?: boolean;
}

export interface RankedOpportunityItem {
  rank: number;
  evaluation_id: string;
  canonical_job_id: string;
  job_title: string;
  company_name: string;
  location?: string | null;
  work_arrangement?: string | null;
  employment_type?: string | null;
  eligibility_outcome: MatchingOutcome;
  relevance_index: number;
  mandatory_coverage_ratio: number;
  preferred_coverage_ratio: number;
  critical_gaps_count: number;
  unknowns_count: number;
  application_readiness: ApplicationReadiness;
  posting_discovered_at?: string | null;
  last_evaluated_at: string;
}

export interface RankingOverview {
  total_evaluated: number;
  eligible_and_aligned: number;
  conditionally_eligible: number;
  requires_review: number;
  known_unmet: number;
  hard_policy_excluded: number;
  average_relevance_index: number;
  latest_evaluation_at?: string | null;
}

export interface JobComparisonMatrix {
  canonical_job_ids: string[];
  items: Array<Record<string, any>>;
}

export interface SimulationRequest {
  evaluation_id: string;
  scenario_name: string;
  hypothetical_skills?: string[];
  hypothetical_min_salary?: number | null;
  hypothetical_work_arrangement?: string | null;
  hypothetical_confirm_work_auth?: boolean | null;
  hypothetical_graduation_status?: string | null;
}

export interface SimulationResponse {
  simulation_id: string;
  evaluation_id: string;
  scenario_name: string;
  original_relevance_index: number;
  simulated_relevance_index: number;
  original_eligibility: MatchingOutcome;
  simulated_eligibility: MatchingOutcome;
  diff_explanation: string;
  dimension_diffs: Array<Record<string, any>>;
  remaining_gaps: SkillGapItem[];
}

export interface ReviewResolutionRequest {
  resolution_notes: string;
  decision: string;
  reviewer_id?: string;
}
