/**
 * Stage 16 Browser Automation Shared Types
 */

export type BrowserType = 'chromium' | 'msedge' | 'chrome' | 'firefox' | 'webkit';

export type BrowserSessionStatus = 'created' | 'launching' | 'running' | 'paused' | 'error' | 'closed';

export type BrowserTabStatus = 'active' | 'navigating' | 'ready' | 'crashed' | 'closed';

export type BrowserActionType =
  | 'navigate'
  | 'click'
  | 'fill'
  | 'select'
  | 'check'
  | 'press_key'
  | 'hover'
  | 'scroll'
  | 'inspect_dom'
  | 'download'
  | 'screenshot'
  | 'evaluate';

export type BrowserActionStatus = 'pending' | 'executing' | 'succeeded' | 'failed' | 'blocked';

export type BrowserTaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type BrowserDownloadStatus = 'in_progress' | 'completed' | 'failed' | 'cancelled';

export interface BrowserTabInfo {
  id: string;
  session_id: string;
  tab_index: number;
  title: string;
  url: string;
  status: BrowserTabStatus;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
}

export interface BrowserTabCreateRequest {
  url?: string | null;
}

export interface BrowserTabSwitchRequest {
  tab_id: string;
}

export interface BrowserSessionResponse {
  id: string;
  profile_id?: string | null;
  browser_type: string;
  channel?: string | null;
  status: BrowserSessionStatus;
  is_headless: boolean;
  active_tab_id?: string | null;
  pid?: number | null;
  viewport_width: number;
  viewport_height: number;
  user_agent?: string | null;
  locale: string;
  timezone_id: string;
  created_at: string;
  last_activity_at: string;
  closed_at?: string | null;
  error_message?: string | null;
  metadata: Record<string, any>;
  tabs: BrowserTabInfo[];
}

export interface BrowserSessionSummary {
  id: string;
  browser_type: string;
  channel?: string | null;
  status: BrowserSessionStatus;
  is_headless: boolean;
  active_tab_id?: string | null;
  tab_count: number;
  current_url: string;
  current_title: string;
  created_at: string;
  last_activity_at: string;
}

export interface BrowserSessionCreateRequest {
  profile_id?: string | null;
  browser_type?: BrowserType;
  channel?: string | null;
  is_headless?: boolean;
  viewport_width?: number;
  viewport_height?: number;
  user_agent?: string | null;
  locale?: string;
  timezone_id?: string;
  metadata?: Record<string, any>;
}

export interface BrowserNavigateRequest {
  url: string;
  tab_id?: string | null;
  wait_until?: 'load' | 'domcontentloaded' | 'networkidle';
  timeout_ms?: number;
}

export interface BrowserNavigateResponse {
  session_id: string;
  tab_id: string;
  url: string;
  title: string;
  status_code?: number | null;
  navigation_time_ms: number;
  is_secure_origin: boolean;
}

export interface DOMElementNode {
  id: number;
  tag: string;
  role?: string | null;
  name?: string | null;
  text?: string | null;
  placeholder?: string | null;
  value?: string | null;
  selector: string;
  is_visible: boolean;
  is_enabled: boolean;
  is_clickable: boolean;
  is_checked?: boolean | null;
  attributes: Record<string, string>;
}

export interface FormFieldInfo {
  name: string;
  field_type: string;
  label?: string | null;
  placeholder?: string | null;
  required: boolean;
  current_value?: string | null;
  selector: string;
  is_sensitive: boolean;
}

export interface FormInspectionResponse {
  form_id?: string | null;
  action_url?: string | null;
  method: string;
  fields: FormFieldInfo[];
  submit_button_selector?: string | null;
  submit_button_text?: string | null;
}

export interface DOMInspectionRequest {
  tab_id?: string | null;
  max_elements?: number;
  interactive_only?: boolean;
  include_forms?: boolean;
}

export interface DOMInspectionResponse {
  session_id: string;
  tab_id: string;
  url: string;
  title: string;
  elements: DOMElementNode[];
  forms: FormInspectionResponse[];
  total_elements_count: number;
  token_estimate: number;
}

export interface BrowserActionRequest {
  action_type: BrowserActionType;
  target_locator?: string | null;
  tab_id?: string | null;
  parameters?: Record<string, any>;
  timeout_ms?: number;
}

export interface BrowserActionResponse {
  id: string;
  session_id: string;
  tab_id?: string | null;
  action_type: BrowserActionType;
  status: BrowserActionStatus;
  result?: Record<string, any> | null;
  error_message?: string | null;
  screenshot_path?: string | null;
  duration_ms: number;
}

export interface BrowserBatchActionsRequest {
  tab_id?: string | null;
  actions: BrowserActionRequest[];
  stop_on_failure?: boolean;
}

export interface BrowserBatchActionsResponse {
  session_id: string;
  total_actions: number;
  succeeded_count: number;
  failed_count: number;
  results: BrowserActionResponse[];
}

export interface BrowserScreenshotRequest {
  tab_id?: string | null;
  full_page?: boolean;
  element_locator?: string | null;
  quality?: number;
}

export interface BrowserScreenshotResponse {
  session_id: string;
  tab_id: string;
  screenshot_path: string;
  thumbnail_base64?: string | null;
  width: number;
  height: number;
  captured_at: string;
}

export interface BrowserDownloadResponse {
  id: string;
  session_id: string;
  tab_id?: string | null;
  suggested_filename: string;
  destination_path: string;
  file_size_bytes: number;
  sha256_checksum?: string | null;
  mime_type?: string | null;
  source_url: string;
  status: BrowserDownloadStatus;
  created_at: string;
  completed_at?: string | null;
  error_message?: string | null;
}

export interface BrowserProfileCreateRequest {
  name: string;
  description?: string;
  domain_scopes?: string[];
}

export interface BrowserProfileResponse {
  id: string;
  name: string;
  description: string;
  storage_path: string;
  is_authenticated: boolean;
  domain_scopes: string[];
  last_used_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrowserTaskCreateRequest {
  goal: string;
  session_id?: string | null;
  workflow_id?: string | null;
  step_id?: string | null;
  max_steps?: number;
}

export interface BrowserTaskResponse {
  id: string;
  agent_id: string;
  session_id?: string | null;
  workflow_id?: string | null;
  step_id?: string | null;
  goal: string;
  status: BrowserTaskStatus;
  current_step: number;
  total_steps: number;
  result?: Record<string, any> | null;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface BrowserRuntimeStatus {
  playwright_available: boolean;
  installed_browsers: string[];
  system_browsers_detected: string[];
  active_sessions_count: number;
  max_concurrent_sessions: number;
  default_headless: boolean;
  downloads_dir: string;
  screenshots_dir: string;
}
