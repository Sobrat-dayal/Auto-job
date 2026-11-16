/**
/**
 * AUTONOM Centralized Settings Type Definitions
 * Phase 2 — Stage 10
 */

export interface GeneralSettings {
  app_language: string;
  date_format: 'YYYY-MM-DD' | 'DD/MM/YYYY' | 'MM/DD/YYYY';
  time_format: '24h' | '12h';
  timezone_display: 'UTC' | 'Local';
  default_landing_page: string;
  confirm_destructive_actions: boolean;
  confirm_backup_restore: boolean;
  confirm_task_cancellation: boolean;
  show_technical_metrics: boolean;
  high_contrast_borders: boolean;
}

export interface AppearanceSettings {
  theme: 'dark' | 'navy-dark';
  density: 'comfortable' | 'compact';
  font_scale: '90%' | '100%' | '110%';
  sidebar_default_expanded: boolean;
  reduced_motion: boolean;
  chart_animations: boolean;
  table_density: 'compact' | 'normal';
}

export interface AIProviderItem {
  id: string;
  name: string;
  provider_type: 'local' | 'cloud' | 'custom';
  endpoint: string;
  auth_method: 'none' | 'bearer_token' | 'api_key';
  credential_ref?: string | null;
  enabled: boolean;
  connection_status: 'unconfigured' | 'configured' | 'offline' | 'verified';
  last_verified_at?: string | null;
  supported_modalities: string[];
}

export interface AIModelItem {
  id: string;
  name: string;
  provider_id: string;
  task_category: 'scouting' | 'synthesis' | 'coding' | 'analysis' | 'general';
  context_window: number;
  max_output_tokens: number;
  temperature: number;
  timeout_seconds: number;
  fallback_model_id?: string | null;
}

export interface AISettings {
  providers: AIProviderItem[];
  models: AIModelItem[];
  single_active_model_enforced: boolean;
  max_vram_allocation_mb: number;
  idle_model_unload_seconds: number;
  cloud_fallback_enabled: boolean;
}

export interface AgentConfigItem {
  agent_id: string;
  role: string;
  enabled: boolean;
  preferred_model_id: string;
  execution_priority: 'low' | 'normal' | 'high';
  max_concurrent_tasks: number;
  max_execution_duration_seconds: number;
  human_approval_requirement: 'always' | 'sensitive_only' | 'never';
  memory_access_policy: 'read_only' | 'workspace_only' | 'full';
}

export interface AgentSettings {
  agents: AgentConfigItem[];
  default_autonomy_level: 'tier1_full' | 'tier2_supervised' | 'tier3_manual';
  auto_retry_failed_tasks: boolean;
  max_agent_retries: number;
}

export interface AutomationSettings {
  max_concurrent_workers: number;
  max_queued_tasks: number;
  task_default_timeout_seconds: number;
  retry_limit: number;
  background_dispatch_enabled: boolean;
  task_history_retention_days: number;
  notify_on_task_failure: boolean;
  pause_dispatch_on_error_spike: boolean;
}

export interface PermissionCategoryRule {
  category_id: string;
  name: string;
  allowed: boolean;
  requires_approval: boolean;
  description: string;
}

export interface PermissionSettings {
  permissions: PermissionCategoryRule[];
  emergency_killswitch_hotkey: string;
  preauthorize_discovery: boolean;
  preauthorize_dossier_prep: boolean;
}

export interface ComputerControlSettings {
  preferred_interaction_mode: 'structural_first' | 'visual_first' | 'structural_only';
  visual_fallback_enabled: boolean;
  idle_capture_interval_seconds: number;
  active_capture_interval_seconds: number;
  burst_capture_interval_seconds: number;
  screenshot_retention_hours: number;
  sensitive_region_redaction: boolean;
  allowed_applications: string[];
  blocked_applications: string[];
  mouse_keyboard_control_enabled: boolean;
  session_timeout_minutes: number;
}

export interface MCPServerConfigItem {
  server_id: string;
  name: string;
  transport: 'stdio' | 'sse';
  command_or_url: string;
  enabled: boolean;
  trusted: boolean;
  allowed_tools: string[];
}

export interface IntegrationSettings {
  mcp_servers: MCPServerConfigItem[];
  email_integration_enabled: boolean;
  telegram_integration_enabled: boolean;
  whatsapp_integration_enabled: boolean;
  job_board_scouting_enabled: boolean;
}

export interface RecruitmentSettings {
  desired_job_titles: string[];
  related_job_titles: string[];
  role_levels: ('internship' | 'entry' | 'mid' | 'senior' | 'lead')[];
  preferred_locations: string[];
  work_style: ('remote' | 'hybrid' | 'onsite')[];
  relocation_willing: boolean;
  minimum_base_salary: number;
  salary_currency: string;
  excluded_companies: string[];
  excluded_sources: string[];
  max_daily_applications: number;
  application_window_start: string;
  application_window_end: string;
  prevent_duplicate_applications: boolean;
  minimum_match_threshold: number;
  resume_tailoring_mode: 'subtle' | 'focused' | 'comprehensive';
  require_human_approval_for_submission: boolean;
  auto_submission_authorized: boolean;
}

export interface StorageSettings {
  backup_retention_count: number;
  data_retention_days: number;
  auto_backup_on_startup: boolean;
  auto_vacuum_enabled: boolean;
  artifact_storage_limit_mb: number;
}

export interface NotificationSettings {
  notifications_enabled: boolean;
  notify_on_task_completion: boolean;
  notify_on_task_failure: boolean;
  notify_on_backend_events: boolean;
  notify_on_pending_approval: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  sound_enabled: boolean;
  mask_sensitive_previews: boolean;
}

export interface DesktopSettingsModel {
  start_at_login: boolean;
  close_to_tray: boolean;
  minimize_to_tray: boolean;
  restore_window_position: boolean;
  auto_start_backend_sidecar: boolean;
  max_backend_restarts: number;
}

export interface SecurityPrivacySettings {
  dpapi_vault_enabled: boolean;
  redact_secrets_in_logs: boolean;
  audit_logging_level: 'all_actions' | 'sensitive_only' | 'security_only';
  local_first_strict_mode: boolean;
  telemetry_enabled: boolean;
}

export interface AllSettingsResponse {
  general: GeneralSettings;
  appearance: AppearanceSettings;
  ai: AISettings;
  agents: AgentSettings;
  automation: AutomationSettings;
  permissions: PermissionSettings;
  computer: ComputerControlSettings;
  integrations: IntegrationSettings;
  recruitment: RecruitmentSettings;
  storage: StorageSettings;
  notifications: NotificationSettings;
  desktop: DesktopSettingsModel;
  security: SecurityPrivacySettings;
  version: number;
  last_updated_at?: string | null;
}

export interface SettingItemMetadata {
  key: string;
  category: string;
  setting_type: string;
  default_value: unknown;
  description: string;
  requires_restart: boolean;
  is_sensitive: boolean;
  availability: 'available' | 'planned';
  roadmap_stage?: string | null;
}

export interface SettingsSchemaMetadataResponse {
  schema_version: number;
  categories: string[];
  items: SettingItemMetadata[];
}

export interface SettingsExportPayload {
  app_version: string;
  exported_at: string;
  schema_version: number;
  settings: Record<string, unknown>;
}

export interface SettingsImportPayload {
  schema_version?: number;
  settings: Record<string, unknown>;
}

export interface IntegrationConfigurationResponse {
  credentials: Array<{
    id: string;
    provider: string;
    credential_type: string;
    status: string;
    is_configured: boolean;
    created_at: string;
    last_validated_at: string | null;
  }>;
  mcp_servers: MCPServerConfigItem[];
  services: {
    email: boolean;
    telegram: boolean;
    whatsapp: boolean;
    job_boards: boolean;
  };
}
