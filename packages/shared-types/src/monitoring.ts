/**
 * AUTONOM Shared Types - Stage 30 Continuous Recruitment Monitoring & Opportunity Prioritization
 */

export type WatchType =
  | 'career_strategy'
  | 'source'
  | 'employer'
  | 'role'
  | 'location'
  | 'specific_job'
  | 'saved_search';

export type WatchStatus =
  | 'draft'
  | 'validating'
  | 'active'
  | 'paused'
  | 'suspended'
  | 'requires_authorization'
  | 'rate_limited'
  | 'failed'
  | 'disabled'
  | 'archived';

export type RunTriggerType =
  | 'scheduled'
  | 'manual'
  | 'resume_after_restart'
  | 'source_change_event'
  | 'config_changed'
  | 'retry'
  | 'authorized_agent';

export type RunStatus =
  | 'created'
  | 'validating'
  | 'queued'
  | 'waiting_for_resources'
  | 'waiting_for_authorization'
  | 'running'
  | 'rate_limited'
  | 'paused'
  | 'partially_completed'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'interrupted';

export type PipelinePhase =
  | 'discovering'
  | 'aggregating'
  | 'analyzing'
  | 'matching'
  | 'updating_queue'
  | 'evaluating_alerts'
  | 'completed';

export type JobChangeType =
  | 'new_vacancy'
  | 'description_updated'
  | 'skills_changed'
  | 'experience_changed'
  | 'salary_changed'
  | 'location_changed'
  | 'remote_conditions_changed'
  | 'deadline_changed'
  | 'sponsorship_changed'
  | 'application_url_changed'
  | 'job_closed'
  | 'job_reopened';

export type OpportunityPriority =
  | 'critical_review'
  | 'high'
  | 'normal'
  | 'low'
  | 'deferred'
  | 'excluded';

export type OpportunityQueueStatus =
  | 'newly_discovered'
  | 'awaiting_analysis'
  | 'awaiting_match'
  | 'recommended'
  | 'high_priority'
  | 'needs_review'
  | 'ready_for_preparation'
  | 'deferred'
  | 'saved'
  | 'excluded'
  | 'closed'
  | 'outdated'
  | 'archived'
  | 'processing_failed';

export type AlertTriggerType =
  | 'new_job'
  | 'high_priority_job'
  | 'approaching_deadline'
  | 'material_job_change'
  | 'job_closed'
  | 'job_reopened'
  | 'match_changed'
  | 'review_required'
  | 'source_failure'
  | 'permission_expired';

export type AlertSeverity = 'info' | 'warning' | 'critical';

export type NotificationDeliveryStatus =
  | 'pending'
  | 'deferred_by_quiet_hours'
  | 'ready'
  | 'delivery_attempted'
  | 'delivered_where_confirmed'
  | 'outcome_unknown'
  | 'failed'
  | 'dismissed'
  | 'read';

export type RecurrenceType =
  | 'interval'
  | 'hourly'
  | 'daily'
  | 'weekdays'
  | 'selected_days'
  | 'weekly'
  | 'cron';

export type MissedRunPolicy =
  | 'skip'
  | 'run_once_after_restart'
  | 'run_latest_due'
  | 'require_review';

export type ComponentHealthStatus =
  | 'available'
  | 'busy'
  | 'waiting'
  | 'rate_limited'
  | 'paused'
  | 'needs_authorization'
  | 'unhealthy'
  | 'offline'
  | 'disabled';

export interface QuietHoursConfig {
  enabled: boolean;
  start_time: string;
  end_time: string;
  mute_notifications: boolean;
  pause_source_monitoring: boolean;
  pause_heavy_inference: boolean;
}

export interface ScheduleConfig {
  recurrence_type: RecurrenceType;
  interval_minutes: number;
  cron_expression?: string | null;
  days_of_week: number[];
  time_of_day?: string | null;
  timezone: string;
  quiet_hours: QuietHoursConfig;
  missed_run_policy: MissedRunPolicy;
  max_retries: number;
  retry_delay_seconds: number;
}

export interface SchedulePreviewOccurrence {
  occurrence_index: number;
  scheduled_time: string;
  is_quiet_hours: boolean;
  action: string;
}

export interface SchedulePreviewResponse {
  watch_name: string;
  timezone: string;
  recurrence_summary: string;
  next_occurrences: SchedulePreviewOccurrence[];
  estimated_request_budget_per_run: number;
  quiet_hours_active_in_preview: boolean;
  requires_authorization: boolean;
}

export interface MonitoringProfileData {
  id: string;
  owner_id: string;
  career_strategy_id?: string | null;
  career_strategy_version?: number | null;
  name: string;
  enabled: boolean;
  source_scope: string[];
  role_scope: string[];
  location_scope: string[];
  alert_preferences: Record<string, unknown>;
  resource_limits: Record<string, unknown>;
  review_rules: Record<string, unknown>;
  retention_days: number;
  version: number;
  active_watches_count: number;
  created_at: string;
  updated_at: string;
}

export interface MonitoringProfileCreateRequest {
  name: string;
  career_strategy_id?: string | null;
  source_scope?: string[];
  role_scope?: string[];
  location_scope?: string[];
  alert_preferences?: Record<string, unknown>;
  resource_limits?: Record<string, unknown>;
  review_rules?: Record<string, unknown>;
  retention_days?: number;
}

export interface MonitoringProfileUpdateRequest {
  name?: string;
  career_strategy_id?: string | null;
  enabled?: boolean;
  source_scope?: string[];
  role_scope?: string[];
  location_scope?: string[];
  alert_preferences?: Record<string, unknown>;
  resource_limits?: Record<string, unknown>;
  review_rules?: Record<string, unknown>;
  retention_days?: number;
}

export interface JobWatchData {
  id: string;
  owner_id: string;
  profile_id: string;
  name: string;
  watch_type: WatchType;
  career_strategy_id?: string | null;
  approved_sources: string[];
  employer_ids: string[];
  role_filters: Record<string, unknown>;
  location_filters: Record<string, unknown>;
  schedule_config: ScheduleConfig;
  alert_rules: Record<string, unknown>;
  status: WatchStatus;
  error_state?: string | null;
  last_run_at?: string | null;
  next_due_run_at?: string | null;
  consecutive_failures: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface JobWatchCreateRequest {
  profile_id: string;
  name: string;
  watch_type?: WatchType;
  career_strategy_id?: string | null;
  approved_sources?: string[];
  employer_ids?: string[];
  role_filters?: Record<string, unknown>;
  location_filters?: Record<string, unknown>;
  schedule_config?: ScheduleConfig;
  alert_rules?: Record<string, unknown>;
}

export interface JobWatchUpdateRequest {
  name?: string;
  approved_sources?: string[];
  employer_ids?: string[];
  role_filters?: Record<string, unknown>;
  location_filters?: Record<string, unknown>;
  schedule_config?: ScheduleConfig;
  alert_rules?: Record<string, unknown>;
  status?: WatchStatus;
}

export interface MonitoringRunData {
  id: string;
  watch_id: string;
  watch_version: number;
  trigger_type: RunTriggerType;
  scheduled_at?: string | null;
  started_at: string;
  ended_at?: string | null;
  sources_checked_list: string[];
  current_phase: PipelinePhase;
  status: RunStatus;
  progress_pct: number;
  sources_checked: number;
  new_observations_count: number;
  updated_observations_count: number;
  canonical_jobs_created: number;
  canonical_jobs_updated: number;
  intelligence_analyses_triggered: number;
  matches_recalculated: number;
  queue_entries_created: number;
  alerts_generated: number;
  error_message?: string | null;
  output_references: Record<string, unknown>;
}

export interface JobChangeEventData {
  id: string;
  canonical_job_id: string;
  source_id?: string | null;
  run_id?: string | null;
  change_type: JobChangeType;
  is_material: boolean;
  field_name: string;
  previous_value?: unknown;
  current_value?: unknown;
  detected_at: string;
}

export interface OpportunityPreparationCandidate {
  canonical_job_id: string;
  canonical_job_version: string;
  job_title: string;
  company_name: string;
  application_url: string;
  applicant_profile_id: string;
  applicant_profile_version: string;
  job_intelligence_version: string;
  match_evaluation_id: string;
  relevance_score: number;
  eligibility_outcome: string;
  career_strategy_id?: string | null;
  policy_version: number;
  priority: OpportunityPriority;
  current_job_status: string;
  deadline?: string | null;
  missing_information: string[];
  required_reviews: Record<string, unknown>[];
  ready_for_preparation: boolean;
  generated_at: string;
}

export interface OpportunityQueueEntryData {
  id: string;
  canonical_job_id: string;
  job_title: string;
  company: string;
  location?: string | null;
  employment_type?: string | null;
  work_arrangement?: string | null;
  salary_range?: string | null;
  application_url: string;
  applicant_profile_id: string;
  career_strategy_id?: string | null;
  match_evaluation_id?: string | null;
  priority: OpportunityPriority;
  queue_status: OpportunityQueueStatus;
  eligibility_state: string;
  policy_state: string;
  review_requirements: Record<string, unknown>[];
  job_availability: string;
  deadline?: string | null;
  relevance_score?: number | null;
  user_action?: string | null;
  user_action_at?: string | null;
  ready_for_preparation: boolean;
  stage31_candidate?: OpportunityPreparationCandidate | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface OpportunityQueueUpdateRequest {
  priority?: OpportunityPriority;
  queue_status?: OpportunityQueueStatus;
  user_action?: string;
}

export interface AlertRuleData {
  id: string;
  owner_id: string;
  name: string;
  profile_id?: string | null;
  watch_id?: string | null;
  trigger_type: AlertTriggerType;
  conditions: Record<string, unknown>;
  delivery_channels: string[];
  quiet_hours_enabled: boolean;
  cooldown_minutes: number;
  enabled: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface AlertRuleCreateRequest {
  name: string;
  profile_id?: string | null;
  watch_id?: string | null;
  trigger_type: AlertTriggerType;
  conditions?: Record<string, unknown>;
  delivery_channels?: string[];
  quiet_hours_enabled?: boolean;
  cooldown_minutes?: number;
}

export interface AlertRuleUpdateRequest {
  name?: string;
  trigger_type?: AlertTriggerType;
  conditions?: Record<string, unknown>;
  delivery_channels?: string[];
  quiet_hours_enabled?: boolean;
  cooldown_minutes?: number;
  enabled?: boolean;
}

export interface AlertEventData {
  id: string;
  owner_id: string;
  rule_id?: string | null;
  queue_entry_id?: string | null;
  canonical_job_id?: string | null;
  run_id?: string | null;
  title: string;
  message: string;
  alert_type: AlertTriggerType;
  severity: AlertSeverity;
  is_read: boolean;
  is_dismissed: boolean;
  acknowledged_at?: string | null;
  deep_link?: string | null;
  created_at: string;
}

export interface NotificationOutboxData {
  id: string;
  alert_event_id: string;
  delivery_channel: string;
  title: string;
  body: string;
  status: NotificationDeliveryStatus;
  attempts: number;
  last_attempt_at?: string | null;
  error_message?: string | null;
  deferred_until?: string | null;
  created_at: string;
}

export interface MonitoringSettingsData {
  owner_id: string;
  background_monitoring_enabled: boolean;
  start_at_windows_signin: boolean;
  minimize_to_tray: boolean;
  default_interval_minutes: number;
  global_concurrency_limit: number;
  daily_request_budget: number;
  pause_on_battery: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  timezone: string;
  notification_privacy_mode: boolean;
  retention_days: number;
  updated_at: string;
}

export interface MonitoringSettingsUpdateRequest {
  background_monitoring_enabled?: boolean;
  start_at_windows_signin?: boolean;
  minimize_to_tray?: boolean;
  default_interval_minutes?: number;
  global_concurrency_limit?: number;
  daily_request_budget?: number;
  pause_on_battery?: boolean;
  quiet_hours_enabled?: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  timezone?: string;
  notification_privacy_mode?: boolean;
  retention_days?: number;
}

export interface MonitoringOverviewKPIs {
  monitoring_enabled: boolean;
  active_watches_count: number;
  next_scheduled_run_at?: string | null;
  last_successful_run_at?: string | null;
  currently_running_runs_count: number;
  total_opportunities_count: number;
  high_priority_count: number;
  review_required_count: number;
  ready_for_preparation_count: number;
  unread_alerts_count: number;
  source_failures_count: number;
}

export interface MonitoringMetricsData {
  total_runs_executed: number;
  successful_runs_count: number;
  failed_runs_count: number;
  total_requests_attempted: number;
  total_requests_successful: number;
  rate_limited_responses_count: number;
  new_source_observations_count: number;
  new_canonical_jobs_count: number;
  changed_canonical_jobs_count: number;
  intelligence_analyses_count: number;
  matches_recalculated_count: number;
  queue_entries_created_count: number;
  alerts_generated_count: number;
  notifications_delivered_count: number;
  average_run_latency_seconds: number;
}

export interface ComponentHealthData {
  component: string;
  status: ComponentHealthStatus;
  heartbeat_at: string;
  details: Record<string, unknown>;
}

export interface DiagnosticsReport {
  system_time_utc: string;
  timezone_configured: string;
  is_quiet_hours_now: boolean;
  database_status: string;
  emergency_stop_active: boolean;
  automation_paused: boolean;
  active_worker_leases: number;
  pending_outbox_notifications: number;
  components_health: ComponentHealthData[];
  active_cooldowns: Record<string, unknown>[];
}
