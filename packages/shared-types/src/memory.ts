/**
 * TypeScript contracts and types for Stage 15 Memory Engine.
 */

export type MemoryType = 'working' | 'episodic' | 'semantic' | 'procedural';

export type MemoryScope =
  | 'user'
  | 'applicant_profile'
  | 'workflow'
  | 'task'
  | 'agent'
  | 'project'
  | 'integration'
  | 'shared';

export type MemoryVerificationStatus =
  | 'verified'
  | 'user_confirmed'
  | 'evidence_supported'
  | 'unverified'
  | 'conflicted'
  | 'superseded'
  | 'expired'
  | 'rejected';

export type ConfidenceCategory = 'high' | 'medium' | 'low' | 'unrated';

export type SensitivityCategory =
  | 'public'
  | 'internal'
  | 'personal'
  | 'sensitive'
  | 'restricted'
  | 'secret';

export type VisibilityPolicy = 'scoped' | 'shared' | 'private';

export type SearchMode = 'hybrid' | 'semantic' | 'keyword';

export type RetentionPolicy =
  | 'permanent'
  | 'session'
  | 'task'
  | 'workflow'
  | '30_days'
  | '90_days'
  | '1_year';

export type EmbeddingStatus = 'pending' | 'completed' | 'failed' | 'not_required';

export interface MemoryRecord {
  id: string;
  memory_type: MemoryType;
  title: string;
  content: string;
  summary: string;
  owner_scope: MemoryScope;
  scope_id: string;
  source_type: string;
  source_ref: string;
  provenance: Record<string, unknown>;
  verification_status: MemoryVerificationStatus;
  confidence_category: ConfidenceCategory;
  sensitivity_category: SensitivityCategory;
  visibility_policy: VisibilityPolicy;
  created_at: string;
  updated_at: string;
  last_accessed_at: string;
  expires_at?: string | null;
  superseded_by?: string | null;
  version: number;
  embedding_model_id: string;
  embedding_version: number;
  embedding_status: EmbeddingStatus;
  content_checksum: string;
  retention_policy: RetentionPolicy;
  is_deleted: boolean;
  metadata: Record<string, unknown>;
}

export interface MemorySearchResultItem {
  memory_id: string;
  title: string;
  content_snippet: string;
  memory_type: MemoryType;
  owner_scope: MemoryScope;
  scope_id: string;
  verification_status: MemoryVerificationStatus;
  sensitivity_category: SensitivityCategory;
  similarity_score: number;
  keyword_score: number;
  combined_score: number;
  provenance: Record<string, unknown>;
  created_at: string;
}

export interface MemorySearchResponse {
  results: MemorySearchResultItem[];
  query: string;
  search_mode: SearchMode;
  total_matched: number;
  latency_ms: number;
}

export interface MemoryStatsResponse {
  total_records: number;
  by_type: Record<string, number>;
  by_verification_status: Record<string, number>;
  by_scope: Record<string, number>;
  indexed_records: number;
  pending_embeddings: number;
  conflicts_unresolved: number;
  active_procedures: number;
  vector_dimension: number;
  fts_enabled: boolean;
}

export interface MemoryConflict {
  id: string;
  memory_id_a: string;
  memory_id_b: string;
  conflict_type: string;
  description: string;
  status: string;
  resolution_action?: string | null;
  resolved_by?: string | null;
  created_at: string;
  resolved_at?: string | null;
}

export interface ProceduralMemory {
  id: string;
  procedure_id: string;
  name: string;
  description: string;
  capability_id: string;
  required_inputs: Record<string, unknown>;
  steps: Array<Record<string, unknown>>;
  preconditions: Record<string, unknown>;
  expected_outputs: Record<string, unknown>;
  verification_requirements: Record<string, unknown>;
  required_permissions: string[];
  provenance: Record<string, unknown>;
  version: number;
  validation_status: string;
  success_count: number;
  failure_count: number;
  created_at: string;
  updated_at: string;
}
