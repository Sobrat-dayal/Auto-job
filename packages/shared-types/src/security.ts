/**
 * Security & Autonomy Policy Data Types
 */

export type AutonomyTier = 1 | 2 | 3;

export type ActionCategory =
  | 'job_search'
  | 'document_tailor'
  | 'application_submit'
  | 'email_send'
  | 'payment_spend'
  | 'shell_exec'
  | 'sensitive_attestation';

export interface AuthorizationPolicy {
  id: string;
  scopeName: string;
  tier: AutonomyTier;
  isAdvanceGranted: boolean;
  expiresAt: string | null;
  trustedDomains: string[];
  maxApplicationsPerDay: number;
  dailySpendLimitUsd: number;
  createdAt: string;
}

export interface ApprovalRequest {
  id: string;
  taskId: string;
  agentId: string;
  tier: AutonomyTier;
  actionType: ActionCategory;
  targetResource: string;
  summary: string;
  details: Record<string, unknown>;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  createdAt: string;
  resolvedAt: string | null;
  resolvedBy: string | null;
}

export interface AuditLogEntry {
  id: number;
  timestamp: string;
  agentId: string;
  taskId: string | null;
  action: string;
  targetResource: string | null;
  preStateHash: string | null;
  postStateHash: string | null;
  metadata: Record<string, unknown>;
}
