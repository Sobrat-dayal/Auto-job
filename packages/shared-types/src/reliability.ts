/**
 * Stage 20: Advanced Computer Action Recording, Reusable Procedure Generation,
 * State-Aware Replay, Persistent Checkpoints, and Crash Recovery Types.
 */

export type RecordingMode = 'interactive' | 'supervised' | 'autonomous';
export type RecordingStatus = 'active' | 'paused' | 'stopped' | 'sealed';
export type ProcedureValidationStatus = 'valid' | 'warning' | 'invalid';
export type SideEffectClass = 'read_only' | 'idempotent' | 'non_idempotent';
export type CheckpointPolicy = 'per_step' | 'per_side_effect' | 'manual';
export type ReplayMode =
  | 'dry_run'
  | 'step_by_step'
  | 'automatic_authorized'
  | 'resume_from_checkpoint';
export type ProcedureExecutionStatus =
  | 'pending'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'aborted';
export type CheckpointType =
  | 'periodic'
  | 'pre_action'
  | 'post_action'
  | 'pre_side_effect'
  | 'recovery';
export type SideEffectOutcome =
  | 'pending'
  | 'confirmed'
  | 'denied'
  | 'duplicate_blocked'
  | 'indeterminate';
export type RecoveryClassification =
  | 'safe_to_retry'
  | 'skip_and_continue'
  | 'requires_replan'
  | 'unrecoverable';

export interface RecordedAction {
  action_id: string;
  session_id: string;
  sequence_number: number;
  timestamp: string;
  source_adapter: 'browser' | 'desktop' | 'visual' | 'hybrid';
  action_type: string;
  raw_parameters: Record<string, any>;
  normalized_parameters: Record<string, any>;
  application_name?: string;
  window_title?: string;
  web_origin?: string;
  target_locator?: Record<string, any>;
  state_snapshot?: Record<string, any>;
  is_sensitive: boolean;
}

export interface RecordingSession {
  session_id: string;
  name: string;
  status: RecordingStatus;
  mode: RecordingMode;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  allowed_app_scopes: string[];
  allowed_web_origins: string[];
  actions: RecordedAction[];
  integrity_hash?: string;
  captured_actions_count: number;
  workflow_id?: string;
  agent_id?: string;
}

export interface StartRecordingRequest {
  name?: string;
  mode?: RecordingMode;
  allowed_app_scopes?: string[];
  allowed_web_origins?: string[];
  workflow_id?: string;
  agent_id?: string;
}

export interface ProcedureParameter {
  name: string;
  type: 'string' | 'integer' | 'float' | 'boolean' | 'json';
  description?: string;
  default_value?: any;
  required: boolean;
  is_secret: boolean;
}

export interface ProcedureStep {
  step_id: string;
  order_index: number;
  name: string;
  action_type: string;
  target_surface: 'browser' | 'desktop' | 'visual' | 'hybrid';
  locator_schema: Record<string, any>;
  input_bindings: Record<string, any>;
  side_effect_class: SideEffectClass;
  checkpoint_policy: CheckpointPolicy;
  preconditions: Record<string, any>[];
  postconditions: Record<string, any>[];
  timeout_ms: number;
  max_retries: number;
  allow_failure: boolean;
}

export interface ReusableProcedure {
  procedure_id: string;
  version: number;
  name: string;
  description?: string;
  category: string;
  is_draft: boolean;
  is_deprecated: boolean;
  author?: string;
  created_at: string;
  updated_at: string;
  parameters: ProcedureParameter[];
  steps: ProcedureStep[];
  allowed_applications: string[];
  allowed_origins: string[];
  required_permissions: string[];
  validation_status: ProcedureValidationStatus;
  validation_issues: string[];
  static_risk_score: number;
  originating_session_id?: string;
}

export interface CompileProcedureRequest {
  session_id: string;
  name: string;
  description?: string;
  parameterize_inputs?: boolean;
  category?: string;
}

export interface PreflightReport {
  can_execute: boolean;
  procedure_id: string;
  version: number;
  issues: string[];
  missing_parameters: string[];
  missing_permissions: string[];
  required_adapters: string[];
  adapters_ready: boolean;
  emergency_stop_active: boolean;
  session_locked: boolean;
  risk_assessment: Record<string, any>;
}

export interface StateFingerprint {
  fingerprint_id: string;
  timestamp: string;
  active_window_title?: string;
  active_process_name?: string;
  focused_element_id?: string;
  browser_url?: string;
  browser_title?: string;
  visual_summary_hash?: string;
  extra_attributes: Record<string, any>;
}

export interface ExecutionCheckpoint {
  checkpoint_id: string;
  execution_id: string;
  step_id: string;
  step_index: number;
  checkpoint_type: CheckpointType;
  timestamp: string;
  state_fingerprint: StateFingerprint;
  scope_variables: Record<string, any>;
  completed_steps: string[];
  integrity_hash: string;
  can_resume: boolean;
}

export interface ExternalSideEffect {
  effect_id: string;
  execution_id: string;
  step_id: string;
  side_effect_class: SideEffectClass;
  outcome: SideEffectOutcome;
  intent_hash: string;
  target_system: string;
  operation: string;
  parameters: Record<string, any>;
  timestamp: string;
  confirmed_at?: string;
  idempotency_key?: string;
  response_evidence: Record<string, any>;
}

export interface ProcedureExecution {
  execution_id: string;
  procedure_id: string;
  version: number;
  status: ProcedureExecutionStatus;
  mode: ReplayMode;
  started_at: string;
  completed_at?: string;
  current_step_index: number;
  total_steps: number;
  resolved_arguments: Record<string, any>;
  completed_steps: string[];
  failed_steps: string[];
  error_message?: string;
  execution_time_ms: number;
  preflight_report?: PreflightReport;
  checkpoints: ExecutionCheckpoint[];
  side_effects: ExternalSideEffect[];
}

export interface RecoveryPlan {
  plan_id: string;
  execution_id: string;
  failed_step_id?: string;
  checkpoint_id?: string;
  classification: RecoveryClassification;
  can_resume: boolean;
  resume_step_index: number;
  actions_to_skip: string[];
  actions_to_reexecute: string[];
  rationale: string;
  created_at: string;
}

export interface ReliabilityDiagnosticsInfo {
  service_status: string;
  active_recording_sessions: number;
  total_registered_procedures: number;
  active_executions: number;
  total_checkpoints_preserved: number;
  tracked_side_effects_count: number;
  emergency_stop_triggered: boolean;
  interrupted_executions_found: number;
}
