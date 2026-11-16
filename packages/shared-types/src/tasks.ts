/**
 * Durable Task & Workflow State Machine
 */

export type TaskStatus =
  | 'Created'
  | 'Queued'
  | 'Planning'
  | 'WaitingForDependencies'
  | 'Running'
  | 'WaitingForAuthorization'
  | 'Paused'
  | 'Retrying'
  | 'Completed'
  | 'Failed'
  | 'Cancelled';

export type TaskPriority = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10; // 1 is highest

export interface TaskRecord {
  id: string;
  parentTaskId: string | null;
  workflowId: string | null;
  agentId: string;
  taskType: string;
  priority: TaskPriority;
  status: TaskStatus;
  idempotencyKey: string | null;
  parameters: Record<string, unknown>;
  result: Record<string, unknown> | null;
  errorMessage: string | null;
  retryCount: number;
  maxRetries: number;
  timeoutSeconds: number;
  createdAt: string;
  startedAt: string | null;
  completedAt: string | null;
}

export interface TaskDependency {
  taskId: string;
  dependsOnTaskId: string;
}

export interface VerificationRecord {
  id: string;
  taskId: string;
  stepIndex: number;
  verificationRule: string;
  preStateHash: string | null;
  postStateHash: string | null;
  verdict: 'VERIFIED' | 'FAILED' | 'INDETERMINATE';
  diagnosticInfo: Record<string, unknown> | null;
  createdAt: string;
}
