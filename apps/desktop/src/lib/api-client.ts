/**
 * Typed API Client for AUTONOM Backend Service
 */

import type {
  EventEnvelope,
  SystemCapabilitiesResponse,
  SystemStatusResponse,
  TaskCancelResponse,
  TaskCreateRequest,
  TaskListResponse,
  TaskResponse,
  TaskResultResponse,
  WorkerListResponse,
} from '@autonom/shared-types';

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
}

export const apiClient = new ApiClient();
