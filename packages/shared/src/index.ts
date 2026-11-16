// AUTONOM Shared Types & API Contracts

export interface BackendHealthResponse {
  status: 'healthy' | 'degraded' | 'offline';
  version: string;
  uptime_seconds: number;
  database: {
    connected: boolean;
    mode: string;
    path: string;
  };
  subsystems: {
    agent_engine: 'ready' | 'busy' | 'error';
    computer_interaction: 'ready' | 'active' | 'error';
    job_crawler: 'idle' | 'scanning' | 'error';
  };
}

export interface SystemTelemetry {
  os: string;
  platform: string;
  python_version: string;
  cpu_usage_percent: number;
  memory: {
    total_mb: number;
    available_mb: number;
    process_rss_mb: number;
  };
  monitors: Array<{
    index: number;
    width: number;
    height: number;
    scale_factor: number;
    is_primary: boolean;
  }>;
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'planning' | 'executing' | 'verifying' | 'awaiting_approval' | 'error';
  current_task: string | null;
  tasks_completed: number;
  model: string;
}

export interface AgentSwarmStatus {
  agents: AgentInfo[];
  total_active_tasks: number;
}

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  remote_type: 'remote' | 'hybrid' | 'onsite';
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  url: string;
  platform: 'linkedin' | 'indeed' | 'greenhouse' | 'lever' | 'workday' | 'glassdoor' | 'other';
  match_score: number;
  status:
    | 'discovered'
    | 'matched'
    | 'tailored'
    | 'review_required'
    | 'applied'
    | 'interviewing'
    | 'rejected';
  posted_date: string;
}

export interface JobsListResponse {
  total: number;
  jobs: JobPosting[];
  page: number;
  limit: number;
}

export interface ApprovalRequest {
  id: string;
  task_id: string;
  agent_id: string;
  tier: 1 | 2 | 3;
  action_type: 'job_submission' | 'file_write' | 'payment' | 'email_send' | 'sensitive_attestation';
  target_resource: string;
  summary: string;
  details: Record<string, unknown>;
  created_at: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
}

export interface ComputerInteractionCommand {
  modality: 'visual' | 'structural' | 'hybrid';
  action: 'click' | 'move' | 'type' | 'scroll' | 'drag' | 'focus';
  target?: {
    automation_id?: string;
    selector?: string;
    text?: string;
    x?: number;
    y?: number;
  };
  text_to_type?: string;
}
