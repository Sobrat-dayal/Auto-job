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

// Stage 05: Desktop Shell & Native Integration Types

export type BackendProcessState =
  | 'Stopped'
  | 'Starting'
  | 'Connecting'
  | 'Ready'
  | 'Degraded'
  | 'Restarting'
  | 'Failed'
  | 'Stopping';

export interface AppInfo {
  name: string;
  version: string;
  tauri_version: string;
  os: string;
  arch: string;
}

export interface SavedWindowState {
  x: number;
  y: number;
  width: number;
  height: number;
  maximized: boolean;
  selected_module: string;
}

export interface DesktopSettings {
  close_to_tray: boolean;
  start_at_login: boolean;
  notifications_enabled: boolean;
  notify_on_task_completion: boolean;
  notify_on_backend_events: boolean;
  window: SavedWindowState;
}

export interface DesktopStatus {
  app_info: AppInfo;
  active_tasks_count: number;
  settings: DesktopSettings;
}

export interface BackendProcessStatus {
  state: BackendProcessState;
  pid: number | null;
  port: number;
  uptime_seconds: number;
  restart_count: number;
  max_restarts: number;
  last_error: string | null;
  backend_mode: string;
  database_ready: boolean;
}
