/**
 * Stage 19: Hybrid Computer Interaction & Multi-Method Automation Contracts
 */

export type InteractionMethod =
  | 'BROWSER_DOM'
  | 'WINDOWS_UIA'
  | 'WINDOWS_WIN32'
  | 'VISUAL_GROUNDING';

export type SurfaceType =
  | 'BROWSER_DOM'
  | 'NATIVE_UIA'
  | 'NATIVE_WIN32'
  | 'CUSTOM_RENDERED'
  | 'EMBEDDED_WEBVIEW'
  | 'UNKNOWN';

export type TargetType =
  | 'BROWSER_PAGE'
  | 'BROWSER_TAB'
  | 'BROWSER_FRAME'
  | 'BROWSER_ELEMENT'
  | 'NATIVE_APP'
  | 'NATIVE_WINDOW'
  | 'UIA_ELEMENT'
  | 'VISUAL_CAPTURE_TARGET'
  | 'VISUAL_REGION';

export type ActionRiskLevel =
  | 'READ_ONLY'
  | 'REPEATABLE'
  | 'CONDITIONALLY_REPEATABLE'
  | 'NON_IDEMPOTENT'
  | 'IRREVERSIBLE';

export type HybridActionType =
  | 'click'
  | 'double_click'
  | 'right_click'
  | 'enter_text'
  | 'navigate'
  | 'scroll'
  | 'key_press'
  | 'hotkey'
  | 'inspect'
  | 'submit'
  | 'select_option';

export type HybridTaskStatus =
  | 'pending'
  | 'routing'
  | 'executing'
  | 'verifying'
  | 'falling_back'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'blocked_policy'
  | 'waiting_approval';

export type HybridVerificationStatus =
  | 'success'
  | 'failed'
  | 'unknown_outcome'
  | 'not_verified';

export interface InteractionTarget {
  target_id: string;
  target_type: TargetType;
  surface_type: SurfaceType;
  session_id?: string | null;
  browser_context_id?: string | null;
  page_id?: string | null;
  dom_selector?: string | null;
  process_id?: number | null;
  process_name?: string | null;
  window_handle?: number | null;
  window_ref?: string | null;
  uia_runtime_id?: string | null;
  control_type?: string | null;
  element_name?: string | null;
  visual_target_name?: string | null;
  coordinates?: Record<string, any> | null;
  bounds?: Record<string, any> | null;
  authorization_scope?: string;
  last_observed_at?: string | null;
  metadata?: Record<string, any>;
}

export interface CapabilityProbe {
  method: InteractionMethod;
  is_available: boolean;
  is_applicable: boolean;
  confidence_score: number;
  supported_actions: string[];
  required_permissions: string[];
  resource_cost_score: number;
  latency_ms_estimate: number;
  verification_supported: boolean;
  reason: string;
  probed_at: string;
}

export interface ObservationRequest {
  target: InteractionTarget;
  preferred_method?: InteractionMethod | null;
  include_snapshot?: boolean;
  include_visual?: boolean;
  timeout_ms?: number;
}

export interface InteractionObservation {
  observation_id: string;
  target_id: string;
  method: InteractionMethod;
  surface_type: SurfaceType;
  observed_text?: string | null;
  structure_summary?: string | null;
  dom_elements?: Array<Record<string, any>>;
  uia_elements?: Array<Record<string, any>>;
  visual_detections?: Array<Record<string, any>>;
  is_valid: boolean;
  is_stale: boolean;
  captured_at: string;
  metadata?: Record<string, any>;
}

export interface InteractionAction {
  action_id?: string;
  task_id?: string | null;
  target: InteractionTarget;
  action_type: HybridActionType;
  method?: InteractionMethod | null;
  input_text?: string | null;
  key?: string | null;
  hotkey_modifiers?: string[];
  url?: string | null;
  click_offset?: Record<string, number> | null;
  risk_level?: ActionRiskLevel;
  is_non_idempotent?: boolean;
  expected_mutation?: string | null;
  timeout_ms?: number;
  allow_fallback?: boolean;
  metadata?: Record<string, any>;
}

export interface InteractionResult {
  action_id: string;
  method: InteractionMethod;
  success: boolean;
  execution_time_ms: number;
  verification_status: HybridVerificationStatus;
  verification_details: string;
  error_message?: string | null;
  mutation_detected: boolean;
  fallback_occurred: boolean;
  fallback_attempts: number;
  executed_at: string;
  metadata?: Record<string, any>;
}

export interface RoutingDecisionRecord {
  decision_id: string;
  task_id?: string | null;
  target_id: string;
  selected_method: InteractionMethod;
  candidate_methods: InteractionMethod[];
  rejected_methods: Record<string, string>;
  scoring: Record<string, number>;
  rationale: string;
  decided_at: string;
}

export interface FallbackRecord {
  fallback_id: string;
  task_id: string;
  initial_method: InteractionMethod;
  fallback_method: InteractionMethod;
  trigger_reason: string;
  reobservation_successful: boolean;
  outcome: string;
  timestamp: string;
}

export interface HybridTaskRequest {
  instruction: string;
  target?: InteractionTarget | null;
  action_type?: HybridActionType | null;
  preferred_method?: InteractionMethod | null;
  allow_fallback?: boolean;
  max_fallback_steps?: number;
  require_verification?: boolean;
  context?: Record<string, any>;
}

export interface HybridTaskResponse {
  task_id: string;
  status: HybridTaskStatus;
  instruction: string;
  selected_method?: InteractionMethod | null;
  routing_decision?: RoutingDecisionRecord | null;
  attempts: Array<Record<string, any>>;
  final_result?: InteractionResult | null;
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface MethodHealthStatus {
  method: InteractionMethod;
  status: string;
  success_count: number;
  failure_count: number;
  avg_latency_ms: number;
  last_error?: string | null;
  last_used_at?: string | null;
}

export interface HybridDiagnosticsInfo {
  engine_version: string;
  is_healthy: boolean;
  emergency_stop_active: boolean;
  input_lease_owner?: string | null;
  methods: MethodHealthStatus[];
  total_tasks: number;
  active_tasks: number;
  total_fallbacks: number;
  recent_routing_decisions: RoutingDecisionRecord[];
}
