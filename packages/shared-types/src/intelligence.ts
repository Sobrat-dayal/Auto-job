/**
 * Shared TypeScript Contracts for Job Intelligence Engine (Stage 28).
 */

import type { EmploymentType } from './policy';

export type AnalysisStatus =
  | 'NotAnalyzed'
  | 'Queued'
  | 'LoadingSources'
  | 'Parsing'
  | 'Extracting'
  | 'Validating'
  | 'NeedsReview'
  | 'PartiallyAnalyzed'
  | 'Completed'
  | 'Failed'
  | 'Cancelled'
  | 'Outdated';

export type RequirementCategory =
  | 'Mandatory'
  | 'Preferred'
  | 'Optional'
  | 'Conditional'
  | 'Informational'
  | 'EmployerDescription'
  | 'ApplicantBenefit'
  | 'Unknown';

export type LogicalOperator =
  | 'AND'
  | 'OR'
  | 'NOT'
  | 'AtLeastN'
  | 'ALL'
  | 'ANY'
  | 'Conditional'
  | 'EquivalentAlternative'
  | 'UnknownRelation';

export type QualificationType =
  | 'TECHNICAL_SKILL'
  | 'EDUCATION'
  | 'EXPERIENCE'
  | 'CERTIFICATION'
  | 'LICENSE'
  | 'SECURITY_CLEARANCE'
  | 'WORK_AUTHORIZATION'
  | 'LANGUAGE'
  | 'SOFT_SKILL';

export type DegreeLevel =
  | 'HIGH_SCHOOL'
  | 'ASSOCIATE'
  | 'BACHELOR'
  | 'MASTER'
  | 'DOCTORATE'
  | 'PROFESSIONAL'
  | 'EQUIVALENT'
  | 'NOT_REQUIRED'
  | 'UNKNOWN';

export type DegreeStatus =
  | 'COMPLETED'
  | 'CURRENTLY_ENROLLED'
  | 'FINAL_YEAR'
  | 'GRADUATED_RECENTLY'
  | 'NOT_REQUIRED'
  | 'UNKNOWN';

export type WorkplaceType =
  | 'REMOTE_GLOBAL'
  | 'REMOTE_COUNTRY_ONLY'
  | 'HYBRID'
  | 'ONSITE'
  | 'FLEXIBLE'
  | 'UNKNOWN';

export type PayPeriod =
  | 'HOURLY'
  | 'DAILY'
  | 'WEEKLY'
  | 'BIWEEKLY'
  | 'MONTHLY'
  | 'ANNUAL'
  | 'STIPEND'
  | 'PROJECT'
  | 'UNKNOWN';

export type EvidenceConfidence =
  | 'EXPLICIT_VERIFIED_SOURCE'
  | 'EXPLICIT_UNVERIFIED'
  | 'STRONGLY_SUPPORTED'
  | 'AMBIGUOUS'
  | 'WEAK_INFERENCE'
  | 'NO_EVIDENCE';

export type ExtractionMethod =
  | 'DETERMINISTIC_RULES'
  | 'STRUCTURED_SCHEMA_ORG'
  | 'AI_EXTRACTION'
  | 'HYBRID'
  | 'MANUAL_ENTRY';

export type ReviewStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'MODIFIED' | 'NOT_NEEDED';

export type ConflictType =
  | 'DEGREE_REQUIREMENT'
  | 'WORK_ARRANGEMENT'
  | 'SALARY_RANGE'
  | 'VISA_SPONSORSHIP'
  | 'EXPERIENCE_DURATION'
  | 'OTHER';

export type ResolutionStrategy =
  | 'PENDING'
  | 'HIGHER_AUTHORITY_ACCEPTED'
  | 'NEWER_SOURCE_ACCEPTED'
  | 'MANUAL_OVERRIDE';

export type SkillCategory =
  | 'PROGRAMMING_LANGUAGE'
  | 'FRAMEWORK_LIBRARY'
  | 'DATABASE'
  | 'CLOUD_DEVOPS'
  | 'AI_ML'
  | 'TOOLS_PLATFORMS'
  | 'METHODOLOGY'
  | 'NON_TECHNICAL';

export interface RequirementEvidence {
  id: string;
  requirement_id?: string | null;
  section_name: string;
  supporting_text: string;
  start_char: number;
  end_char: number;
  quote_hash: string;
  extraction_method: ExtractionMethod;
  verified_in_source: boolean;
  created_at: string;
}

export interface AtomicRequirement {
  id: string;
  category: RequirementCategory;
  qualification_type: QualificationType;
  name: string;
  normalized_value: string;
  raw_text: string;
  min_years?: number | null;
  max_years?: number | null;
  is_negated: boolean;
  confidence: EvidenceConfidence;
  confidence_score: number;
  evidence: RequirementEvidence[];
  needs_review: boolean;
  review_notes?: string | null;
}

export interface RequirementGroup {
  id: string;
  parent_group_id?: string | null;
  operator: LogicalOperator;
  min_count?: number | null;
  description?: string | null;
  requirement_ids?: string[];
  child_group_ids?: string[];
}

export interface StructuredSkill {
  name: string;
  normalized_name: string;
  category: SkillCategory;
  min_years?: number | null;
  is_mandatory: boolean;
  version_requirement?: string | null;
  evidence?: RequirementEvidence | null;
}

export interface EducationRequirement {
  degree_level: DegreeLevel;
  fields_of_study: string[];
  degree_status: DegreeStatus;
  minimum_gpa?: number | null;
  alternative_experience_years?: number | null;
  is_mandatory: boolean;
  raw_text: string;
  evidence: RequirementEvidence[];
}

export interface ExperienceRequirement {
  minimum_years?: number | null;
  maximum_years?: number | null;
  domain_categories: string[];
  is_mandatory: boolean;
  raw_text: string;
  evidence: RequirementEvidence[];
}

export interface EmploymentConditions {
  workplace_type: WorkplaceType;
  primary_location?: string | null;
  allowed_countries: string[];
  office_days_per_week?: number | null;
  travel_percentage?: number | null;
  working_hours?: string | null;
  employment_type: EmploymentType;
  contract_duration?: string | null;
  is_relocation_offered?: boolean | null;
  evidence: RequirementEvidence[];
}

export interface CompensationIntelligence {
  base_min?: number | null;
  base_max?: number | null;
  currency: string;
  pay_period: PayPeriod;
  has_bonus: boolean;
  bonus_details?: string | null;
  has_equity: boolean;
  equity_details?: string | null;
  benefits: string[];
  original_text: string;
  is_disclosed: boolean;
  is_ambiguous: boolean;
  evidence: RequirementEvidence[];
}

export interface EligibilityConditions {
  work_authorization_required: boolean;
  visa_sponsorship_offered?: boolean | null;
  visa_sponsorship_refused?: boolean | null;
  citizenship_restrictions: string[];
  security_clearance_required?: string | null;
  is_ambiguous: boolean;
  evidence: RequirementEvidence[];
}

export interface ApplicationInstructions {
  deadline_utc?: string | null;
  is_rolling: boolean;
  start_date_utc?: string | null;
  application_url: string;
  required_documents: string[];
  instructions_text: string;
  evidence: RequirementEvidence[];
}

export interface ConflictRecord {
  id: string;
  conflict_type: ConflictType;
  source_a_id?: string | null;
  source_a_text: string;
  source_b_id?: string | null;
  source_b_text: string;
  resolution_strategy: ResolutionStrategy;
  resolved_text?: string | null;
  is_resolved: boolean;
  resolved_by?: string | null;
  resolved_at?: string | null;
}

export interface JobIntelligenceReviewItem {
  id: string;
  intelligence_id: string;
  requirement_id?: string | null;
  conflict_id?: string | null;
  review_type: string;
  reason: string;
  status: ReviewStatus;
  reviewer_decision?: string | null;
  reviewer_notes?: string | null;
  created_at: string;
}

export interface JobIntelligenceRecord {
  id: string;
  canonical_job_id: string;
  canonical_job_version: number;
  description_hash: string;
  extractor_version: string;
  analysis_status: AnalysisStatus;
  job_title: string;
  role_family?: string | null;
  seniority?: string | null;
  responsibilities: string[];
  mandatory_requirements: AtomicRequirement[];
  preferred_requirements: AtomicRequirement[];
  optional_requirements: AtomicRequirement[];
  conditional_requirements: AtomicRequirement[];
  requirement_groups: RequirementGroup[];
  skills: StructuredSkill[];
  education: EducationRequirement[];
  experience: ExperienceRequirement[];
  employment_conditions: EmploymentConditions;
  compensation: CompensationIntelligence;
  eligibility: EligibilityConditions;
  application_instructions: ApplicationInstructions;
  conflicts: ConflictRecord[];
  review_items: JobIntelligenceReviewItem[];
  data_quality_warnings: string[];
  overall_confidence: number;
  review_status: ReviewStatus;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}
