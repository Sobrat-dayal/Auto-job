/**
 * AUTONOM — Shared TypeScript Types for AI Model Gateway (Stage 11)
 */

export type TaskCategory =
  | 'general_conversation'
  | 'short_reasoning'
  | 'complex_reasoning'
  | 'coding'
  | 'code_review'
  | 'research_synthesis'
  | 'document_writing'
  | 'job_description_analysis'
  | 'resume_analysis'
  | 'screening_answer_drafting'
  | 'summarization'
  | 'structured_extraction'
  | 'classification'
  | 'planning'
  | 'vision_interpretation'
  | 'computer_control_grounding';

export type RoutingStrategy =
  | 'local_first'
  | 'cloud_first'
  | 'lowest_cost'
  | 'lowest_latency'
  | 'capability_first'
  | 'manual'
  | 'privacy_restricted';

export type ModelCapability =
  | 'chat'
  | 'streaming'
  | 'structured_output'
  | 'tool_calling'
  | 'vision'
  | 'embeddings'
  | 'reasoning';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  source: 'reported' | 'estimated' | 'unknown';
}

export interface ModelPricing {
  input_cost_per_million: number;
  output_cost_per_million: number;
}

export interface ModelInfo {
  id: string; // provider_id:model_id
  provider_id: string;
  model_id: string;
  display_name: string;
  provider_type: 'local' | 'cloud';
  is_available: boolean;
  context_window: number;
  max_output_tokens: number;
  capabilities: string[];
  pricing: ModelPricing;
  reported_size_bytes?: number | null;
  quantization?: string | null;
  status_message?: string | null;
  last_discovered_at: string;
}

export interface ProviderHealth {
  provider_id: string;
  is_healthy: boolean;
  status: 'available' | 'unavailable' | 'degraded' | 'auth_required' | 'disabled';
  latency_ms?: number | null;
  error_message?: string | null;
  last_checked_at: string;
}

export interface ProviderSummary {
  provider_id: string;
  display_name: string;
  provider_type: 'local' | 'cloud';
  is_healthy: boolean;
  status: string;
  latency_ms?: number | null;
}

export interface RoutingDecision {
  selected_provider_id: string;
  selected_model_id: string;
  strategy_used: RoutingStrategy;
  rule_applied: string;
  explanation: string;
  candidates_considered: string[];
  fallbacks_available: string[];
  is_local: boolean;
}

export interface InferenceRequest {
  request_id?: string;
  task_id?: string | null;
  task_category?: TaskCategory;
  messages: ChatMessage[];
  system_prompt?: string | null;
  provider_preference?: string | null;
  model_preference?: string | null;
  routing_strategy?: RoutingStrategy;
  temperature?: number;
  top_p?: number;
  max_tokens?: number;
  context_budget?: number;
  timeout_seconds?: number;
  stream?: boolean;
  response_format?: 'text' | 'json_object' | 'json_schema';
  json_schema?: Record<string, unknown> | null;
  allow_cloud_fallback?: boolean;
  is_local_only?: boolean;
  max_cost_usd?: number | null;
  required_capabilities?: string[];
  correlation_id?: string | null;
}

export interface InferenceResponse {
  request_id: string;
  provider_id: string;
  model_id: string;
  content: string;
  finish_reason?: string | null;
  usage: TokenUsage;
  estimated_cost_usd: number;
  latency_ms: number;
  time_to_first_token_ms?: number | null;
  routing_decision?: RoutingDecision | null;
  structured_data?: unknown | null;
  created_at: string;
}

export interface InferenceChunk {
  request_id: string;
  provider_id: string;
  model_id: string;
  delta: string;
  finish_reason?: string | null;
  usage?: TokenUsage | null;
}

export interface HardwareTelemetry {
  system_ram_total_mb: number;
  system_ram_available_mb: number;
  system_ram_used_mb: number;
  system_ram_percent: number;
  gpu_name?: string | null;
  gpu_vram_total_mb?: number | null;
  gpu_vram_used_mb?: number | null;
  gpu_vram_available_mb?: number | null;
  gpu_vram_percent?: number | null;
  active_local_model?: string | null;
  active_inference_count: number;
  local_concurrency_limit: number;
  timestamp: string;
}

export interface ProviderUsageItem {
  provider_id: string;
  requests: number;
  tokens: number;
  cost_usd: number;
}

export interface ModelUsageItem {
  provider_id: string;
  model_id: string;
  requests: number;
  tokens: number;
  cost_usd: number;
}

export interface AIUsageSummary {
  time_range_days: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  cancelled_requests: number;
  success_rate_percent: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_estimated_cost_usd: number;
  average_latency_ms: number;
  local_requests: number;
  cloud_requests: number;
  by_provider: ProviderUsageItem[];
  by_model: ModelUsageItem[];
}

export interface AIRoutingPreference {
  category: TaskCategory;
  preferred_provider: string;
  preferred_model: string;
  fallback_provider?: string | null;
  fallback_model?: string | null;
  is_local_only: boolean;
  updated_at: string;
}
