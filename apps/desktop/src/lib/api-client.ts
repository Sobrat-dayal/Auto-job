/**
 * Typed API Client for AUTONOM Backend Service
 */

import type {
  AllSettingsResponse,
  BackupManifest,
  CredentialStatus,
  EventEnvelope,
  IntegrationConfigurationResponse,
  ProfileSummary,
  RestoreResponse,
  SettingsExportPayload,
  SettingsImportPayload,
  SettingsSchemaMetadataResponse,
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
  AIUsageSummary,
  HardwareTelemetry,
  InferenceRequest,
  InferenceResponse,
  ModelInfo,
  ProviderHealth,
  ProviderSummary,
  RoutingDecision,
  AIRoutingPreference,
  TaskCategory,
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

  // Centralized Settings (Stage 10)
  async getAllSettings(): Promise<AllSettingsResponse> {
    return this.request<AllSettingsResponse>('/api/v1/settings/all');
  }

  async getSettingCategory<T>(category: string): Promise<T> {
    const res = await this.request<{ category: string; value: T }>(`/api/v1/settings/${category}`);
    return res.value;
  }

  async updateSettingCategory<T>(category: string, value: Partial<T>): Promise<T> {
    const res = await this.request<{ category: string; value: T }>(`/api/v1/settings/${category}`, {
      method: 'PATCH',
      body: JSON.stringify(value),
    });
    return res.value;
  }

  async resetSettingCategory<T>(category: string): Promise<T> {
    const res = await this.request<{ reset: boolean; category: string; defaults: T }>(
      `/api/v1/settings/${category}/reset`,
      { method: 'POST' }
    );
    return res.defaults;
  }

  async exportSettings(): Promise<SettingsExportPayload> {
    return this.request<SettingsExportPayload>('/api/v1/settings/export');
  }

  async importSettings(
    payload: SettingsImportPayload
  ): Promise<{ success: boolean; imported_categories: string[]; total_categories: number }> {
    return this.request<{
      success: boolean;
      imported_categories: string[];
      total_categories: number;
    }>('/api/v1/settings/import', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getSettingsSchema(): Promise<SettingsSchemaMetadataResponse> {
    return this.request<SettingsSchemaMetadataResponse>('/api/v1/settings/schema');
  }

  async getIntegrationConfigurations(): Promise<IntegrationConfigurationResponse> {
    return this.request<IntegrationConfigurationResponse>('/api/v1/integrations/configurations');
  }

  async storeCredential(
    provider: string,
    secretValue: string,
    credentialType: string = 'api_key'
  ): Promise<unknown> {
    return this.request('/api/v1/integrations/credentials', {
      method: 'POST',
      body: JSON.stringify({
        provider,
        secret_value: secretValue,
        credential_type: credentialType,
      }),
    });
  }

  async deleteCredential(provider: string): Promise<unknown> {
    return this.request(`/api/v1/integrations/credentials/${provider}`, {
      method: 'DELETE',
    });
  }

  // =========================================================================
  // AI Model Gateway Endpoints (Stage 11)
  // =========================================================================

  async getAIProviders(): Promise<ProviderSummary[]> {
    return this.request<ProviderSummary[]>('/api/v1/ai/providers');
  }

  async getAIProviderHealth(providerId: string): Promise<ProviderHealth> {
    return this.request<ProviderHealth>(`/api/v1/ai/providers/${providerId}/health`);
  }

  async getAIModels(providerId?: string): Promise<ModelInfo[]> {
    const query = providerId ? `?provider_id=${encodeURIComponent(providerId)}` : '';
    return this.request<ModelInfo[]>(`/api/v1/ai/models${query}`);
  }

  async getAIModel(providerId: string, modelId: string): Promise<ModelInfo> {
    return this.request<ModelInfo>(`/api/v1/ai/models/${providerId}/${modelId}`);
  }

  async refreshAIModels(): Promise<ModelInfo[]> {
    return this.request<ModelInfo[]>('/api/v1/ai/models/refresh', {
      method: 'POST',
    });
  }

  async loadLocalAIModel(
    modelId: string
  ): Promise<{ status: string; model_id: string; currently_loaded: string | null }> {
    return this.request('/api/v1/ai/models/local/load', {
      method: 'POST',
      body: JSON.stringify({ model_id: modelId }),
    });
  }

  async unloadLocalAIModel(modelId: string): Promise<{ status: string; model_id: string }> {
    return this.request('/api/v1/ai/models/local/unload', {
      method: 'POST',
      body: JSON.stringify({ model_id: modelId }),
    });
  }

  async createInferenceRequest(request: InferenceRequest): Promise<InferenceResponse> {
    return this.request<InferenceResponse>('/api/v1/ai/requests', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async previewAIRoute(request: InferenceRequest): Promise<RoutingDecision> {
    return this.request<RoutingDecision>('/api/v1/ai/route/preview', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async cancelAIRequest(requestId: string): Promise<{ request_id: string; cancelled: boolean }> {
    return this.request(`/api/v1/ai/requests/${requestId}/cancel`, {
      method: 'POST',
    });
  }

  async getAIHardwareResources(): Promise<HardwareTelemetry> {
    return this.request<HardwareTelemetry>('/api/v1/ai/resources');
  }

  async getAIUsageSummary(days: number = 30): Promise<AIUsageSummary> {
    return this.request<AIUsageSummary>(`/api/v1/ai/usage?days=${days}`);
  }

  async listInferenceRequests(params?: {
    limit?: number;
    offset?: number;
    provider_id?: string;
    status?: string;
    category?: string;
  }): Promise<{ items: any[]; total: number }> {
    const q = new URLSearchParams();
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.offset) q.set('offset', String(params.offset));
    if (params?.provider_id) q.set('provider_id', params.provider_id);
    if (params?.status) q.set('status', params.status);
    if (params?.category) q.set('category', params.category);
    return this.request(`/api/v1/ai/requests?${q.toString()}`);
  }

  async getAIRoutingPreferences(): Promise<AIRoutingPreference[]> {
    return this.request<AIRoutingPreference[]>('/api/v1/ai/routing/preferences');
  }

  async updateAIRoutingPreference(preference: {
    category: TaskCategory;
    preferred_provider: string;
    preferred_model: string;
    fallback_provider?: string | null;
    fallback_model?: string | null;
    is_local_only?: boolean;
  }): Promise<any> {
    return this.request('/api/v1/ai/routing/preferences', {
      method: 'PATCH',
      body: JSON.stringify(preference),
    });
  }

  streamAIChat(
    payload: {
      prompt: string;
      system_prompt?: string | null;
      task_category?: TaskCategory;
      routing_strategy?: string;
      provider_preference?: string | null;
      model_preference?: string | null;
      temperature?: number;
      max_tokens?: number;
      is_local_only?: boolean;
    },
    callbacks: {
      onStart?: (data: any) => void;
      onDelta: (delta: string) => void;
      onComplete: (data: any) => void;
      onError: (err: string) => void;
    }
  ): () => void {
    const controller = new AbortController();
    const token = 'dev-local-autonom-key';

    (async () => {
      try {
        const response = await fetch(`${this.baseUrl}/api/v1/ai/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        if (!response.ok) {
          const errText = await response.text();
          callbacks.onError(`HTTP ${response.status}: ${errText}`);
          return;
        }

        const reader = response.body?.getReader();
        if (!reader) {
          callbacks.onError('ReadableStream not supported by browser.');
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          let currentEvent = 'message';
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim();
              try {
                const data = JSON.parse(dataStr);
                if (currentEvent === 'start') {
                  callbacks.onStart?.(data);
                } else if (currentEvent === 'delta') {
                  callbacks.onDelta(data.delta || '');
                } else if (currentEvent === 'complete') {
                  callbacks.onComplete(data);
                } else if (currentEvent === 'error') {
                  callbacks.onError(data.error || 'Stream error');
                } else if (currentEvent === 'cancelled') {
                  callbacks.onError('Generation cancelled.');
                }
              } catch {
                // Ignore parse errors on partial chunks
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          callbacks.onError(err.message || 'Stream connection error');
        }
      }
    })();

    return () => {
      controller.abort();
    };
  }
}

export const apiClient = new ApiClient();
