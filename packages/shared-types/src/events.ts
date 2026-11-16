/**
 * Real-time event models and SSE envelope definitions.
 */

export interface EventEnvelope<T = Record<string, unknown>> {
  event_id: string;
  event_type: string;
  timestamp: string;
  correlation_id?: string | null;
  task_id?: string | null;
  payload: T;
}

export interface TaskProgressEventPayload {
  task_id: string;
  progress: number;
  message?: string | null;
  details?: Record<string, unknown>;
}

export interface TaskStateEventPayload {
  task_id: string;
  task_type: string;
  previous_state?: string | null;
  new_state: string;
  reason?: string | null;
}

export interface WorkerEventPayload {
  worker_id: string;
  task_id?: string | null;
  state: 'idle' | 'busy' | 'stopped';
}
