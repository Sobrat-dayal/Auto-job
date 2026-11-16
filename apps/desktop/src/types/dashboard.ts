/**
 * Dashboard & Operational Telemetry Types for AUTONOM Command Center (Stage 08)
 */

export interface DashboardTasksSummary {
  running: number;
  queued: number;
  completed: number;
  failed: number;
  cancelled: number;
  total: number;
}

export type AgentOperationState =
  | 'unavailable'
  | 'offline'
  | 'idle'
  | 'starting'
  | 'planning'
  | 'running'
  | 'paused'
  | 'waiting_approval'
  | 'recovering'
  | 'completed'
  | 'failed'
  | 'degraded';

export interface AgentOperationStatus {
  id: string;
  name: string;
  role: string;
  status: AgentOperationState;
  target_stage: string;
  is_available: boolean;
  current_task?: string | null;
  progress?: number | null;
  last_activity?: string | null;
  successful_tasks: number;
  failed_tasks: number;
  message: string;
}

export interface RecruitmentSummary {
  jobs_discovered: number;
  jobs_discovered_today: number;
  active_listings: number;
  applications_total: number;
  applications_submitted: number;
  pipeline_stages: Record<string, number>;
  automated_scouting_enabled: boolean;
  automated_scouting_message: string;
}

export interface DashboardWorkersStatus {
  total: number;
  active: number;
  idle: number;
  max_capacity: number;
}

export interface DashboardOverviewResponse {
  system_status: 'operational' | 'degraded' | 'disconnected';
  uptime_seconds: number;
  backend_connected: boolean;
  task_dispatch_status: 'active' | 'paused';
  ai_swarm_status: 'scheduled_stage_12' | 'active' | 'degraded';
  tasks_summary: DashboardTasksSummary;
  agents: AgentOperationStatus[];
  recruitment: RecruitmentSummary;
  workers: DashboardWorkersStatus;
  pending_actions_count: number;
  timestamp: string;
}

export interface TaskTrendDataPoint {
  date: string;
  created: number;
  completed: number;
  failed: number;
  cancelled: number;
  avg_duration_seconds: number;
}

export interface DashboardTaskTrendsResponse {
  window: 'today' | '7d' | '30d';
  data_points: TaskTrendDataPoint[];
  total_volume: number;
  overall_success_rate: number;
}

export interface DashboardActivityEvent {
  id: string;
  task_id: string;
  event_type: string;
  timestamp: string;
  state_transition?: string | null;
  metadata: Record<string, unknown>;
  correlation_id?: string | null;
}

export interface TaskHistoryEvent {
  id: string;
  task_id: string;
  event_type: string;
  timestamp: string;
  state_transition?: string | null;
  metadata?: Record<string, unknown>;
  correlation_id?: string | null;
}
