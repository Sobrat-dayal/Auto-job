/**
 * Typed API Client for AUTONOM Backend Service
 */

import type {
  BackupManifest,
  CredentialStatus,
  EventEnvelope,
  ProfileSummary,
  RestoreResponse,
  StorageHealth,
  StorageStatus,
  SystemCapabilitiesResponse,
  SystemStatusResponse,
  TaskCancelResponse,
  TaskCreateRequest,
  TaskListResponse,
  TaskResponse,
  TaskResultResponse,
  WorkerListResponse,
} from '@autonom/shared-types';
import type {
  DashboardActivityEvent,
  DashboardOverviewResponse,
  DashboardTaskTrendsResponse,
  TaskHistoryEvent,
} from '@/types/dashboard';
import type {
  ApplicationItem,
  ApplicationListResponse,
  ArtifactItem,
  ArtifactListResponse,
  JobListingItem,
  JobListResponse,
} from '@/types/modules';

export interface ApiClientConfig {
  baseUrl: string;
  timeoutMs: number;
}

export interface BackendHealth {
  status: string;
  version: string;
  uptime_seconds: number;
  environment: string;
  is_loopback: boolean;
  timestamp: string;
}

export interface BackendVersion {
  app_name: string;
  version: string;
  api_version: string;
  python_version: string;
  platform: string;
}

export interface BackendReadiness {
  ready: boolean;
  status: string;
  checks: Record<string, boolean>;
  timestamp: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const DEFAULT_CONFIG: ApiClientConfig = {
  baseUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8765',
  timeoutMs: 5000,
};

export class ApiClient {
  private config: ApiClientConfig;

  constructor(config: Partial<ApiClientConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  get baseUrl(): string {
    return this.config.baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer dev-local-autonom-key',
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorData: unknown;
        try {
          errorData = await response.json();
        } catch {
          errorData = await response.text();
        }
        throw new ApiError(`HTTP Error ${response.status}`, response.status, errorData);
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        throw err;
      }
      if (err instanceof Error && err.name === 'AbortError') {
        throw new ApiError(`Request timeout after ${this.config.timeoutMs}ms`, 408);
      }
      throw new ApiError(
        err instanceof Error ? err.message : 'Failed to connect to backend service',
        0
      );
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // System & Health Endpoints
  async getHealth(): Promise<BackendHealth> {
    return this.request<BackendHealth>('/api/v1/health');
  }

  async getVersion(): Promise<BackendVersion> {
    return this.request<BackendVersion>('/api/v1/version');
  }

  async getReadiness(): Promise<BackendReadiness> {
    return this.request<BackendReadiness>('/api/v1/ready');
  }

  async getSystemStatus(): Promise<SystemStatusResponse> {
    return this.request<SystemStatusResponse>('/api/v1/system/status');
  }

  async getSystemCapabilities(): Promise<SystemCapabilitiesResponse> {
    return this.request<SystemCapabilitiesResponse>('/api/v1/system/capabilities');
  }

  // Worker Management
  async getWorkers(): Promise<WorkerListResponse> {
    return this.request<WorkerListResponse>('/api/v1/workers');
  }

  // Task Execution Endpoints
  async listTasks(): Promise<TaskListResponse> {
    return this.request<TaskListResponse>('/api/v1/tasks');
  }

  async createTask(request: TaskCreateRequest): Promise<TaskResponse> {
    return this.request<TaskResponse>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getTask(taskId: string): Promise<TaskResponse> {
    return this.request<TaskResponse>(`/api/v1/tasks/${taskId}`);
  }

  async getTaskResult(taskId: string): Promise<TaskResultResponse> {
    return this.request<TaskResultResponse>(`/api/v1/tasks/${taskId}/result`);
  }

  async cancelTask(taskId: string): Promise<TaskCancelResponse> {
    return this.request<TaskCancelResponse>(`/api/v1/tasks/${taskId}/cancel`, {
      method: 'POST',
    });
  }

  // Event System
  async getRecentEvents(limit: number = 50): Promise<EventEnvelope[]> {
    return this.request<EventEnvelope[]>(`/api/v1/events/recent?limit=${limit}`);
  }

  getEventStreamUrl(): string {
    return `${this.config.baseUrl}/api/v1/events/stream`;
  }

  // Storage & Database Diagnostics
  async getStorageStatus(): Promise<StorageStatus> {
    return this.request<StorageStatus>('/api/v1/storage/status');
  }

  async getStorageHealth(): Promise<StorageHealth> {
    return this.request<StorageHealth>('/api/v1/storage/health');
  }

  async listBackups(): Promise<BackupManifest[]> {
    return this.request<BackupManifest[]>('/api/v1/storage/backups');
  }

  async createBackup(): Promise<BackupManifest> {
    return this.request<BackupManifest>('/api/v1/storage/backups', {
      method: 'POST',
    });
  }

  async restoreBackup(filename: string): Promise<RestoreResponse> {
    return this.request<RestoreResponse>('/api/v1/storage/restore', {
      method: 'POST',
      body: JSON.stringify({ filename, confirm: true }),
    });
  }

  // Profiles & Credentials
  async listProfiles(): Promise<ProfileSummary[]> {
    return this.request<ProfileSummary[]>('/api/v1/profiles');
  }

  async getCredentialStatus(): Promise<CredentialStatus[]> {
    return this.request<CredentialStatus[]>('/api/v1/integrations/credentials/status');
  }

  // Dashboard Aggregates (Stage 08)
  async getDashboardOverview(): Promise<DashboardOverviewResponse> {
    return this.request<DashboardOverviewResponse>('/api/v1/dashboard/overview');
  }

  async getDashboardTaskTrends(
    window: 'today' | '7d' | '30d' = '7d'
  ): Promise<DashboardTaskTrendsResponse> {
    return this.request<DashboardTaskTrendsResponse>(
      `/api/v1/dashboard/task-trends?window=${window}`
    );
  }

  async getDashboardActivity(limit: number = 50): Promise<DashboardActivityEvent[]> {
    return this.request<DashboardActivityEvent[]>(`/api/v1/dashboard/activity?limit=${limit}`);
  }

  async getTaskHistory(taskId: string): Promise<TaskHistoryEvent[]> {
    return this.request<TaskHistoryEvent[]>(`/api/v1/tasks/${taskId}/history`);
  }

  // Jobs & Applications (Stage 09 Module Endpoints)
  async listJobs(
    params: {
      status?: string;
      company?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<JobListResponse> {
    const query = new URLSearchParams();
    if (params.status) query.set('status', params.status);
    if (params.company) query.set('company', params.company);
    if (params.limit) query.set('limit', String(params.limit));
    if (params.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return this.request<JobListResponse>(`/api/v1/jobs${qs ? `?${qs}` : ''}`);
  }

  async getJob(jobId: string): Promise<JobListingItem> {
    return this.request<JobListingItem>(`/api/v1/jobs/${jobId}`);
  }

  async listApplications(
    params: {
      status?: string;
      profileId?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<ApplicationListResponse> {
    const query = new URLSearchParams();
    if (params.status) query.set('status', params.status);
    if (params.profileId) query.set('profile_id', params.profileId);
    if (params.limit) query.set('limit', String(params.limit));
    if (params.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return this.request<ApplicationListResponse>(`/api/v1/applications${qs ? `?${qs}` : ''}`);
  }

  async getApplication(applicationId: string): Promise<ApplicationItem> {
    return this.request<ApplicationItem>(`/api/v1/applications/${applicationId}`);
  }

  async listArtifacts(
    params: {
      artifactType?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<ArtifactListResponse> {
    const query = new URLSearchParams();
    if (params.artifactType) query.set('artifact_type', params.artifactType);
    if (params.limit) query.set('limit', String(params.limit));
    if (params.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return this.request<ArtifactListResponse>(`/api/v1/artifacts${qs ? `?${qs}` : ''}`);
  }

  async getArtifact(artifactId: string): Promise<ArtifactItem> {
    return this.request<ArtifactItem>(`/api/v1/artifacts/${artifactId}`);
  }
}

export const apiClient = new ApiClient();
