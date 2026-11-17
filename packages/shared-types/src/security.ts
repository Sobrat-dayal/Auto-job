/**
 * Security, Authorization, Grants, Emergency Stop, and Audit Types for AUTONOM (Stage 14).
 */

export type RiskLevel = 'low' | 'moderate' | 'high' | 'critical';

export type PermissionCategory =
  | 'system'
  | 'recruitment'
  | 'filesystem'
  | 'network'
  | 'credential'
  | 'browser'
  | 'desktop'
  | 'communication'
  | 'code'
  | 'creative';

export type ActionEffect = 'allow' | 'deny' | 'require_approval';

export type ApprovalStatus = 'pending' | 'approved' | 'denied' | 'expired' | 'consumed';

export type ApprovalMode = 'one_time' | 'session' | 'workflow' | 'standing_grant';

export type GrantType = 'standing' | 'workflow_scoped' | 'task_scoped' | 'session_scoped';

export type ReasonCode =
  | 'EMERGENCY_STOP_ENGAGED'
  | 'AUTOMATION_PAUSED'
  | 'CREDENTIAL_ACCESS_RESTRICTED'
  | 'SECURITY_INVARIANT_VIOLATION'
  | 'EXPLICIT_DENY_POLICY'
  | 'APPROVAL_REQUIRED_BY_POLICY'
  | 'EXPLICIT_ALLOW_POLICY'
  | 'PREAUTHORIZED_GRANT'
  | 'APPROVAL_GRANTED'
  | 'APPROVAL_EXPIRED'
  | 'HIGH_RISK_ACTION'
  | 'DEFAULT_DENY'
  | 'READ_ONLY_BASELINE';

export interface ActorContext {
  actor_id: string;
  actor_type: 'user' | 'agent' | 'system';
  agent_id?: string | null;
  workflow_id?: string | null;
  step_id?: string | null;
  task_id?: string | null;
  session_id?: string | null;
  correlation_id?: string | null;
}

export interface SecurityResourceScope {
  allowed_paths?: string[];
  allowed_origins?: string[];
  allowed_sources?: string[];
  excluded_companies?: string[];
  min_match_score?: number;
  max_applications_per_day?: number;
  unrestricted?: boolean;
  [key: string]: unknown;
}

export interface AuthorizationPolicy {
  id: string;
  name: string;
  description: string;
  version: number;
  is_enabled: boolean;
  is_system: boolean;
  subject_scope: string;
  category_scope: string;
  action_scope: string[];
  resource_scope: SecurityResourceScope;
  effect: ActionEffect;
  conditions: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AuthorizationGrant {
  id: string;
  name: string;
  description?: string;
  grant_type: GrantType;
  subject_id: string;
  allowed_categories: string[];
  allowed_capabilities: string[];
  resource_scope: SecurityResourceScope;
  max_uses?: number | null;
  use_count: number;
  workflow_id?: string | null;
  task_id?: string | null;
  granted_by: string;
  granted_at: string;
  expires_at?: string | null;
  is_active: boolean;
  is_revoked: boolean;
  revocation_reason?: string | null;
}

export interface ApprovalRequest {
  id: string;
  correlation_id?: string | null;
  workflow_id?: string | null;
  step_id?: string | null;
  agent_id?: string | null;
  capability_id: string;
  action: string;
  parameters_digest: string;
  parameters_payload: Record<string, unknown>;
  resource_type: string;
  resource_id?: string | null;
  risk_level: RiskLevel;
  reason: string;
  approval_mode: ApprovalMode;
  status: ApprovalStatus;
  requested_at: string;
  expires_at: string;
  decided_at?: string | null;
  decided_by?: string | null;
  decision_reason?: string | null;
  consumed_at?: string | null;
}

export interface AuthorizationDecision {
  outcome: ActionEffect;
  reason_code: ReasonCode;
  explanation: string;
  policy_id?: string | null;
  grant_id?: string | null;
  approval_id?: string | null;
  risk_level: RiskLevel;
  correlation_id?: string | null;
  timestamp: string;
}

export interface EmergencyStopState {
  is_active: boolean;
  is_paused: boolean;
  engaged_at?: string | null;
  engaged_by?: string | null;
  reason?: string | null;
  active_operations_aborted: number;
  pending_approvals_frozen: number;
}

export interface SecurityAuditEntry {
  id: string;
  correlation_id?: string | null;
  actor_id: string;
  actor_type: string;
  agent_id?: string | null;
  workflow_id?: string | null;
  step_id?: string | null;
  capability_id: string;
  action: string;
  parameters_digest: string;
  outcome: ActionEffect;
  reason_code: ReasonCode;
  risk_level: RiskLevel;
  explanation: string;
  policy_id?: string | null;
  grant_id?: string | null;
  timestamp: string;
}

export interface PermissionTaxonomyItem {
  id: string;
  name: string;
  description: string;
  default_risk: RiskLevel;
  requires_approval_by_default: boolean;
  is_grantable: boolean;
  category: PermissionCategory;
}

// Backward compatibility types
export type AutonomyTier = 1 | 2 | 3;
export type ActionCategory =
  | 'job_search'
  | 'document_tailor'
  | 'application_submit'
  | 'email_send'
  | 'payment_spend'
  | 'shell_exec'
  | 'sensitive_attestation';
