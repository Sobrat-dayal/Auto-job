/**
 * System and Worker Status types matching FastAPI backend models.
 */

export interface WorkerInfo {
  worker_id: string;
  name: string;
  state: 'idle' | 'busy' | 'stopped';
  current_task_id: string | null;
  tasks_processed: number;
  uptime_seconds: number;
}

export interface WorkerListResponse {
  total_workers: number;
  active_workers: number;
  idle_workers: number;
  max_capacity: number;
  workers: WorkerInfo[];
}

export interface SystemStatusResponse {
  service: string;
  version: string;
  status: string;
  timestamp: string;
  uptime_seconds: number;
  workers: {
    total: number;
    active: number;
    idle: number;
    max_capacity: number;
  };
  tasks: {
    queued: number;
    active: number;
  };
}

export interface SystemCapabilitiesResponse {
  service: string;
  supported_task_types: string[];
  max_concurrency: number;
  queue_capacity: number;
  features: Record<string, boolean>;
}
