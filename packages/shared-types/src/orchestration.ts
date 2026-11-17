/**
 * Multi-Agent Orchestration types and contracts for AUTONOM (Stage 12).
 */

export type WorkflowStatus =
  | 'created'
  | 'planning'
  | 'plan_ready'
  | 'queued'
  | 'running'
  | 'waiting_for_dependencies'
  | 'waiting_for_authorization'
  | 'paused'
  | 'recovering'
  | 'verifying'
  | 'completed'
  | 'partially_completed'
  | 'failed'
  | 'cancelled';

export type StepStatus =
  | 'pending'
  | 'ready'
  | 'assigned'
  | 'running'
  | 'verifying'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'blocked'
  | 'paused';

export type PriorityLevel =
  | 'critical'
  | 'interactive'
  | 'high'
  | 'normal'
  | 'background';

export type FailureCategory =
  | 'provider_unavailable'
  | 'model_unavailable'
  | 'timeout'
  | 'rate_limit'
  | 'invalid_output'
  | 'failed_verification'
  | 'missing_capability'
  | 'resource_exhausted'
  | 'authorization_required'
  | 'dependency_failure'
  | 'backend_interruption'
  | 'cancelled_by_user'
  | 'unknown_external_outcome';

export type VerificationStatus =
  | 'pass'
  | 'fail'
  | 'needs_review'
  | 'unverifiable';

export type VerificationPolicy =
  | 'schema_validation'
  | 'deterministic_assertion'
  | 'output_contract'
  | 'semantic_review'
  | 'artifact_validation'
  | 'human_judgment';

export interface WorkflowStepDefinition {
  step_id: string;
  title: string;
  description: string;
  capability_id: string;
  dependencies: string[];
  input_bindings: Record<string, any>;
  expected_output_schema?: Record<string, any> | null;
  verification_policy: VerificationPolicy;
  timeout_seconds?: number;
  max_retries?: number;
  requires_authorization?: boolean;
  priority?: PriorityLevel;
}

export interface WorkflowPlan {
  workflow_id: string;
  version: number;
  goal: string;
  steps: WorkflowStepDefinition[];
  success_criteria: string[];
  max_duration_seconds: number;
  max_total_steps: number;
  max_parallel_steps: number;
}

export interface WorkflowStepResponse {
  id: string;
  workflow_id: string;
  plan_id: string;
  step_id: string;
  title: string;
  description: string;
  capability_id: string;
  assigned_agent_id: string | null;
  status: StepStatus;
  dependencies: string[];
  input_bindings: Record<string, any>;
  output_result: Record<string, any> | null;
  error_info: Record<string, any> | null;
  verification_status: VerificationStatus | null;
  retry_count: number;
  max_retries: number;
  timeout_seconds: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface WorkflowResponse {
  id: string;
  title: string;
  goal: string;
  status: WorkflowStatus;
  priority: PriorityLevel;
  active_plan_id: string | null;
  active_plan: WorkflowPlan | null;
  steps: WorkflowStepResponse[];
  context: Record<string, any>;
  constraints: Record<string, any>;
  total_steps: number;
  completed_steps: number;
  failed_steps: number;
  total_cost_usd: number;
  total_tokens: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
}

export interface WorkflowSummary {
  id: string;
  title: string;
  goal: string;
  status: WorkflowStatus;
  priority: PriorityLevel;
  total_steps: number;
  completed_steps: number;
  failed_steps: number;
  total_cost_usd: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowCreateRequest {
  goal: string;
  title?: string | null;
  constraints?: Record<string, any>;
  priority?: PriorityLevel;
  model_preference?: string | null;
  is_local_only?: boolean;
}

export interface WorkflowReplanRequest {
  reason: string;
  failed_step_id?: string | null;
  additional_constraints?: Record<string, any>;
}

export interface AgentDefinition {
  agent_id: string;
  name: string;
  role: string;
  description: string;
  capabilities: string[];
  supported_task_types: string[];
  required_permissions: string[];
  concurrency_limit: number;
  model_preference?: string | null;
  is_available: boolean;
  enabled: boolean;
  implementation_version: string;
  roadmap_stage: string;
}

export interface CapabilityDefinition {
  capability_id: string;
  name: string;
  version: string;
  description: string;
  input_schema: Record<string, any>;
  output_schema: Record<string, any>;
  requires_ai: boolean;
  is_deterministic: boolean;
  default_verification_policy: VerificationPolicy;
  timeout_seconds: number;
  idempotent: boolean;
}

export interface DAGVisualizationData {
  steps: Array<{
    step_id: string;
    title: string;
    capability_id: string;
    dependencies: string[];
  }>;
  topological_order: string[];
  stages: string[][];
}

export interface OrchestrationStats {
  total_workflows: number;
  completed_workflows: number;
  running_workflows: number;
  paused_workflows: number;
  failed_workflows: number;
  completion_rate_percent: number;
}

// =========================================================================
// Stage 13: Specialist Agent Framework Types
// =========================================================================

export type AgentCategory =
  | 'orchestration'
  | 'recruitment'
  | 'computer'
  | 'development'
  | 'research'
  | 'productivity'
  | 'creative'
  | 'communication'
  | 'automation';

export type AvailabilityState =
  | 'operational'
  | 'limited'
  | 'planned'
  | 'unavailable'
  | 'disabled';

export interface AgentModelProfile {
  preferred_model?: string | null;
  task_category: string;
  local_first: boolean;
  cloud_permitted: boolean;
  fallback_model?: string | null;
  max_context_tokens: number;
  max_output_tokens: number;
  temperature: number;
  timeout_seconds: number;
  cost_budget_usd: number;
}

export interface AgentContextPolicy {
  allowed_input_keys: string[];
  isolation_level: string;
  allow_credentials: boolean;
  allow_system_logs: boolean;
  retention_policy: string;
}

export interface AgentExecutionLimits {
  timeout_seconds: number;
  concurrency_limit: number;
  max_retries: number;
  max_model_calls: number;
}

export interface AgentManifest {
  agent_id: string;
  name: string;
  role: string;
  description: string;
  category: AgentCategory;
  version: string;
  capabilities: string[];
  required_permissions: string[];
  allowed_tools: string[];
  model_profile: AgentModelProfile;
  context_policy: AgentContextPolicy;
  execution_limits: AgentExecutionLimits;
  verification_policy: string;
  availability_state: AvailabilityState;
  roadmap_stage: string;
  system_instructions: string;
  instructions_version: string;
  enabled: boolean;
  metadata?: Record<string, any>;
}

export interface AgentStatusResponse {
  agent_id: string;
  name: string;
  category: AgentCategory;
  availability_state: AvailabilityState;
  enabled: boolean;
  active_assignments: number;
  concurrency_limit: number;
  is_busy: boolean;
  preferred_model?: string | null;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  last_execution_at?: string | null;
}

export interface AgentConfigurationUpdate {
  enabled?: boolean;
  preferred_model?: string | null;
  concurrency_limit?: number;
  timeout_seconds?: number;
  temperature?: number;
  max_tokens?: number;
  local_first?: boolean;
  cloud_permitted?: boolean;
  allowed_capabilities?: string[];
  custom_settings?: Record<string, any>;
}

export interface AgentExecutionHistoryItem {
  id: string;
  agent_id: string;
  workflow_id: string;
  step_id: string;
  status: string;
  model_used?: string | null;
  tokens_used: number;
  cost_usd: number;
  duration_ms: number;
  created_at: string;
  completed_at?: string | null;
}

