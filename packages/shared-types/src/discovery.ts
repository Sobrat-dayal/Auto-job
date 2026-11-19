/**
 * Multi-Source Job Discovery Engine TypeScript Definitions (Stage 26).
 */

export type ConnectorId =
  | 'greenhouse'
  | 'lever'
  | 'ashby'
  | 'usajobs'
  | 'rss_atom'
  | 'json_feed'
  | 'career_page'
  | 'manual_import'
  | 'url_import';

export type SourceCategory =
  | 'official_public_api'
  | 'authorized_partner_api'
  | 'employer_ats_board'
  | 'employer_career_site'
  | 'rss_atom_feed'
  | 'structured_json_feed'
  | 'user_supplied_url'
  | 'manual_imported'
  | 'restricted_commercial';

export type SourceAccessStatus =
  | 'available_public'
  | 'available_authorized'
  | 'requires_credentials'
  | 'requires_partner_access'
  | 'manual_import_only'
  | 'temporarily_rate_limited'
  | 'access_denied'
  | 'restricted_by_terms'
  | 'unavailable'
  | 'unverified';

export type PostingAvailability =
  | 'available'
  | 'closed'
  | 'expired'
  | 'removed'
  | 'redirected'
  | 'unknown'
  | 'source_unavailable';

export type SnapshotCompleteness =
  | 'complete'
  | 'partial'
  | 'interrupted'
  | 'rate_limited'
  | 'invalid'
  | 'failed';

export type DiscoveryTaskState =
  | 'created'
  | 'validating'
  | 'queued'
  | 'running'
  | 'paused'
  | 'rate_limited'
  | 'partially_completed'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type PrefilterOutcome =
  | 'prefilter_accepted'
  | 'prefilter_rejected'
  | 'needs_review'
  | 'unknown';

export type ExtractionConfidence = 'high' | 'medium' | 'low' | 'unknown';

export type ConnectorCapability =
  | 'list_postings'
  | 'get_posting_details'
  | 'server_search'
  | 'server_filter'
  | 'pagination'
  | 'conditional_fetch'
  | 'credential_gated'
  | 'structured_schema_org'
  | 'browser_render_fallback';

export interface ConnectorManifest {
  connector_id: ConnectorId;
  version: string;
  provider_name: string;
  endpoint_category: SourceCategory;
  authentication_method: string;
  required_permissions: string[];
  supported_capabilities: ConnectorCapability[];
  provider_restrictions: string[];
  last_verified_doc_url: string;
  last_verified_at: string;
}

export interface JobSourceConfig {
  id: string;
  name: string;
  connector_id: ConnectorId;
  category: SourceCategory;
  official_domain: string;
  board_token?: string | null;
  site_id?: string | null;
  feed_url?: string | null;
  employer_name?: string | null;
  access_status: SourceAccessStatus;
  is_enabled: boolean;
  rate_limit_rpm: number;
  custom_headers: Record<string, string>;
  custom_params: Record<string, any>;
  credential_alias?: string | null;
  last_synced_at?: string | null;
  error_status?: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobSourceHealth {
  source_id: string;
  last_successful_fetch?: string | null;
  last_failed_fetch?: string | null;
  response_latency_ms?: number | null;
  retrieved_count: number;
  error_count: number;
  rate_limited_count: number;
  consecutive_failures: number;
  current_status: SourceAccessStatus;
  status_message?: string | null;
  last_checked_at: string;
}

export interface EmployerCareerSource {
  id: string;
  employer_name: string;
  career_url: string;
  provider_type?: ConnectorId | null;
  board_token?: string | null;
  approved_origin: string;
  last_validated_at?: string | null;
  access_status: SourceAccessStatus;
  is_enabled: boolean;
  created_at: string;
}

export interface FieldProvenance {
  source_id: string;
  retrieved_at: string;
  raw_field_path: string;
  parser_method: string;
  confidence: ExtractionConfidence;
  is_transformed: boolean;
  original_raw_value?: string | null;
}

export interface ExtractedCompensation {
  min_amount?: number | null;
  max_amount?: number | null;
  currency?: string | null;
  unit?: string | null;
  pay_period?: string | null;
  compensation_type?: string | null;
  raw_text?: string | null;
}

export interface ExtractedLocation {
  country?: string | null;
  state_region?: string | null;
  city?: string | null;
  office?: string | null;
  is_remote: boolean;
  workplace_type?: string | null;
  raw_location_text?: string | null;
}

export interface ExtractedPosting {
  native_posting_id: string;
  title: string;
  employer_name: string;
  official_posting_url: string;
  application_url?: string | null;
  location: ExtractedLocation;
  employment_type?: string | null;
  compensation?: ExtractedCompensation | null;
  posted_date?: string | null;
  updated_date?: string | null;
  closing_date?: string | null;
  department?: string | null;
  office?: string | null;
  description_text: string;
  description_html?: string | null;
  raw_source_data: Record<string, any>;
  provenance: Record<string, FieldProvenance>;
}

export interface JobSourceObservation {
  id: string;
  source_id: string;
  provider: ConnectorId;
  native_posting_id: string;
  source_url: string;
  title: string;
  employer: string;
  location: ExtractedLocation;
  employment_type?: string | null;
  compensation?: ExtractedCompensation | null;
  description_text: string;
  application_url?: string | null;
  department?: string | null;
  posted_at?: string | null;
  updated_at?: string | null;
  discovered_at: string;
  last_fetched_at: string;
  availability: PostingAvailability;
  prefilter_status: PrefilterOutcome;
  prefilter_reasons: string[];
  snapshot_id?: string | null;
  extraction_version: string;
  raw_data_ref?: string | null;
}

export interface JobSourceSnapshot {
  id: string;
  source_id: string;
  task_id: string;
  completeness: SnapshotCompleteness;
  total_observed: intOrNumber;
  new_count: intOrNumber;
  updated_count: intOrNumber;
  unchanged_count: intOrNumber;
  closed_count: intOrNumber;
  started_at: string;
  completed_at?: string | null;
  cursor?: string | null;
  error_message?: string | null;
}

type intOrNumber = number;

export interface DiscoveryTaskRecord {
  id: string;
  strategy_id?: string | null;
  requested_sources: string[];
  selected_sources: string[];
  status: DiscoveryTaskState;
  started_at: string;
  completed_at?: string | null;
  total_postings_found: number;
  new_postings_count: number;
  errors: string[];
  cancellation_requested: boolean;
  source_snapshots: Record<string, string>;
}

export interface DiscoverySettingsConfig {
  max_concurrent_sources: number;
  per_source_request_rpm: number;
  request_timeout_seconds: number;
  max_postings_per_task: number;
  max_browser_sessions: number;
  cache_duration_minutes: number;
  allow_browser_fallback: boolean;
  enforce_ssrf_protection: boolean;
  local_only_preference: boolean;
}

export interface DiscoveryOverviewStats {
  total_sources: number;
  enabled_sources: number;
  total_observations: number;
  active_postings_count: number;
  recently_discovered_count: number;
  failed_sources_count: number;
  rate_limited_sources_count: number;
  active_tasks_count: number;
}

export interface JobSourceCreateRequest {
  name: string;
  connector_id: ConnectorId;
  official_domain: string;
  board_token?: string | null;
  site_id?: string | null;
  feed_url?: string | null;
  employer_name?: string | null;
  category?: SourceCategory;
  is_enabled?: boolean;
  rate_limit_rpm?: number;
  custom_headers?: Record<string, string>;
  custom_params?: Record<string, any>;
}

export interface JobSourceUpdateRequest {
  name?: string | null;
  board_token?: string | null;
  site_id?: string | null;
  feed_url?: string | null;
  employer_name?: string | null;
  is_enabled?: boolean | null;
  rate_limit_rpm?: number | null;
  custom_headers?: Record<string, string> | null;
  custom_params?: Record<string, any> | null;
}

export interface DiscoveryTaskCreateRequest {
  strategy_id?: string | null;
  source_ids?: string[];
  keywords?: string[];
  location_filter?: string | null;
  work_arrangement?: string | null;
  max_postings?: number;
}

export interface UrlImportRequest {
  url: string;
  employer_name?: string | null;
  target_role?: string | null;
  notes?: string | null;
}

export interface ManualImportRequest {
  title: string;
  employer_name: string;
  source_url?: string | null;
  location?: string | null;
  work_arrangement?: string | null;
  employment_type?: string | null;
  compensation_text?: string | null;
  description: string;
  application_url?: string | null;
  notes?: string | null;
}

export interface EmployerCareerPageCreateRequest {
  employer_name: string;
  career_url: string;
}

export interface SourceValidationResult {
  source_id: string;
  is_valid: boolean;
  detected_connector?: ConnectorId | null;
  access_status: SourceAccessStatus;
  available_postings_count?: number | null;
  response_latency_ms?: number | null;
  message: string;
}
