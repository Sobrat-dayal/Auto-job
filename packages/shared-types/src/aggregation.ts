/**
 * Multi-Source Job Aggregation & Canonical Database TypeScript Definitions (Stage 27).
 */

export type EmployerIdentityStatus =
  | 'canonical'
  | 'alias'
  | 'subsidiary'
  | 'parent'
  | 'staffing_agency'
  | 'unresolved';

export type OrganizationType =
  | 'direct_employer'
  | 'staffing_agency'
  | 'recruiting_firm'
  | 'job_board'
  | 'aggregator'
  | 'holding_company'
  | 'subsidiary'
  | 'unknown';

export type CanonicalJobStatus =
  | 'active'
  | 'possibly_active'
  | 'closed'
  | 'expired'
  | 'removed'
  | 'draft'
  | 'unknown';

export type JobIdentityStatus =
  | 'canonical'
  | 'probable'
  | 'in_review'
  | 'rejected';

export type ConflictState =
  | 'no_conflict'
  | 'auto_resolved'
  | 'unresolved_manual'
  | 'acknowledged';

export type DuplicateDecisionState =
  | 'proposed'
  | 'in_review'
  | 'confirmed_duplicate'
  | 'confirmed_distinct'
  | 'related_but_distinct'
  | 'possible_duplicate'
  | 'auto_merged';

export type DuplicateAction =
  | 'merge'
  | 'keep_separate'
  | 'mark_related'
  | 'defer';

export type AggregationConflictType =
  | 'salary_range'
  | 'work_arrangement'
  | 'employment_type'
  | 'location'
  | 'title'
  | 'description'
  | 'other';

export type ConflictResolutionStatus =
  | 'unresolved'
  | 'chosen_source'
  | 'manual_override'
  | 'merged_value';

export type AggregationTaskType =
  | 'incremental'
  | 'full_reindex'
  | 'source_sync'
  | 'duplicate_scan'
  | 'split_reconciliation';

export type AggregationTaskStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface CanonicalJobLocationRecord {
  id: string;
  canonical_job_id: string;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  is_primary: boolean;
  raw_location_text?: string | null;
}

export interface CanonicalJobIdentifierRecord {
  id: string;
  canonical_job_id: string;
  identifier_type: string;
  identifier_value: string;
  source_evidence?: Record<string, unknown>;
}

export interface CanonicalJobSourceLinkRecord {
  id: string;
  canonical_job_id: string;
  listing_id?: string | null;
  source_observation_id: string;
  source_id: string;
  provider: string;
  native_posting_id: string;
  original_url: string;
  application_url?: string | null;
  association_status: string;
  decision_method: string;
  evidence: Record<string, unknown>;
  is_primary: boolean;
  created_at: string;
}

export interface CanonicalJobConflictRecord {
  id: string;
  field_name: string;
  conflict_type: AggregationConflictType;
  status: ConflictResolutionStatus;
  source_values: Record<string, unknown>;
  resolution_note?: string | null;
  resolved_by?: string | null;
  resolved_at?: string | null;
}

export interface CanonicalJobRecord {
  id: string;
  employer_id?: string | null;
  employer_name: string;
  display_title: string;
  normalized_title: string;
  requisition_id?: string | null;
  employment_type?: string | null;
  location_summary?: string | null;
  work_arrangement?: string | null;
  description_reference?: string | null;
  compensation_summary?: string | null;
  status: CanonicalJobStatus;
  first_observed_at: string;
  last_observed_at: string;
  last_verified_active_at?: string | null;
  version: number;
  source_count: number;
  identity_status: JobIdentityStatus;
  conflict_state: ConflictState;
  primary_source_id?: string | null;
  primary_url?: string | null;
  is_evergreen: boolean;
  is_repost: boolean;
  sources: CanonicalJobSourceLinkRecord[];
  locations: CanonicalJobLocationRecord[];
  identifiers: CanonicalJobIdentifierRecord[];
  conflicts: CanonicalJobConflictRecord[];
  created_at: string;
  updated_at: string;
}

export interface CanonicalEmployerRecord {
  id: string;
  name: string;
  legal_name?: string | null;
  organization_type: OrganizationType;
  identity_status: EmployerIdentityStatus;
  official_careers_url?: string | null;
  primary_domain?: string | null;
  confidence_score: number;
  aliases: string[];
  verified_domains: string[];
  provider_boards: Array<{ provider: string; token: string }>;
  created_at: string;
  updated_at: string;
}

export interface DuplicateCandidateRecord {
  id: string;
  left_job_id: string;
  right_job_id: string;
  status: DuplicateDecisionState;
  similarity_score: number;
  matching_factors: Record<string, unknown>;
  contradictions: Record<string, unknown>;
  recommended_action: DuplicateAction;
  created_at: string;
}

export interface MergePreviewResponse {
  surviving_job_id: string;
  superseded_job_id: string;
  proposed_title: string;
  proposed_employer_id?: string | null;
  resulting_source_count: number;
  source_links_to_transfer: string[];
  detected_conflicts: Array<{ field: string; surviving: unknown; superseded: unknown }>;
  affected_downstream_references: string[];
  is_safe_to_merge: boolean;
  warnings: string[];
}

export interface MergeExecuteResponse {
  operation_id: string;
  surviving_job: CanonicalJobRecord;
  superseded_job_id: string;
  status: string;
  transferred_source_count: number;
  created_alias_id: string;
}

export interface SplitPreviewResponse {
  source_job_id: string;
  source_links: CanonicalJobSourceLinkRecord[];
  proposed_split_groups: Array<{ source_id: string; provider: string; url: string }>;
  affected_references_warning: string[];
}

export interface SplitExecuteResponse {
  operation_id: string;
  original_job_id: string;
  new_canonical_job_ids: string[];
  status: string;
}

export interface AggregationOverviewStats {
  total_source_observations: number;
  total_canonical_jobs: number;
  multi_source_canonical_jobs: number;
  pending_duplicate_reviews: number;
  confirmed_duplicate_merges: number;
  unresolved_employer_identities: number;
  active_field_conflicts: number;
  running_tasks: number;
  last_sync_timestamp?: string | null;
}

export interface AggregationDiagnosticsReport {
  status: string;
  database_connected: boolean;
  canonical_jobs_count: number;
  canonical_employers_count: number;
  active_conflicts_count: number;
  unresolved_candidates_count: number;
  recent_tasks: AggregationTaskRecord[];
  system_timestamp: string;
}

export interface AggregationSettingsConfig {
  auto_merge_enabled: boolean;
  min_similarity_for_candidate: number;
  min_similarity_for_auto_merge: number;
  require_same_requisition: boolean;
  enable_ai_assisted_review: boolean;
  batch_size: number;
  worker_concurrency: number;
  updated_at: string;
}

export interface AggregationTaskRecord {
  id: string;
  task_type: AggregationTaskType;
  status: AggregationTaskStatus;
  observations_total: number;
  observations_processed: number;
  canonical_jobs_created: number;
  canonical_jobs_updated: number;
  duplicates_found: number;
  merges_performed: number;
  reviews_queued: number;
  conflicts_detected: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
}
