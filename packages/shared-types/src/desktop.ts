/**
 * Shared TypeScript definitions for Windows Structural UI Automation (Stage 17).
 */

export type DesktopSessionState = 'active' | 'locked' | 'disconnected' | 'unavailable';

export type WindowManageAction = 'activate' | 'minimize' | 'maximize' | 'restore' | 'close';

export type ControlPatternType =
  | 'invoke'
  | 'value'
  | 'toggle'
  | 'selection'
  | 'selection_item'
  | 'expand_collapse'
  | 'scroll'
  | 'text'
  | 'table'
  | 'grid'
  | 'window'
  | 'legacy_ia';

export type DesktopActionType =
  | 'invoke'
  | 'set_value'
  | 'select'
  | 'toggle'
  | 'expand'
  | 'collapse'
  | 'scroll'
  | 'read_text'
  | 'activate_window'
  | 'close_window'
  | 'press_key'
  | 'get_window_state';

export interface DesktopSessionInfo {
  wts_session_id: number;
  status: DesktopSessionState;
  desktop_name: string;
  user_name: string;
  resolution: string;
  is_interactive: boolean;
  is_locked: boolean;
  last_active_at: string;
}

export interface DesktopApplicationInfo {
  id: string;
  name: string;
  executable_path: string;
  executable_name: string;
  publisher?: string | null;
  is_allowed: boolean;
  risk_level: string;
  integrity_level: string;
  pids: number[];
  window_count: number;
  last_detected_at: string;
}

export interface WindowBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

export interface WindowInfo {
  window_ref: string;
  hwnd: number;
  pid: number;
  process_name: string;
  title: string;
  window_class: string;
  is_visible: boolean;
  is_enabled: boolean;
  is_foreground: boolean;
  is_minimized: boolean;
  is_maximized: boolean;
  bounds: WindowBounds;
  created_at: string;
  last_inspected_at?: string | null;
}

export interface UIElementInfo {
  element_ref: string;
  window_ref: string;
  name?: string | null;
  automation_id?: string | null;
  control_type: string;
  control_type_id: number;
  class_name?: string | null;
  framework_id?: string | null;
  is_enabled: boolean;
  is_offscreen: boolean;
  has_keyboard_focus: boolean;
  bounding_box: WindowBounds;
  supported_patterns: string[];
  value?: string | null;
  toggle_state?: string | null;
  parent_ref?: string | null;
}

export interface UITreeNode {
  element: UIElementInfo;
  children: UITreeNode[];
}

export interface InspectionOptions {
  max_depth?: number;
  max_nodes?: number;
  view_type?: 'control' | 'raw';
  timeout_ms?: number;
}

export interface UITreeSnapshot {
  window_ref: string;
  title: string;
  root: UITreeNode;
  total_nodes: number;
  max_depth_reached: number;
  is_truncated: boolean;
  estimated_tokens: number;
  inspected_at: string;
}

export interface ElementQuery {
  automation_id?: string;
  name?: string;
  control_type?: string;
  class_name?: string;
  exact_name?: boolean;
}

export interface DesktopActionRequest {
  action_type: DesktopActionType;
  window_ref: string;
  element_ref?: string;
  locator?: ElementQuery;
  value?: string;
  key?: string;
  modifiers?: string[];
  timeout_ms?: number;
  verify?: boolean;
  expected_outcome?: string;
}

export interface DesktopActionResult {
  action_id: string;
  action_type: string;
  status: 'succeeded' | 'failed' | 'blocked';
  verification_status: 'verified' | 'failed' | 'unknown' | 'skipped';
  duration_ms: number;
  result_data: Record<string, unknown>;
  error_message?: string | null;
  executed_at: string;
}

export interface DesktopTaskRequest {
  goal: string;
  target_app?: string;
  workflow_id?: string;
  step_id?: string;
}

export interface DesktopTaskResponse {
  task_id: string;
  goal: string;
  target_app?: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_step: number;
  total_steps: number;
  result?: Record<string, unknown> | null;
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface DesktopDiagnosticsInfo {
  session: DesktopSessionInfo;
  uia_available: boolean;
  win32_available: boolean;
  active_worker_threads: number;
  cached_windows: number;
  registered_applications: number;
  emergency_stop_active: boolean;
  diagnostic_timestamp: string;
}
