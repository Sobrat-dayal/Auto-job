/**
 * Durable Task & Workflow State Machine and Task Execution API schemas.
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

export type TaskExecutionState =
  | 'created'
  | 'queued'
  | 'planning'
  | 'waiting_dependencies'
  | 'running'
  | 'waiting_auth'
  | 'paused'
  | 'retrying'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type TaskExecutionPriority = 'critical' | 'high' | 'normal' | 'low' | 'batch';

export interface TaskCreateRequest {
  task_type: string;
  payload?: Record<string, unknown>;
  priority?: TaskExecutionPriority;
  timeout_seconds?: number;
  correlation_id?: string | null;
}

export interface TaskResponse {
  task_id: string;
  task_type: string;
  state: TaskExecutionState;
  priority: TaskExecutionPriority;
  progress: number;
  message?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  error?: string | null;
  correlation_id?: string | null;
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
}

export interface TaskResultResponse {
  task_id: string;
  state: TaskExecutionState;
  result?: Record<string, unknown> | null;
  error?: string | null;
  completed_at?: string | null;
}

export interface TaskCancelResponse {
  task_id: string;
  state: TaskExecutionState;
  cancelled: boolean;
  message: string;
}

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
