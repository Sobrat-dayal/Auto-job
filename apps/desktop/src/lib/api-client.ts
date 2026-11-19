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
  AgentDefinition,
  AgentManifest,
  AgentStatusResponse,
  AgentConfigurationUpdate,
  AgentExecutionHistoryItem,
  CapabilityDefinition,
  DAGVisualizationData,
  OrchestrationStats,
  WorkflowCreateRequest,
  WorkflowReplanRequest,
  WorkflowResponse,
  WorkflowStatus,
  WorkflowSummary,
  ApprovalMode,
  ApprovalRequest,
  AuthorizationDecision,
  AuthorizationGrant,
  AuthorizationPolicy,
  EmergencyStopState,
  GrantType,
  PermissionCategory,
  RiskLevel,
  SecurityAuditEntry,
  MemoryRecord,
  MemorySearchResponse,
  MemoryStatsResponse,
  MemoryConflict,
  ProceduralMemory,
  SearchMode,
  MemoryType,
  MemoryScope,
  BrowserRuntimeStatus,
  BrowserSessionSummary,
  BrowserSessionResponse,
  BrowserSessionCreateRequest,
  BrowserNavigateRequest,
  BrowserNavigateResponse,
  DOMInspectionRequest,
  DOMInspectionResponse,
  BrowserActionRequest,
  BrowserActionResponse,
  BrowserBatchActionsRequest,
  BrowserBatchActionsResponse,
  BrowserScreenshotRequest,
  BrowserScreenshotResponse,
  BrowserTabInfo,
  BrowserTabCreateRequest,
  BrowserProfileResponse,
  BrowserProfileCreateRequest,
  BrowserDownloadResponse,
  BrowserTaskResponse,
  BrowserTaskCreateRequest,
  DesktopSessionInfo,
  DesktopApplicationInfo,
  WindowInfo,
  WindowManageAction,
  InspectionOptions,
  UITreeSnapshot,
  ElementQuery,
  UIElementInfo,
  DesktopActionRequest,
  DesktopActionResult,
  DesktopTaskRequest,
  DesktopTaskResponse,
  DesktopDiagnosticsInfo,
  DisplayInfo,
  OCRResult,
  OCRLine,
  VisualElementDetection,
  VisualGroundingResult,
  VisualActionRequest,
  VisualActionResult,
  VisualDiagnosticsInfo,
  CaptureSessionCreateRequest,
  CaptureSessionResponse,
  VisualTaskRequest,
  VisualTaskResponse,
  InteractionMethod,
  InteractionTarget,
  CapabilityProbe,
  ObservationRequest,
  InteractionObservation,
  InteractionAction,
  InteractionResult,
  RoutingDecisionRecord,
  HybridTaskRequest,
  HybridTaskResponse,
  HybridDiagnosticsInfo,
  RecordingSession,
  StartRecordingRequest,
  RecordedAction,
  ReusableProcedure,
  CompileProcedureRequest,
  PreflightReport,
  ProcedureExecution,
  ExecutionCheckpoint,
  RecoveryPlan,
  ReliabilityDiagnosticsInfo,
  ReplayMode,
  ApplicantProfile,
  EducationRecord,
  EmploymentRecord,
  SkillItem,
  ProjectRecord,
  CertificationRecord,
  EvidenceMetadata,
  ApplicantClaim,
  ProfileConflict,
  ImportJob,
  DataQualityReport,
  ProfileSnapshot,
  ProfileVersionRecord,
  GitHubConnection,
  GitHubDiagnostics,
  GitHubStatusSummary,
  RepositoryMetadata,
  TechnologyFinding,
  RepositoryArchitecture,
  CommitEvidence,
  PullRequestEvidence,
  ContributionFinding,
  CandidateSkill,
  CandidateProject,
  SyncJobRecord,
  SourceTreeEntry,
  FileContentSnippet,
  ConnectGitHubRequest,
  ManualRepoRequest,
  SelectRepoRequest,
  ConfirmCandidateRequest,
  ResumeDocument,
  ResumeCreateRequest,
  ResumeUpdateRequest,
  ResumeVersionRecord,
  JobDescriptionSnapshot,
  JobDescriptionParseRequest,
  RequirementEvidenceMapping,
  ResumeTailorRequest,
  ATSReadabilityReport,
  ResumeTemplateDefinition,
  ExportArtifact,
  ResumeExportRequest,
  PortfolioDocument,
  PortfolioCreateRequest,
  PortfolioUpdateRequest,
  ResumeOverviewStats,
  WritingOverviewStats,
  CoverLetterDocument,
  CoverLetterTemplateDefinition,
  CoverLetterVersionRecord,
  ApplicationQuestionRecord,
  ApplicationAnswer,
  ApplicationQuestionSet,
  AnswerLibraryEntry,
  MissingInformationItem,
  SensitiveDecisionItem,
  ConflictItem,
  ApplicationWritingPackage,
  CoverLetterCreateRequest,
  CoverLetterUpdateRequest,
  CoverLetterGenerateRequest,
  CoverLetterExportRequest,
  ParagraphRewriteRequest,
  QuestionParseRequest,
  QuestionSetCreateRequest,
  AnswerUpdateRequest,
  AnswerLibraryCreateRequest,
  AnswerLibraryUpdateRequest,
  AnswerReusePreviewRequest,
  UserAttestationRequest,
  WritingPackageCreateRequest,
  CareerStrategy,
  CareerPreferenceProfile,
  JobOpportunityContext,
  RecruitmentDecision,
  RecruitmentBudget,
  ReviewQueueItem,
  StandingGrantRecord,
  PolicyVersionSnapshot,
  CareerStrategyCreateRequest,
  CareerStrategyUpdateRequest,
  PolicySimulationRequest,
  PolicySimulationResponse,
  PolicyConflictReport,
  BudgetReservationRequest,
  BudgetReservationResponse,
  BudgetConfirmationRequest,
  BudgetReleaseRequest,
  StandingGrantCreateRequest,
  AutonomyStatusResponse,
  ReviewQueueResolutionRequest,
  PolicyDiagnosticsResponse,
  ConnectorManifest,
  JobSourceConfig,
  JobSourceHealth,
  EmployerCareerSource,
  JobSourceObservation,
  JobSourceSnapshot,
  DiscoveryTaskRecord,
  DiscoverySettingsConfig,
  DiscoveryOverviewStats,
  JobSourceCreateRequest,
  JobSourceUpdateRequest,
  DiscoveryTaskCreateRequest,
  UrlImportRequest,
  ManualImportRequest,
  EmployerCareerPageCreateRequest,
  SourceValidationResult,
  PostingAvailability,
  PrefilterOutcome,
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

  // ==========================================
  // Multi-Agent Orchestration Methods (Stage 12)
  // ==========================================

  async createWorkflow(request: WorkflowCreateRequest): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>('/api/v1/orchestration/workflows', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async listWorkflows(status?: WorkflowStatus, limit = 50, offset = 0): Promise<WorkflowSummary[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    return this.request<WorkflowSummary[]>(`/api/v1/orchestration/workflows?${params.toString()}`);
  }

  async getWorkflow(workflowId: string): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(`/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}`);
  }

  async startWorkflow(workflowId: string, background = true): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/start?background=${background}`,
      { method: 'POST' }
    );
  }

  async pauseWorkflow(workflowId: string): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/pause`,
      { method: 'POST' }
    );
  }

  async resumeWorkflow(workflowId: string): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/resume`,
      { method: 'POST' }
    );
  }

  async cancelWorkflow(workflowId: string): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/cancel`,
      { method: 'POST' }
    );
  }

  async replanWorkflow(workflowId: string, request: WorkflowReplanRequest): Promise<WorkflowResponse> {
    return this.request<WorkflowResponse>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/replan`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
  }

  async getWorkflowDag(workflowId: string): Promise<DAGVisualizationData> {
    return this.request<DAGVisualizationData>(
      `/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/dag`
    );
  }

  async getWorkflowExecutions(workflowId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/executions`);
  }

  async getWorkflowMessages(workflowId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/messages`);
  }

  async getWorkflowVerifications(workflowId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/verifications`);
  }

  async getWorkflowRecoveries(workflowId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/orchestration/workflows/${encodeURIComponent(workflowId)}/recoveries`);
  }

  async listAgents(onlyAvailable = false): Promise<AgentDefinition[]> {
    return this.request<AgentDefinition[]>(
      `/api/v1/orchestration/agents?only_available=${onlyAvailable}`
    );
  }

  async listCapabilities(): Promise<CapabilityDefinition[]> {
    return this.request<CapabilityDefinition[]>('/api/v1/orchestration/capabilities');
  }

  async getOrchestrationStats(): Promise<OrchestrationStats> {
    return this.request<OrchestrationStats>('/api/v1/orchestration/stats');
  }

  // ==========================================
  // Specialist Agent Methods (Stage 13)
  // ==========================================

  async listAgentManifests(params?: {
    category?: string;
    status?: string;
    onlyAvailable?: boolean;
  }): Promise<AgentManifest[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append('category', params.category);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.onlyAvailable) searchParams.append('only_available', 'true');
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<AgentManifest[]>(`/api/v1/agents${query}`);
  }

  async getAgentManifest(agentId: string): Promise<AgentManifest> {
    return this.request<AgentManifest>(`/api/v1/agents/${encodeURIComponent(agentId)}`);
  }

  async getAgentCapabilities(agentId: string): Promise<CapabilityDefinition[]> {
    return this.request<CapabilityDefinition[]>(`/api/v1/agents/${encodeURIComponent(agentId)}/capabilities`);
  }

  async getAgentStatus(agentId: string): Promise<AgentStatusResponse> {
    return this.request<AgentStatusResponse>(`/api/v1/agents/${encodeURIComponent(agentId)}/status`);
  }

  async getAgentExecutions(agentId: string, limit = 50): Promise<AgentExecutionHistoryItem[]> {
    return this.request<AgentExecutionHistoryItem[]>(
      `/api/v1/agents/${encodeURIComponent(agentId)}/executions?limit=${limit}`
    );
  }

  async getAgentConfiguration(agentId: string): Promise<any> {
    return this.request<any>(`/api/v1/agents/${encodeURIComponent(agentId)}/configuration`);
  }

  async updateAgentConfiguration(
    agentId: string,
    patch: AgentConfigurationUpdate
  ): Promise<AgentManifest> {
    return this.request<AgentManifest>(`/api/v1/agents/${encodeURIComponent(agentId)}/configuration`, {
      method: 'PATCH',
      body: JSON.stringify(patch),
    });
  }

  async testAgent(agentId: string): Promise<{ passed: boolean; details: string; duration_ms: number; tested_at: string }> {
    return this.request<{ passed: boolean; details: string; duration_ms: number; tested_at: string }>(
      `/api/v1/agents/${encodeURIComponent(agentId)}/test`,
      { method: 'POST' }
    );
  }

  async listAllCapabilities(): Promise<CapabilityDefinition[]> {
    return this.request<CapabilityDefinition[]>('/api/v1/agents/capabilities');
  }

  // --- Stage 14: Security, Authorization, Grants & Emergency Stop ---

  async getPermissionsTaxonomy(): Promise<{
    categories: PermissionCategory[];
    risk_levels: RiskLevel[];
    action_effects: string[];
    approval_modes: ApprovalMode[];
    grant_types: GrantType[];
  }> {
    return this.request('/api/v1/security/permissions');
  }

  async getEmergencyStopStatus(): Promise<EmergencyStopState> {
    return this.request<EmergencyStopState>('/api/v1/security/emergency-stop');
  }

  async activateEmergencyStop(reason?: string): Promise<EmergencyStopState> {
    return this.request<EmergencyStopState>('/api/v1/security/emergency-stop', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async clearEmergencyStop(): Promise<EmergencyStopState> {
    return this.request<EmergencyStopState>('/api/v1/security/emergency-stop/clear', {
      method: 'POST',
    });
  }

  async pauseAutomation(reason?: string): Promise<EmergencyStopState> {
    return this.request<EmergencyStopState>('/api/v1/security/automation/pause', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async resumeAutomation(): Promise<EmergencyStopState> {
    return this.request<EmergencyStopState>('/api/v1/security/automation/resume', {
      method: 'POST',
    });
  }

  async listPolicies(enabledOnly = false): Promise<AuthorizationPolicy[]> {
    return this.request<AuthorizationPolicy[]>(
      `/api/v1/security/policies${enabledOnly ? '?enabled_only=true' : ''}`
    );
  }

  async getPolicy(id: string): Promise<AuthorizationPolicy> {
    return this.request<AuthorizationPolicy>(`/api/v1/security/policies/${encodeURIComponent(id)}`);
  }

  async createPolicy(policy: Partial<AuthorizationPolicy>): Promise<AuthorizationPolicy> {
    return this.request<AuthorizationPolicy>('/api/v1/security/policies', {
      method: 'POST',
      body: JSON.stringify(policy),
    });
  }

  async updatePolicy(
    id: string,
    patch: Partial<AuthorizationPolicy> & { expected_version?: number; change_reason?: string }
  ): Promise<AuthorizationPolicy> {
    return this.request<AuthorizationPolicy>(`/api/v1/security/policies/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(patch),
    });
  }

  async revokePolicy(id: string): Promise<AuthorizationPolicy> {
    return this.request<AuthorizationPolicy>(`/api/v1/security/policies/${encodeURIComponent(id)}/revoke`, {
      method: 'POST',
    });
  }

  async evaluatePolicyPreview(request: any): Promise<AuthorizationDecision> {
    return this.request<AuthorizationDecision>('/api/v1/security/policies/evaluate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async listGrants(params?: {
    activeOnly?: boolean;
    subjectId?: string;
    workflowId?: string;
  }): Promise<AuthorizationGrant[]> {
    const searchParams = new URLSearchParams();
    if (params?.activeOnly) searchParams.append('active_only', 'true');
    if (params?.subjectId) searchParams.append('subject_id', params.subjectId);
    if (params?.workflowId) searchParams.append('workflow_id', params.workflowId);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<AuthorizationGrant[]>(`/api/v1/security/grants${query}`);
  }

  async createGrant(grant: any): Promise<AuthorizationGrant> {
    return this.request<AuthorizationGrant>('/api/v1/security/grants', {
      method: 'POST',
      body: JSON.stringify(grant),
    });
  }

  async revokeGrant(id: string, reason?: string): Promise<AuthorizationGrant> {
    const query = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return this.request<AuthorizationGrant>(`/api/v1/security/grants/${encodeURIComponent(id)}/revoke${query}`, {
      method: 'POST',
    });
  }

  async listApprovals(params?: {
    status?: string;
    workflowId?: string;
    agentId?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApprovalRequest[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append('status', params.status);
    if (params?.workflowId) searchParams.append('workflow_id', params.workflowId);
    if (params?.agentId) searchParams.append('agent_id', params.agentId);
    if (params?.limit) searchParams.append('limit', String(params.limit));
    if (params?.offset) searchParams.append('offset', String(params.offset));
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<ApprovalRequest[]>(`/api/v1/security/approvals${query}`);
  }

  async getApproval(id: string): Promise<ApprovalRequest> {
    return this.request<ApprovalRequest>(`/api/v1/security/approvals/${encodeURIComponent(id)}`);
  }

  async approveRequest(
    id: string,
    options?: {
      reason?: string;
      approval_mode?: ApprovalMode;
      valid_until_seconds?: number;
    }
  ): Promise<ApprovalRequest> {
    return this.request<ApprovalRequest>(`/api/v1/security/approvals/${encodeURIComponent(id)}/approve`, {
      method: 'POST',
      body: JSON.stringify({
        decision: 'approve',
        reason: options?.reason,
        approval_mode: options?.approval_mode || 'one_time',
        valid_until_seconds: options?.valid_until_seconds,
      }),
    });
  }

  async denyRequest(id: string, options?: { reason?: string }): Promise<ApprovalRequest> {
    return this.request<ApprovalRequest>(`/api/v1/security/approvals/${encodeURIComponent(id)}/deny`, {
      method: 'POST',
      body: JSON.stringify({
        decision: 'deny',
        reason: options?.reason,
      }),
    });
  }

  async listSecurityAuditLogs(params?: {
    limit?: number;
    offset?: number;
    correlationId?: string;
    outcome?: string;
    agentId?: string;
  }): Promise<SecurityAuditEntry[]> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.append('limit', String(params.limit));
    if (params?.offset) searchParams.append('offset', String(params.offset));
    if (params?.correlationId) searchParams.append('correlation_id', params.correlationId);
    if (params?.outcome) searchParams.append('outcome', params.outcome);
    if (params?.agentId) searchParams.append('agent_id', params.agentId);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<SecurityAuditEntry[]>(`/api/v1/security/audit${query}`);
  }

  // -------------------------------------------------------------------------
  // Stage 15: Agent Memory & Hybrid Retrieval Engine
  // -------------------------------------------------------------------------

  async getMemoryStatus(): Promise<MemoryStatsResponse> {
    return this.request<MemoryStatsResponse>('/api/v1/memory/status');
  }

  async listMemories(params?: {
    owner_scope?: MemoryScope;
    scope_id?: string;
    memory_type?: MemoryType;
    limit?: number;
    offset?: number;
  }): Promise<MemoryRecord[]> {
    const searchParams = new URLSearchParams();
    if (params?.owner_scope) searchParams.append('owner_scope', params.owner_scope);
    if (params?.scope_id) searchParams.append('scope_id', params.scope_id);
    if (params?.memory_type) searchParams.append('memory_type', params.memory_type);
    if (params?.limit) searchParams.append('limit', String(params.limit));
    if (params?.offset) searchParams.append('offset', String(params.offset));
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<MemoryRecord[]>(`/api/v1/memory${query}`);
  }

  async getMemory(id: string): Promise<MemoryRecord> {
    return this.request<MemoryRecord>(`/api/v1/memory/${encodeURIComponent(id)}`);
  }

  async createMemory(payload: {
    memory_type?: MemoryType;
    title: string;
    content: string;
    summary?: string;
    owner_scope?: MemoryScope;
    scope_id: string;
    source_type?: string;
    source_ref?: string;
    verification_status?: string;
    confidence_category?: string;
    sensitivity_category?: string;
  }): Promise<MemoryRecord> {
    return this.request<MemoryRecord>('/api/v1/memory', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateMemory(
    id: string,
    payload: {
      title?: string;
      content?: string;
      summary?: string;
      verification_status?: string;
      confidence_category?: string;
      sensitivity_category?: string;
      superseded_by?: string;
    }
  ): Promise<MemoryRecord> {
    return this.request<MemoryRecord>(`/api/v1/memory/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async deleteMemory(id: string): Promise<void> {
    await this.request<void>(`/api/v1/memory/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async searchMemory(payload: {
    query: string;
    search_mode?: SearchMode;
    memory_types?: MemoryType[];
    owner_scope?: MemoryScope;
    scope_id?: string;
    limit?: number;
    min_score?: number;
    exclude_superseded?: boolean;
  }): Promise<MemorySearchResponse> {
    const mode = payload.search_mode || 'hybrid';
    const path =
      mode === 'semantic'
        ? '/api/v1/memory/search/semantic'
        : mode === 'keyword'
          ? '/api/v1/memory/search/keyword'
          : '/api/v1/memory/search';
    return this.request<MemorySearchResponse>(path, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async listMemoryConflicts(status: string = 'unresolved'): Promise<MemoryConflict[]> {
    return this.request<MemoryConflict[]>(`/api/v1/memory/conflicts?status=${encodeURIComponent(status)}`);
  }

  async resolveMemoryConflict(
    conflictId: string,
    payload: { resolution_action: string; superseding_memory_id?: string }
  ): Promise<MemoryConflict> {
    return this.request<MemoryConflict>(
      `/api/v1/memory/conflicts/${encodeURIComponent(conflictId)}/resolve`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  }

  async listProceduralMemories(capabilityId?: string): Promise<ProceduralMemory[]> {
    const query = capabilityId ? `?capability_id=${encodeURIComponent(capabilityId)}` : '';
    return this.request<ProceduralMemory[]>(`/api/v1/memory/procedures${query}`);
  }

  async rebuildMemoryIndex(): Promise<{ status: string; vector_store_size: number }> {
    return this.request<{ status: string; vector_store_size: number }>('/api/v1/memory/index/rebuild', {
      method: 'POST',
    });
  }

  async consolidateMemories(scopeId: string): Promise<{ scope_id: string; consolidated_records: number }> {
    return this.request<{ scope_id: string; consolidated_records: number }>(
      `/api/v1/memory/consolidate?scope_id=${encodeURIComponent(scopeId)}`,
      {
        method: 'POST',
      }
    );
  }

  // -------------------------------------------------------------------------
  // Stage 16 Browser Automation Methods
  // -------------------------------------------------------------------------

  async getBrowserRuntimeStatus(): Promise<BrowserRuntimeStatus> {
    return this.request<BrowserRuntimeStatus>('/api/v1/browser/status');
  }

  async listBrowserSessions(): Promise<BrowserSessionSummary[]> {
    return this.request<BrowserSessionSummary[]>('/api/v1/browser/sessions');
  }

  async createBrowserSession(req: BrowserSessionCreateRequest = {}): Promise<BrowserSessionResponse> {
    return this.request<BrowserSessionResponse>('/api/v1/browser/sessions', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getBrowserSession(sessionId: string): Promise<BrowserSessionResponse> {
    return this.request<BrowserSessionResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}`);
  }

  async closeBrowserSession(sessionId: string): Promise<void> {
    await this.request<void>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  }

  async navigateBrowser(sessionId: string, req: BrowserNavigateRequest): Promise<BrowserNavigateResponse> {
    return this.request<BrowserNavigateResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/navigate`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getBrowserActivePage(sessionId: string): Promise<{ session_id: string; tab_id: string; title: string; url: string; status: string }> {
    return this.request(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/page`);
  }

  async inspectBrowserDOM(sessionId: string, req?: DOMInspectionRequest): Promise<DOMInspectionResponse> {
    return this.request<DOMInspectionResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/inspect`, {
      method: 'POST',
      body: JSON.stringify(req || {}),
    });
  }

  async executeBrowserAction(sessionId: string, req: BrowserActionRequest): Promise<BrowserActionResponse> {
    return this.request<BrowserActionResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/actions`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async executeBatchBrowserActions(sessionId: string, req: BrowserBatchActionsRequest): Promise<BrowserBatchActionsResponse> {
    return this.request<BrowserBatchActionsResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/batch-actions`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async captureBrowserScreenshot(sessionId: string, req?: BrowserScreenshotRequest): Promise<BrowserScreenshotResponse> {
    return this.request<BrowserScreenshotResponse>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/screenshot`, {
      method: 'POST',
      body: JSON.stringify(req || {}),
    });
  }

  async listBrowserTabs(sessionId: string): Promise<BrowserTabInfo[]> {
    return this.request<BrowserTabInfo[]>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/tabs`);
  }

  async createBrowserTab(sessionId: string, req?: BrowserTabCreateRequest): Promise<BrowserTabInfo> {
    return this.request<BrowserTabInfo>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/tabs`, {
      method: 'POST',
      body: JSON.stringify(req || {}),
    });
  }

  async switchBrowserTab(sessionId: string, tabId: string): Promise<{ session_id: string; active_tab_id: string; success: boolean }> {
    return this.request(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/tabs/switch`, {
      method: 'PUT',
      body: JSON.stringify({ tab_id: tabId }),
    });
  }

  async closeBrowserTab(sessionId: string, tabId: string): Promise<void> {
    await this.request<void>(`/api/v1/browser/sessions/${encodeURIComponent(sessionId)}/tabs/${encodeURIComponent(tabId)}`, {
      method: 'DELETE',
    });
  }

  async listBrowserProfiles(): Promise<BrowserProfileResponse[]> {
    return this.request<BrowserProfileResponse[]>('/api/v1/browser/profiles');
  }

  async createBrowserProfile(req: BrowserProfileCreateRequest): Promise<BrowserProfileResponse> {
    return this.request<BrowserProfileResponse>('/api/v1/browser/profiles', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listBrowserDownloads(): Promise<BrowserDownloadResponse[]> {
    return this.request<BrowserDownloadResponse[]>('/api/v1/browser/downloads');
  }

  async listBrowserTasks(): Promise<BrowserTaskResponse[]> {
    return this.request<BrowserTaskResponse[]>('/api/v1/browser/tasks');
  }

  async createBrowserTask(req: BrowserTaskCreateRequest): Promise<BrowserTaskResponse> {
    return this.request<BrowserTaskResponse>('/api/v1/browser/tasks', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  // -------------------------------------------------------------------------
  // Stage 17: Native Windows Structural Automation Methods
  // -------------------------------------------------------------------------

  async getDesktopStatus(): Promise<DesktopDiagnosticsInfo> {
    return this.request<DesktopDiagnosticsInfo>('/api/v1/desktop/status');
  }

  async getDesktopSession(): Promise<DesktopSessionInfo> {
    return this.request<DesktopSessionInfo>('/api/v1/desktop/session');
  }

  async listDesktopApplications(): Promise<DesktopApplicationInfo[]> {
    return this.request<DesktopApplicationInfo[]>('/api/v1/desktop/applications');
  }

  async launchDesktopApplication(executableName: string, args: string[] = []): Promise<WindowInfo | null> {
    return this.request<WindowInfo | null>('/api/v1/desktop/applications/launch', {
      method: 'POST',
      body: JSON.stringify({ executable_name: executableName, arguments: args }),
    });
  }

  async listDesktopWindows(includeInvisible = false): Promise<WindowInfo[]> {
    return this.request<WindowInfo[]>(`/api/v1/desktop/windows?include_invisible=${includeInvisible}`);
  }

  async getDesktopWindow(windowRef: string): Promise<WindowInfo> {
    return this.request<WindowInfo>(`/api/v1/desktop/windows/${encodeURIComponent(windowRef)}`);
  }

  async manageDesktopWindow(windowRef: string, action: WindowManageAction): Promise<{ window_ref: string; action: string; success: boolean }> {
    return this.request(`/api/v1/desktop/windows/${encodeURIComponent(windowRef)}/manage`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  }

  async inspectDesktopTree(windowRef: string, options?: InspectionOptions): Promise<UITreeSnapshot> {
    return this.request<UITreeSnapshot>(`/api/v1/desktop/windows/${encodeURIComponent(windowRef)}/inspect`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    });
  }

  async searchDesktopElements(windowRef: string, query: ElementQuery): Promise<UIElementInfo[]> {
    return this.request<UIElementInfo[]>('/api/v1/desktop/elements/search', {
      method: 'POST',
      body: JSON.stringify({ window_ref: windowRef, query }),
    });
  }

  async executeDesktopAction(req: DesktopActionRequest): Promise<DesktopActionResult> {
    return this.request<DesktopActionResult>('/api/v1/desktop/actions', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listDesktopActions(limit = 50): Promise<DesktopActionResult[]> {
    return this.request<DesktopActionResult[]>(`/api/v1/desktop/actions?limit=${limit}`);
  }

  async getDesktopAction(actionId: string): Promise<DesktopActionResult> {
    return this.request<DesktopActionResult>(`/api/v1/desktop/actions/${encodeURIComponent(actionId)}`);
  }

  async listDesktopTasks(): Promise<DesktopTaskResponse[]> {
    return this.request<DesktopTaskResponse[]>('/api/v1/desktop/tasks');
  }

  async submitDesktopTask(req: DesktopTaskRequest): Promise<DesktopTaskResponse> {
    return this.request<DesktopTaskResponse>('/api/v1/desktop/tasks', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getDesktopTask(taskId: string): Promise<DesktopTaskResponse> {
    return this.request<DesktopTaskResponse>(`/api/v1/desktop/tasks/${encodeURIComponent(taskId)}`);
  }

  async cancelDesktopTask(taskId: string): Promise<{ task_id: string; status: string }> {
    return this.request(`/api/v1/desktop/tasks/${encodeURIComponent(taskId)}/cancel`, {
      method: 'POST',
    });
  }

  async getDesktopDiagnostics(): Promise<DesktopDiagnosticsInfo> {
    return this.request<DesktopDiagnosticsInfo>('/api/v1/desktop/diagnostics');
  }

  async getDesktopCapabilities(): Promise<Array<{ name: string; description: string }>> {
    return this.request<Array<{ name: string; description: string }>>('/api/v1/desktop/capabilities');
  }

  // =========================================================================
  // Stage 18: Visual Computer Automation
  // =========================================================================

  async getVisualDiagnostics(): Promise<VisualDiagnosticsInfo> {
    return this.request<VisualDiagnosticsInfo>('/api/v1/visual/diagnostics');
  }

  async listVisualMonitors(): Promise<DisplayInfo[]> {
    return this.request<DisplayInfo[]>('/api/v1/visual/monitors');
  }

  async createVisualSession(req: CaptureSessionCreateRequest): Promise<CaptureSessionResponse> {
    return this.request<CaptureSessionResponse>('/api/v1/visual/sessions', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listVisualSessions(): Promise<CaptureSessionResponse[]> {
    return this.request<CaptureSessionResponse[]>('/api/v1/visual/sessions');
  }

  async getVisualSession(sessionId: string): Promise<CaptureSessionResponse> {
    return this.request<CaptureSessionResponse>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}`);
  }

  async closeVisualSession(sessionId: string): Promise<{ session_id: string; closed: boolean }> {
    return this.request<{ session_id: string; closed: boolean }>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  }

  async captureVisualFrame(sessionId: string): Promise<{
    frame_id: string;
    session_id: string;
    metadata: any;
    thumbnail_b64: string;
  }> {
    return this.request(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/frame`, {
      method: 'POST',
    });
  }

  async runVisualOCR(sessionId: string): Promise<OCRResult> {
    return this.request<OCRResult>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/ocr`, {
      method: 'POST',
    });
  }

  async findVisualText(sessionId: string, query: string): Promise<OCRLine[]> {
    return this.request<OCRLine[]>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/find-text`, {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  async detectVisualElements(sessionId: string): Promise<VisualElementDetection[]> {
    return this.request<VisualElementDetection[]>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/detect-elements`, {
      method: 'POST',
    });
  }

  async groundVisualQuery(sessionId: string, query: string): Promise<VisualGroundingResult> {
    return this.request<VisualGroundingResult>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/ground`, {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  async executeVisualAction(sessionId: string, action: VisualActionRequest): Promise<VisualActionResult> {
    return this.request<VisualActionResult>(`/api/v1/visual/sessions/${encodeURIComponent(sessionId)}/actions`, {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  async quickVisualClick(
    sessionId: string,
    x: number,
    y: number,
    button: string = 'left',
    clicks: number = 1,
  ): Promise<VisualActionResult> {
    return this.request<VisualActionResult>('/api/v1/visual/quick-click', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, x, y, button, clicks }),
    });
  }

  async quickVisualType(
    sessionId: string,
    text: string,
    targetElement?: string,
  ): Promise<VisualActionResult> {
    return this.request<VisualActionResult>('/api/v1/visual/quick-type', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, text, target_element: targetElement }),
    });
  }

  async submitVisualTask(req: VisualTaskRequest): Promise<VisualTaskResponse> {
    return this.request<VisualTaskResponse>('/api/v1/visual/tasks', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listVisualTasks(): Promise<VisualTaskResponse[]> {
    return this.request<VisualTaskResponse[]>('/api/v1/visual/tasks');
  }

  async getVisualTask(taskId: string): Promise<VisualTaskResponse> {
    return this.request<VisualTaskResponse>(`/api/v1/visual/tasks/${encodeURIComponent(taskId)}`);
  }

  async listVisualRecoveryEvents(): Promise<any[]> {
    return this.request<any[]>('/api/v1/visual/recovery-events');
  }

  // =========================================================================
  // Stage 19: Hybrid Computer Interaction & Multi-Method Automation
  // =========================================================================

  async getHybridStatus(): Promise<any> {
    return this.request<any>('/api/v1/hybrid/status');
  }

  async listHybridMethods(): Promise<InteractionMethod[]> {
    return this.request<InteractionMethod[]>('/api/v1/hybrid/methods');
  }

  async getHybridCapabilities(): Promise<any[]> {
    return this.request<any[]>('/api/v1/hybrid/capabilities');
  }

  async resolveHybridTarget(req: {
    target_hint?: string;
    session_id?: string;
    dom_selector?: string;
    window_title?: string;
    window_handle?: number;
    coordinates?: Record<string, any>;
    process_name?: string;
  }): Promise<InteractionTarget> {
    return this.request<InteractionTarget>('/api/v1/hybrid/targets/resolve', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async probeHybridMethods(target: InteractionTarget): Promise<Record<string, CapabilityProbe>> {
    return this.request<Record<string, CapabilityProbe>>('/api/v1/hybrid/methods/probe', {
      method: 'POST',
      body: JSON.stringify(target),
    });
  }

  async previewHybridRoute(req: {
    target: InteractionTarget;
    action_type?: string;
    preferred_method?: InteractionMethod;
  }): Promise<RoutingDecisionRecord> {
    return this.request<RoutingDecisionRecord>('/api/v1/hybrid/route/preview', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async observeHybrid(req: ObservationRequest): Promise<InteractionObservation> {
    return this.request<InteractionObservation>('/api/v1/hybrid/observe', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async executeHybridAction(action: InteractionAction): Promise<InteractionResult> {
    return this.request<InteractionResult>('/api/v1/hybrid/actions', {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  async getHybridAction(actionId: string): Promise<InteractionResult> {
    return this.request<InteractionResult>(`/api/v1/hybrid/actions/${encodeURIComponent(actionId)}`);
  }

  async listHybridTasks(limit: number = 50): Promise<HybridTaskResponse[]> {
    return this.request<HybridTaskResponse[]>(`/api/v1/hybrid/tasks?limit=${limit}`);
  }

  async submitHybridTask(req: HybridTaskRequest): Promise<HybridTaskResponse> {
    return this.request<HybridTaskResponse>('/api/v1/hybrid/tasks', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getHybridTask(taskId: string): Promise<HybridTaskResponse> {
    return this.request<HybridTaskResponse>(`/api/v1/hybrid/tasks/${encodeURIComponent(taskId)}`);
  }

  async cancelHybridTask(taskId: string): Promise<{ task_id: string; status: string }> {
    return this.request<{ task_id: string; status: string }>(
      `/api/v1/hybrid/tasks/${encodeURIComponent(taskId)}/cancel`,
      { method: 'POST' }
    );
  }

  async getHybridTaskHistory(taskId: string): Promise<any> {
    return this.request<any>(`/api/v1/hybrid/tasks/${encodeURIComponent(taskId)}/history`);
  }

  async getHybridTaskRouting(taskId: string): Promise<RoutingDecisionRecord> {
    return this.request<RoutingDecisionRecord>(`/api/v1/hybrid/tasks/${encodeURIComponent(taskId)}/routing`);
  }

  async getHybridDiagnostics(): Promise<HybridDiagnosticsInfo> {
    return this.request<HybridDiagnosticsInfo>('/api/v1/hybrid/diagnostics');
  }

  async activateHybridKillswitch(reason?: string): Promise<{ status: string; reason: string }> {
    return this.request<{ status: string; reason: string }>('/api/v1/hybrid/killswitch/activate', {
      method: 'POST',
      body: JSON.stringify({ reason: reason || 'Operator hybrid killswitch activation' }),
    });
  }

  async deactivateHybridKillswitch(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/api/v1/hybrid/killswitch/deactivate', {
      method: 'POST',
    });
  }

  // -------------------------------------------------------------------------
  // Stage 20: Workflow Reliability & Computer Action Recording Methods
  // -------------------------------------------------------------------------

  async startRecording(req: StartRecordingRequest): Promise<RecordingSession> {
    return this.request<RecordingSession>('/api/v1/reliability/recordings', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listRecordings(limit: number = 50): Promise<RecordingSession[]> {
    return this.request<RecordingSession[]>(`/api/v1/reliability/recordings?limit=${limit}`);
  }

  async getRecording(sessionId: string): Promise<RecordingSession> {
    return this.request<RecordingSession>(`/api/v1/reliability/recordings/${encodeURIComponent(sessionId)}`);
  }

  async pauseRecording(sessionId: string): Promise<RecordingSession> {
    return this.request<RecordingSession>(`/api/v1/reliability/recordings/${encodeURIComponent(sessionId)}/pause`, {
      method: 'POST',
    });
  }

  async resumeRecording(sessionId: string): Promise<RecordingSession> {
    return this.request<RecordingSession>(`/api/v1/reliability/recordings/${encodeURIComponent(sessionId)}/resume`, {
      method: 'POST',
    });
  }

  async stopRecording(sessionId: string): Promise<RecordingSession> {
    return this.request<RecordingSession>(`/api/v1/reliability/recordings/${encodeURIComponent(sessionId)}/stop`, {
      method: 'POST',
    });
  }

  async recordAction(sessionId: string, action: Partial<RecordedAction>): Promise<RecordedAction> {
    return this.request<RecordedAction>(`/api/v1/reliability/recordings/${encodeURIComponent(sessionId)}/actions`, {
      method: 'POST',
      body: JSON.stringify(action),
    });
  }

  async compileProcedure(req: CompileProcedureRequest): Promise<ReusableProcedure> {
    return this.request<ReusableProcedure>('/api/v1/reliability/procedures/compile', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listProcedures(category?: string, includeDeprecated: boolean = false): Promise<ReusableProcedure[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (includeDeprecated) params.append('include_deprecated', 'true');
    const qs = params.toString() ? `?${params.toString()}` : '';
    return this.request<ReusableProcedure[]>(`/api/v1/reliability/procedures${qs}`);
  }

  async getProcedure(procedureId: string, version?: number): Promise<ReusableProcedure> {
    const qs = version !== undefined ? `?version=${version}` : '';
    return this.request<ReusableProcedure>(`/api/v1/reliability/procedures/${encodeURIComponent(procedureId)}${qs}`);
  }

  async updateProcedureDraft(procedureId: string, draft: Partial<ReusableProcedure>): Promise<ReusableProcedure> {
    return this.request<ReusableProcedure>(`/api/v1/reliability/procedures/${encodeURIComponent(procedureId)}`, {
      method: 'PUT',
      body: JSON.stringify(draft),
    });
  }

  async publishProcedureVersion(procedureId: string): Promise<ReusableProcedure> {
    return this.request<ReusableProcedure>(`/api/v1/reliability/procedures/${encodeURIComponent(procedureId)}/publish`, {
      method: 'POST',
    });
  }

  async branchProcedureDraft(procedureId: string): Promise<ReusableProcedure> {
    return this.request<ReusableProcedure>(`/api/v1/reliability/procedures/${encodeURIComponent(procedureId)}/branch`, {
      method: 'POST',
    });
  }

  async preflightProcedure(procedureId: string, args: Record<string, any> = {}, version?: number): Promise<PreflightReport> {
    return this.request<PreflightReport>(`/api/v1/reliability/procedures/${encodeURIComponent(procedureId)}/preflight`, {
      method: 'POST',
      body: JSON.stringify({ arguments: args, version }),
    });
  }

  async executeProcedure(
    procedureId: string,
    args: Record<string, any> = {},
    version?: number,
    mode: ReplayMode = 'automatic_authorized'
  ): Promise<ProcedureExecution> {
    return this.request<ProcedureExecution>('/api/v1/reliability/executions', {
      method: 'POST',
      body: JSON.stringify({ procedure_id: procedureId, version, arguments: args, mode }),
    });
  }

  async listExecutions(procedureId?: string, limit: number = 50): Promise<ProcedureExecution[]> {
    const params = new URLSearchParams();
    if (procedureId) params.append('procedure_id', procedureId);
    params.append('limit', String(limit));
    return this.request<ProcedureExecution[]>(`/api/v1/reliability/executions?${params.toString()}`);
  }

  async getExecution(executionId: string): Promise<ProcedureExecution> {
    return this.request<ProcedureExecution>(`/api/v1/reliability/executions/${encodeURIComponent(executionId)}`);
  }

  async listExecutionCheckpoints(executionId: string): Promise<ExecutionCheckpoint[]> {
    return this.request<ExecutionCheckpoint[]>(`/api/v1/reliability/executions/${encodeURIComponent(executionId)}/checkpoints`);
  }

  async getRecoveryPlan(executionId: string): Promise<RecoveryPlan> {
    return this.request<RecoveryPlan>(`/api/v1/reliability/executions/${encodeURIComponent(executionId)}/recovery-plan`);
  }

  async resumeExecution(executionId: string): Promise<ProcedureExecution> {
    return this.request<ProcedureExecution>(`/api/v1/reliability/executions/${encodeURIComponent(executionId)}/resume`, {
      method: 'POST',
    });
  }

  async getReliabilityDiagnostics(): Promise<ReliabilityDiagnosticsInfo> {
    return this.request<ReliabilityDiagnosticsInfo>('/api/v1/reliability/diagnostics');
  }

  // ================= Stage 21: Applicant Profile Intelligence =================

  async listApplicantProfiles(): Promise<ApplicantProfile[]> {
    return this.request<ApplicantProfile[]>('/api/v1/applicants');
  }

  async getApplicantProfile(profileId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}`);
  }

  async createApplicantProfile(displayLabel: string = 'Primary Career Profile', ownerId?: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>('/api/v1/applicants', {
      method: 'POST',
      body: JSON.stringify({ display_label: displayLabel, owner_id: ownerId }),
    });
  }

  async updateApplicantProfileMeta(profileId: string, displayLabel: string, expectedVersion?: number): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}`, {
      method: 'PATCH',
      body: JSON.stringify({ display_label: displayLabel, expected_version: expectedVersion }),
    });
  }

  async updateApplicantIdentity(profileId: string, payload: { contact?: any; location?: any; eligibility?: any; expected_version?: number }): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/identity`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async listApplicantEducation(profileId: string): Promise<EducationRecord[]> {
    return this.request<EducationRecord[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/education`);
  }

  async addApplicantEducation(profileId: string, record: Partial<EducationRecord>): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/education`, {
      method: 'POST',
      body: JSON.stringify(record),
    });
  }

  async deleteApplicantEducation(profileId: string, educationId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/education/${encodeURIComponent(educationId)}`, {
      method: 'DELETE',
    });
  }

  async listApplicantExperience(profileId: string): Promise<EmploymentRecord[]> {
    return this.request<EmploymentRecord[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/experience`);
  }

  async addApplicantExperience(profileId: string, record: Partial<EmploymentRecord>): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/experience`, {
      method: 'POST',
      body: JSON.stringify(record),
    });
  }

  async deleteApplicantExperience(profileId: string, experienceId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/experience/${encodeURIComponent(experienceId)}`, {
      method: 'DELETE',
    });
  }

  async listApplicantSkills(profileId: string): Promise<SkillItem[]> {
    return this.request<SkillItem[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/skills`);
  }

  async upsertApplicantSkill(profileId: string, skill: Partial<SkillItem>): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/skills`, {
      method: 'POST',
      body: JSON.stringify(skill),
    });
  }

  async deleteApplicantSkill(profileId: string, skillId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/skills/${encodeURIComponent(skillId)}`, {
      method: 'DELETE',
    });
  }

  async listApplicantProjects(profileId: string): Promise<ProjectRecord[]> {
    return this.request<ProjectRecord[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/projects`);
  }

  async addApplicantProject(profileId: string, project: Partial<ProjectRecord>): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/projects`, {
      method: 'POST',
      body: JSON.stringify(project),
    });
  }

  async deleteApplicantProject(profileId: string, projectId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/projects/${encodeURIComponent(projectId)}`, {
      method: 'DELETE',
    });
  }

  async listApplicantCertifications(profileId: string): Promise<CertificationRecord[]> {
    return this.request<CertificationRecord[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/certifications`);
  }

  async addApplicantCertification(profileId: string, cert: Partial<CertificationRecord>): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/certifications`, {
      method: 'POST',
      body: JSON.stringify(cert),
    });
  }

  async deleteApplicantCertification(profileId: string, certId: string): Promise<ApplicantProfile> {
    return this.request<ApplicantProfile>(`/api/v1/applicants/${encodeURIComponent(profileId)}/certifications/${encodeURIComponent(certId)}`, {
      method: 'DELETE',
    });
  }

  async listApplicantClaims(profileId: string, category?: string, status?: string): Promise<ApplicantClaim[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    const qs = params.toString();
    return this.request<ApplicantClaim[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/claims${qs ? `?${qs}` : ''}`);
  }

  async confirmApplicantClaim(profileId: string, claimId: string, notes?: string): Promise<ApplicantClaim> {
    return this.request<ApplicantClaim>(`/api/v1/applicants/${encodeURIComponent(profileId)}/claims/${encodeURIComponent(claimId)}/confirm`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async rejectApplicantClaim(profileId: string, claimId: string, reason?: string): Promise<ApplicantClaim> {
    return this.request<ApplicantClaim>(`/api/v1/applicants/${encodeURIComponent(profileId)}/claims/${encodeURIComponent(claimId)}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async listApplicantConflicts(profileId: string): Promise<ProfileConflict[]> {
    return this.request<ProfileConflict[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/conflicts`);
  }

  async resolveApplicantConflict(profileId: string, conflictId: string, payload: { resolution_choice: string; chosen_claim_id?: string; manual_value?: any; rationale?: string }): Promise<ProfileConflict> {
    return this.request<ProfileConflict>(`/api/v1/applicants/${encodeURIComponent(profileId)}/conflicts/${encodeURIComponent(conflictId)}/resolve`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async listApplicantEvidence(profileId: string): Promise<EvidenceMetadata[]> {
    return this.request<EvidenceMetadata[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/evidence`);
  }

  async deleteApplicantEvidence(profileId: string, evidenceId: string): Promise<any> {
    return this.request<any>(`/api/v1/applicants/${encodeURIComponent(profileId)}/evidence/${encodeURIComponent(evidenceId)}`, {
      method: 'DELETE',
    });
  }

  async createApplicantImport(profileId: string, payload: { filename: string; raw_text?: string; content_base64?: string }): Promise<ImportJob> {
    return this.request<ImportJob>(`/api/v1/applicants/${encodeURIComponent(profileId)}/imports`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getApplicantImport(profileId: string, importId: string): Promise<ImportJob> {
    return this.request<ImportJob>(`/api/v1/applicants/${encodeURIComponent(profileId)}/imports/${encodeURIComponent(importId)}`);
  }

  async reviewImportCandidate(profileId: string, importId: string, candidateId: string, action: string, modifiedData?: any, notes?: string): Promise<any> {
    return this.request<any>(`/api/v1/applicants/${encodeURIComponent(profileId)}/imports/${encodeURIComponent(importId)}/candidates/${encodeURIComponent(candidateId)}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, modified_data: modifiedData, notes }),
    });
  }

  async getApplicantQualityReport(profileId: string): Promise<DataQualityReport> {
    return this.request<DataQualityReport>(`/api/v1/applicants/${encodeURIComponent(profileId)}/quality`);
  }

  async generateApplicantSnapshot(profileId: string, targetAgent: string, scopes?: string[]): Promise<ProfileSnapshot> {
    return this.request<ProfileSnapshot>(`/api/v1/applicants/${encodeURIComponent(profileId)}/snapshot`, {
      method: 'POST',
      body: JSON.stringify({ target_agent: targetAgent, authorized_scopes: scopes }),
    });
  }

  async exportApplicantProfile(profileId: string): Promise<any> {
    return this.request<any>(`/api/v1/applicants/${encodeURIComponent(profileId)}/export`, {
      method: 'POST',
    });
  }

  async getApplicantVersions(profileId: string): Promise<ProfileVersionRecord[]> {
    return this.request<ProfileVersionRecord[]>(`/api/v1/applicants/${encodeURIComponent(profileId)}/versions`);
  }

  // =========================================================================
  // Stage 22: GitHub & Technical Portfolio Intelligence
  // =========================================================================

  async getGitHubStatus(): Promise<GitHubStatusSummary> {
    return this.request<GitHubStatusSummary>('/api/v1/github/status');
  }

  async getGitHubDiagnostics(): Promise<GitHubDiagnostics> {
    return this.request<GitHubDiagnostics>('/api/v1/github/diagnostics');
  }

  async listGitHubConnections(profileId?: string): Promise<GitHubConnection[]> {
    const query = profileId ? `?profile_id=${encodeURIComponent(profileId)}` : '';
    return this.request<GitHubConnection[]>(`/api/v1/github/connections${query}`);
  }

  async connectGitHubAccount(payload: ConnectGitHubRequest): Promise<GitHubConnection> {
    return this.request<GitHubConnection>('/api/v1/github/connections', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getGitHubConnection(connectionId: string): Promise<GitHubConnection> {
    return this.request<GitHubConnection>(`/api/v1/github/connections/${encodeURIComponent(connectionId)}`);
  }

  async disconnectGitHubAccount(connectionId: string): Promise<{ connection_id: string; disconnected: boolean }> {
    return this.request<{ connection_id: string; disconnected: boolean }>(`/api/v1/github/connections/${encodeURIComponent(connectionId)}/disconnect`, {
      method: 'POST',
    });
  }

  async getGitHubConnectionPermissions(connectionId: string): Promise<any> {
    return this.request<any>(`/api/v1/github/connections/${encodeURIComponent(connectionId)}/permissions`);
  }

  async listGitHubRepositories(connectionId?: string, onlySelected?: boolean): Promise<RepositoryMetadata[]> {
    const params = new URLSearchParams();
    if (connectionId) params.append('connection_id', connectionId);
    if (onlySelected) params.append('only_selected', 'true');
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<RepositoryMetadata[]>(`/api/v1/github/repositories${query}`);
  }

  async discoverGitHubRepositories(connectionId: string): Promise<RepositoryMetadata[]> {
    return this.request<RepositoryMetadata[]>('/api/v1/github/repositories/discover', {
      method: 'POST',
      body: JSON.stringify({ connection_id: connectionId }),
    });
  }

  async addManualGitHubRepository(payload: ManualRepoRequest): Promise<RepositoryMetadata> {
    return this.request<RepositoryMetadata>('/api/v1/github/repositories/manual', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getGitHubRepository(repoId: string): Promise<RepositoryMetadata> {
    return this.request<RepositoryMetadata>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}`);
  }

  async selectGitHubRepository(repoId: string, payload: SelectRepoRequest = { allow_source_inspection: true }): Promise<RepositoryMetadata> {
    return this.request<RepositoryMetadata>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/select`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async deselectGitHubRepository(repoId: string): Promise<RepositoryMetadata> {
    return this.request<RepositoryMetadata>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/deselect`, {
      method: 'POST',
    });
  }

  async syncGitHubRepository(repoId: string): Promise<RepositoryMetadata> {
    return this.request<RepositoryMetadata>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/sync`, {
      method: 'POST',
    });
  }

  async getGitHubRepositorySyncStatus(repoId: string): Promise<any> {
    return this.request<any>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/sync-status`);
  }

  async getGitHubRepositoryLanguages(repoId: string): Promise<{ repo_id: string; total_bytes: number; raw_bytes: Record<string, number>; percentages: Record<string, number> }> {
    return this.request<{ repo_id: string; total_bytes: number; raw_bytes: Record<string, number>; percentages: Record<string, number> }>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/languages`);
  }

  async getGitHubRepositoryTechnologies(repoId: string): Promise<TechnologyFinding[]> {
    return this.request<TechnologyFinding[]>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/technologies`);
  }

  async getGitHubRepositoryArchitecture(repoId: string): Promise<RepositoryArchitecture | null> {
    return this.request<RepositoryArchitecture | null>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/architecture`);
  }

  async getGitHubRepositoryContributions(repoId: string): Promise<ContributionFinding[]> {
    return this.request<ContributionFinding[]>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/contributions`);
  }

  async getGitHubRepositoryCommits(repoId: string): Promise<CommitEvidence[]> {
    return this.request<CommitEvidence[]>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/commits`);
  }

  async getGitHubRepositoryPullRequests(repoId: string): Promise<PullRequestEvidence[]> {
    return this.request<PullRequestEvidence[]>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/pull-requests`);
  }

  async getGitHubRepositoryTree(repoId: string, forceRefresh: boolean = false): Promise<SourceTreeEntry[]> {
    const query = forceRefresh ? '?force_refresh=true' : '';
    return this.request<SourceTreeEntry[]>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/tree${query}`);
  }

  async getGitHubRepositoryFile(repoId: string, path: string): Promise<FileContentSnippet> {
    return this.request<FileContentSnippet>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/file?path=${encodeURIComponent(path)}`);
  }

  async triggerGitHubRepositoryAnalysis(repoId: string): Promise<SyncJobRecord> {
    return this.request<SyncJobRecord>(`/api/v1/github/repositories/${encodeURIComponent(repoId)}/analyze`, {
      method: 'POST',
    });
  }

  async listGitHubAnalysisJobs(repoId?: string): Promise<SyncJobRecord[]> {
    const query = repoId ? `?repo_id=${encodeURIComponent(repoId)}` : '';
    return this.request<SyncJobRecord[]>(`/api/v1/github/analysis-jobs${query}`);
  }

  async getGitHubAnalysisJob(jobId: string): Promise<SyncJobRecord> {
    return this.request<SyncJobRecord>(`/api/v1/github/analysis-jobs/${encodeURIComponent(jobId)}`);
  }

  async listGitHubSkillCandidates(repoId?: string): Promise<CandidateSkill[]> {
    const query = repoId ? `?repo_id=${encodeURIComponent(repoId)}` : '';
    return this.request<CandidateSkill[]>(`/api/v1/github/skill-candidates${query}`);
  }

  async listGitHubProjectCandidates(repoId?: string): Promise<CandidateProject[]> {
    const query = repoId ? `?repo_id=${encodeURIComponent(repoId)}` : '';
    return this.request<CandidateProject[]>(`/api/v1/github/project-candidates${query}`);
  }

  async confirmGitHubSkillCandidate(candidateId: string, payload: ConfirmCandidateRequest = { profile_id: 'prof_primary_applicant' }): Promise<CandidateSkill> {
    return this.request<CandidateSkill>(`/api/v1/github/skill-candidates/${encodeURIComponent(candidateId)}/confirm`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async confirmGitHubProjectCandidate(candidateId: string, payload: ConfirmCandidateRequest = { profile_id: 'prof_primary_applicant' }): Promise<CandidateProject> {
    return this.request<CandidateProject>(`/api/v1/github/project-candidates/${encodeURIComponent(candidateId)}/confirm`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async rejectGitHubCandidate(candidateId: string): Promise<{ status: string; candidate_id: string }> {
    return this.request<{ status: string; candidate_id: string }>(`/api/v1/github/candidates/${encodeURIComponent(candidateId)}/reject`, {
      method: 'POST',
    });
  }

  // =========================================================================
  // Stage 23: Resume Intelligence & Professional Portfolio
  // =========================================================================

  async listResumes(resumeType?: string): Promise<ResumeDocument[]> {
    const query = resumeType ? `?resume_type=${encodeURIComponent(resumeType)}` : '';
    return this.request<ResumeDocument[]>(`/api/v1/resumes${query}`);
  }

  async createResume(req: ResumeCreateRequest): Promise<ResumeDocument> {
    return this.request<ResumeDocument>('/api/v1/resumes', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getResumesOverview(): Promise<ResumeOverviewStats> {
    return this.request<ResumeOverviewStats>('/api/v1/resumes/overview');
  }

  async getResume(resumeId: string): Promise<ResumeDocument> {
    return this.request<ResumeDocument>(`/api/v1/resumes/${encodeURIComponent(resumeId)}`);
  }

  async updateResume(resumeId: string, req: ResumeUpdateRequest): Promise<ResumeDocument> {
    return this.request<ResumeDocument>(`/api/v1/resumes/${encodeURIComponent(resumeId)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async deleteResume(resumeId: string): Promise<{ deleted: boolean }> {
    return this.request<{ deleted: boolean }>(`/api/v1/resumes/${encodeURIComponent(resumeId)}`, {
      method: 'DELETE',
    });
  }

  async duplicateResume(resumeId: string, newTitle?: string): Promise<ResumeDocument> {
    const query = newTitle ? `?new_title=${encodeURIComponent(newTitle)}` : '';
    return this.request<ResumeDocument>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/duplicate${query}`, {
      method: 'POST',
    });
  }

  async tailorResume(resumeId: string, req: ResumeTailorRequest): Promise<{
    resume: ResumeDocument;
    evidence_mappings: RequirementEvidenceMapping[];
    matched_count: number;
    missing_count: number;
  }> {
    return this.request<{
      resume: ResumeDocument;
      evidence_mappings: RequirementEvidenceMapping[];
      matched_count: number;
      missing_count: number;
    }>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/tailor`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getResumeValidation(resumeId: string): Promise<{
    resume_id: string;
    issue_count: number;
    issues: any[];
    is_valid: boolean;
  }> {
    return this.request<{
      resume_id: string;
      issue_count: number;
      issues: any[];
      is_valid: boolean;
    }>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/validation`);
  }

  async getResumeATSReport(resumeId: string): Promise<ATSReadabilityReport> {
    return this.request<ATSReadabilityReport>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/ats-report`);
  }

  async getResumePreview(resumeId: string): Promise<{ resume_id: string; html: string }> {
    return this.request<{ resume_id: string; html: string }>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/preview`);
  }

  async approveResume(resumeId: string): Promise<ResumeVersionRecord> {
    return this.request<ResumeVersionRecord>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/approve`, {
      method: 'POST',
    });
  }

  async listResumeVersions(resumeId: string): Promise<ResumeVersionRecord[]> {
    return this.request<ResumeVersionRecord[]>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/versions`);
  }

  async getResumeVersion(resumeId: string, versionId: string): Promise<ResumeVersionRecord> {
    return this.request<ResumeVersionRecord>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/versions/${encodeURIComponent(versionId)}`);
  }

  async exportResume(resumeId: string, req: ResumeExportRequest): Promise<ExportArtifact> {
    return this.request<ExportArtifact>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/export`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listResumeExports(resumeId: string): Promise<ExportArtifact[]> {
    return this.request<ExportArtifact[]>(`/api/v1/resumes/${encodeURIComponent(resumeId)}/exports`);
  }

  async listResumeTemplates(): Promise<ResumeTemplateDefinition[]> {
    return this.request<ResumeTemplateDefinition[]>('/api/v1/resume-templates');
  }

  async getResumeTemplate(templateId: string): Promise<ResumeTemplateDefinition> {
    return this.request<ResumeTemplateDefinition>(`/api/v1/resume-templates/${encodeURIComponent(templateId)}`);
  }

  async analyzeJobDescription(req: JobDescriptionParseRequest): Promise<JobDescriptionSnapshot> {
    return this.request<JobDescriptionSnapshot>('/api/v1/job-descriptions/analyze', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getJobDescription(jobId: string): Promise<JobDescriptionSnapshot> {
    return this.request<JobDescriptionSnapshot>(`/api/v1/job-descriptions/${encodeURIComponent(jobId)}`);
  }

  async listPortfolios(): Promise<PortfolioDocument[]> {
    return this.request<PortfolioDocument[]>('/api/v1/portfolios');
  }

  async createPortfolio(req: PortfolioCreateRequest): Promise<PortfolioDocument> {
    return this.request<PortfolioDocument>('/api/v1/portfolios', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getPortfolio(portfolioId: string): Promise<PortfolioDocument> {
    return this.request<PortfolioDocument>(`/api/v1/portfolios/${encodeURIComponent(portfolioId)}`);
  }

  async updatePortfolio(portfolioId: string, req: PortfolioUpdateRequest): Promise<PortfolioDocument> {
    return this.request<PortfolioDocument>(`/api/v1/portfolios/${encodeURIComponent(portfolioId)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async exportPortfolioPdf(portfolioId: string): Promise<{ portfolio_id: string; file_path: string; format: string }> {
    return this.request<{ portfolio_id: string; file_path: string; format: string }>(`/api/v1/portfolios/${encodeURIComponent(portfolioId)}/export/pdf`, {
      method: 'POST',
    });
  }

  async exportPortfolioHtml(portfolioId: string): Promise<{ portfolio_id: string; file_path: string; format: string }> {
    return this.request<{ portfolio_id: string; file_path: string; format: string }>(`/api/v1/portfolios/${encodeURIComponent(portfolioId)}/export/html`, {
      method: 'POST',
    });
  }

  // =========================================================================
  // Stage 24: Recruitment Writing & Application Question Intelligence
  // =========================================================================

  async getWritingOverview(): Promise<WritingOverviewStats> {
    return this.request<WritingOverviewStats>('/api/v1/recruitment/writing/overview');
  }

  async listCoverLetters(): Promise<CoverLetterDocument[]> {
    return this.request<CoverLetterDocument[]>('/api/v1/cover-letters');
  }

  async getCoverLetter(id: string): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>(`/api/v1/cover-letters/${encodeURIComponent(id)}`);
  }

  async createCoverLetter(req: CoverLetterCreateRequest): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>('/api/v1/cover-letters', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async updateCoverLetter(id: string, req: CoverLetterUpdateRequest): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>(`/api/v1/cover-letters/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async deleteCoverLetter(id: string): Promise<{ status: string; id: string }> {
    return this.request<{ status: string; id: string }>(`/api/v1/cover-letters/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async generateCoverLetter(req: CoverLetterGenerateRequest): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>('/api/v1/cover-letters/generate', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async validateCoverLetter(id: string): Promise<{ is_valid: boolean; errors: string[]; warnings: string[]; total_words: number; verified_facts_count: number }> {
    return this.request<{ is_valid: boolean; errors: string[]; warnings: string[]; total_words: number; verified_facts_count: number }>(`/api/v1/cover-letters/${encodeURIComponent(id)}/validate`);
  }

  async approveCoverLetter(id: string): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>(`/api/v1/cover-letters/${encodeURIComponent(id)}/approve`, {
      method: 'POST',
    });
  }

  async listCoverLetterVersions(id: string): Promise<CoverLetterVersionRecord[]> {
    return this.request<CoverLetterVersionRecord[]>(`/api/v1/cover-letters/${encodeURIComponent(id)}/versions`);
  }

  async restoreCoverLetterVersion(id: string, versionNumber: number): Promise<CoverLetterDocument> {
    return this.request<CoverLetterDocument>(`/api/v1/cover-letters/${encodeURIComponent(id)}/versions/${versionNumber}/restore`, {
      method: 'POST',
    });
  }

  async exportCoverLetter(id: string, req: CoverLetterExportRequest): Promise<{ cover_letter_id: string; format: string; file_path: string; sha256_checksum: string; text_extracted?: string }> {
    return this.request<{ cover_letter_id: string; format: string; file_path: string; sha256_checksum: string; text_extracted?: string }>(`/api/v1/cover-letters/${encodeURIComponent(id)}/export`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async rewriteCoverLetterParagraph(id: string, req: ParagraphRewriteRequest): Promise<{ paragraph_id: string; rewritten_text: string }> {
    return this.request<{ paragraph_id: string; rewritten_text: string }>(`/api/v1/cover-letters/${encodeURIComponent(id)}/rewrite-paragraph`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listCoverLetterTemplates(): Promise<CoverLetterTemplateDefinition[]> {
    return this.request<CoverLetterTemplateDefinition[]>('/api/v1/cover-letter-templates');
  }

  async parseApplicationQuestions(req: QuestionParseRequest): Promise<ApplicationQuestionRecord[]> {
    return this.request<ApplicationQuestionRecord[]>('/api/v1/application-questions/parse', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listQuestionSets(): Promise<ApplicationQuestionSet[]> {
    return this.request<ApplicationQuestionSet[]>('/api/v1/application-questions/sets');
  }

  async getQuestionSet(id: string): Promise<ApplicationQuestionSet> {
    return this.request<ApplicationQuestionSet>(`/api/v1/application-questions/sets/${encodeURIComponent(id)}`);
  }

  async createQuestionSet(req: QuestionSetCreateRequest): Promise<ApplicationQuestionSet> {
    return this.request<ApplicationQuestionSet>('/api/v1/application-questions/sets', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async generateAnswersForQuestionSet(setId: string): Promise<ApplicationAnswer[]> {
    return this.request<ApplicationAnswer[]>(`/api/v1/application-questions/sets/${encodeURIComponent(setId)}/generate-answers`, {
      method: 'POST',
    });
  }

  async updateAnswer(setId: string, questionId: string, req: AnswerUpdateRequest): Promise<ApplicationAnswer> {
    return this.request<ApplicationAnswer>(`/api/v1/application-questions/sets/${encodeURIComponent(setId)}/questions/${encodeURIComponent(questionId)}/answer`, {
      method: 'PUT',
      body: JSON.stringify(req),
    });
  }

  async listAnswerLibrary(category?: string, search?: string): Promise<AnswerLibraryEntry[]> {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (search) params.set('search', search);
    const qs = params.toString();
    return this.request<AnswerLibraryEntry[]>(`/api/v1/application-answers/library${qs ? `?${qs}` : ''}`);
  }

  async createAnswerLibraryEntry(req: AnswerLibraryCreateRequest): Promise<AnswerLibraryEntry> {
    return this.request<AnswerLibraryEntry>('/api/v1/application-answers/library', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async updateAnswerLibraryEntry(id: string, req: AnswerLibraryUpdateRequest): Promise<AnswerLibraryEntry> {
    return this.request<AnswerLibraryEntry>(`/api/v1/application-answers/library/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async previewAnswerReuse(id: string, req: AnswerReusePreviewRequest): Promise<{ original_template: string; resolved_text: string; target_employer?: string; target_role?: string; detected_placeholders: string[] }> {
    return this.request<{ original_template: string; resolved_text: string; target_employer?: string; target_role?: string; detected_placeholders: string[] }>(`/api/v1/application-answers/library/${encodeURIComponent(id)}/preview-reuse`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async deleteAnswerLibraryEntry(id: string): Promise<{ status: string; id: string }> {
    return this.request<{ status: string; id: string }>(`/api/v1/application-answers/library/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async checkAnswerLibraryFreshness(): Promise<{ total_entries: number; outdated_count: number; updated_entries?: string[] }> {
    return this.request<{ total_entries: number; outdated_count: number; updated_entries?: string[] }>('/api/v1/application-answers/library-check-freshness', {
      method: 'POST',
    });
  }

  async getMissingInformation(): Promise<MissingInformationItem[]> {
    return this.request<MissingInformationItem[]>('/api/v1/recruitment/writing/missing-information');
  }

  async getSensitiveDecisions(): Promise<SensitiveDecisionItem[]> {
    return this.request<SensitiveDecisionItem[]>('/api/v1/recruitment/writing/sensitive-decisions');
  }

  async recordUserAttestation(req: UserAttestationRequest): Promise<{ status: string; decision_id: string; timestamp: string }> {
    return this.request<{ status: string; decision_id: string; timestamp: string }>('/api/v1/application-sensitive-decisions/attest', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getWritingConflicts(): Promise<ConflictItem[]> {
    return this.request<ConflictItem[]>('/api/v1/recruitment/writing/conflicts');
  }

  async listWritingPackages(): Promise<ApplicationWritingPackage[]> {
    return this.request<ApplicationWritingPackage[]>('/api/v1/application-writing-packages');
  }

  async createWritingPackage(req: WritingPackageCreateRequest): Promise<ApplicationWritingPackage> {
    return this.request<ApplicationWritingPackage>('/api/v1/application-writing-packages', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getWritingPackage(id: string): Promise<ApplicationWritingPackage> {
    return this.request<ApplicationWritingPackage>(`/api/v1/application-writing-packages/${encodeURIComponent(id)}`);
  }

  async validateWritingPackage(id: string): Promise<{ is_valid: boolean; errors: string[]; warnings: string[]; ready_for_approval: boolean }> {
    return this.request<{ is_valid: boolean; errors: string[]; warnings: string[]; ready_for_approval: boolean }>(`/api/v1/application-writing-packages/${encodeURIComponent(id)}/validate`, {
      method: 'POST',
    });
  }

  async approveWritingPackage(id: string): Promise<ApplicationWritingPackage> {
    return this.request<ApplicationWritingPackage>(`/api/v1/application-writing-packages/${encodeURIComponent(id)}/approve`, {
      method: 'POST',
    });
  }

  // --- Recruitment Policy & Career Preferences (Stage 25) ---

  async listCareerStrategies(): Promise<CareerStrategy[]> {
    return this.request<CareerStrategy[]>('/api/v1/recruitment/career-strategies');
  }

  async getCareerStrategy(id: string): Promise<CareerStrategy> {
    return this.request<CareerStrategy>(`/api/v1/recruitment/career-strategies/${encodeURIComponent(id)}`);
  }

  async createCareerStrategy(req: CareerStrategyCreateRequest): Promise<CareerStrategy> {
    return this.request<CareerStrategy>('/api/v1/recruitment/career-strategies', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async updateCareerStrategy(id: string, req: CareerStrategyUpdateRequest): Promise<CareerStrategy> {
    return this.request<CareerStrategy>(`/api/v1/recruitment/career-strategies/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async activateCareerStrategy(id: string): Promise<CareerStrategy> {
    return this.request<CareerStrategy>(`/api/v1/recruitment/career-strategies/${encodeURIComponent(id)}/activate`, {
      method: 'POST',
    });
  }

  async deleteCareerStrategy(id: string): Promise<{ status: string; id: string }> {
    return this.request<{ status: string; id: string }>(`/api/v1/recruitment/career-strategies/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async getStrategyVersions(id: string): Promise<PolicyVersionSnapshot[]> {
    return this.request<PolicyVersionSnapshot[]>(`/api/v1/recruitment/career-strategies/${encodeURIComponent(id)}/versions`);
  }

  async getCareerPreferenceProfile(): Promise<CareerPreferenceProfile> {
    return this.request<CareerPreferenceProfile>('/api/v1/recruitment/career-profile');
  }

  async evaluateJobPolicy(job: Partial<JobOpportunityContext> & { title: string; employer_name: string }): Promise<RecruitmentDecision> {
    return this.request<RecruitmentDecision>('/api/v1/recruitment/policies/evaluate-job', {
      method: 'POST',
      body: JSON.stringify(job),
    });
  }

  async simulatePolicy(req: PolicySimulationRequest): Promise<PolicySimulationResponse> {
    return this.request<PolicySimulationResponse>('/api/v1/recruitment/policies/simulate', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async detectPolicyConflicts(strategyId?: string): Promise<PolicyConflictReport> {
    const query = strategyId ? `?strategy_id=${encodeURIComponent(strategyId)}` : '';
    return this.request<PolicyConflictReport>(`/api/v1/recruitment/policies/detect-conflicts${query}`);
  }

  async getAutonomyStatus(): Promise<AutonomyStatusResponse> {
    return this.request<AutonomyStatusResponse>('/api/v1/recruitment/autonomy/status');
  }

  async listStandingGrants(): Promise<StandingGrantRecord[]> {
    return this.request<StandingGrantRecord[]>('/api/v1/recruitment/autonomy/standing-grants');
  }

  async createStandingGrant(req: StandingGrantCreateRequest): Promise<StandingGrantRecord> {
    return this.request<StandingGrantRecord>('/api/v1/recruitment/autonomy/standing-grants', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async revokeStandingGrant(id: string, reason?: string): Promise<{ status: string; id: string; reason?: string }> {
    const query = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return this.request<{ status: string; id: string; reason?: string }>(`/api/v1/recruitment/autonomy/standing-grants/${encodeURIComponent(id)}/revoke${query}`, {
      method: 'POST',
    });
  }

  async getRecruitmentBudget(): Promise<RecruitmentBudget> {
    return this.request<RecruitmentBudget>('/api/v1/recruitment/budgets');
  }

  async updateRecruitmentBudget(req: Partial<RecruitmentBudget>): Promise<RecruitmentBudget> {
    return this.request<RecruitmentBudget>('/api/v1/recruitment/budgets', {
      method: 'PUT',
      body: JSON.stringify(req),
    });
  }

  async reserveBudgetSlot(req: BudgetReservationRequest): Promise<BudgetReservationResponse> {
    return this.request<BudgetReservationResponse>('/api/v1/recruitment/budgets/reserve', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async confirmBudgetSlot(req: BudgetConfirmationRequest): Promise<{ status: string; reservation_id: string }> {
    return this.request<{ status: string; reservation_id: string }>('/api/v1/recruitment/budgets/confirm', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async releaseBudgetSlot(req: BudgetReleaseRequest): Promise<{ status: string; reservation_id: string }> {
    return this.request<{ status: string; reservation_id: string }>('/api/v1/recruitment/budgets/release', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listReviewQueue(status?: string): Promise<ReviewQueueItem[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return this.request<ReviewQueueItem[]>(`/api/v1/recruitment/review-queue${query}`);
  }

  async resolveReviewQueueItem(id: string, req: ReviewQueueResolutionRequest): Promise<ReviewQueueItem> {
    return this.request<ReviewQueueItem>(`/api/v1/recruitment/review-queue/${encodeURIComponent(id)}/resolve`, {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listPolicyDecisions(limit: number = 50): Promise<RecruitmentDecision[]> {
    return this.request<RecruitmentDecision[]>(`/api/v1/recruitment/decisions?limit=${limit}`);
  }

  async getPolicyDecision(id: string): Promise<RecruitmentDecision> {
    return this.request<RecruitmentDecision>(`/api/v1/recruitment/decisions/${encodeURIComponent(id)}`);
  }

  async getPolicyDiagnostics(): Promise<PolicyDiagnosticsResponse> {
    return this.request<PolicyDiagnosticsResponse>('/api/v1/recruitment/policy-diagnostics');
  }

  // ---------------------------------------------------------------------------
  // Stage 26: Multi-Source Job Discovery Engine
  // ---------------------------------------------------------------------------
  async getDiscoveryOverview(): Promise<DiscoveryOverviewStats> {
    return this.request<DiscoveryOverviewStats>('/api/v1/recruitment/discovery/overview');
  }

  async getDiscoveryDiagnostics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>('/api/v1/recruitment/discovery/diagnostics');
  }

  async listDiscoveryConnectors(): Promise<ConnectorManifest[]> {
    return this.request<ConnectorManifest[]>('/api/v1/recruitment/discovery/connectors');
  }

  async getDiscoveryConnector(id: string): Promise<ConnectorManifest> {
    return this.request<ConnectorManifest>(`/api/v1/recruitment/discovery/connectors/${encodeURIComponent(id)}`);
  }

  async listJobSources(enabledOnly: boolean = false): Promise<JobSourceConfig[]> {
    return this.request<JobSourceConfig[]>(`/api/v1/recruitment/discovery/sources?enabled_only=${enabledOnly}`);
  }

  async getJobSource(id: string): Promise<JobSourceConfig> {
    return this.request<JobSourceConfig>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}`);
  }

  async createJobSource(req: JobSourceCreateRequest): Promise<JobSourceConfig> {
    return this.request<JobSourceConfig>('/api/v1/recruitment/discovery/sources', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async updateJobSource(id: string, req: JobSourceUpdateRequest): Promise<JobSourceConfig> {
    return this.request<JobSourceConfig>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(req),
    });
  }

  async deleteJobSource(id: string): Promise<{ source_id: string; deleted: boolean }> {
    return this.request<{ source_id: string; deleted: boolean }>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async validateJobSource(id: string): Promise<SourceValidationResult> {
    return this.request<SourceValidationResult>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}/validate`, {
      method: 'POST',
    });
  }

  async refreshJobSource(id: string): Promise<JobSourceSnapshot> {
    return this.request<JobSourceSnapshot>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}/refresh`, {
      method: 'POST',
    });
  }

  async getJobSourceHealth(id: string): Promise<JobSourceHealth> {
    return this.request<JobSourceHealth>(`/api/v1/recruitment/discovery/sources/${encodeURIComponent(id)}/health`);
  }

  async listEmployerCareerSources(enabledOnly: boolean = false): Promise<EmployerCareerSource[]> {
    return this.request<EmployerCareerSource[]>(`/api/v1/recruitment/discovery/employers?enabled_only=${enabledOnly}`);
  }

  async addEmployerCareerSource(req: EmployerCareerPageCreateRequest): Promise<EmployerCareerSource> {
    return this.request<EmployerCareerSource>('/api/v1/recruitment/discovery/employers', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async deleteEmployerCareerSource(id: string): Promise<{ employer_id: string; deleted: boolean }> {
    return this.request<{ employer_id: string; deleted: boolean }>(`/api/v1/recruitment/discovery/employers/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  }

  async importJobUrl(req: UrlImportRequest): Promise<JobSourceObservation> {
    return this.request<JobSourceObservation>('/api/v1/recruitment/discovery/import/url', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async importJobManual(req: ManualImportRequest): Promise<JobSourceObservation> {
    return this.request<JobSourceObservation>('/api/v1/recruitment/discovery/import/manual', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async listJobObservations(params?: {
    source_id?: string;
    availability?: PostingAvailability;
    prefilter?: PrefilterOutcome;
    query?: string;
    limit?: number;
  }): Promise<JobSourceObservation[]> {
    const q = new URLSearchParams();
    if (params?.source_id) q.set('source_id', params.source_id);
    if (params?.availability) q.set('availability', params.availability);
    if (params?.prefilter) q.set('prefilter', params.prefilter);
    if (params?.query) q.set('query', params.query);
    if (params?.limit) q.set('limit', String(params.limit));
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<JobSourceObservation[]>(`/api/v1/recruitment/discovery/postings${qs}`);
  }

  async getJobObservation(id: string): Promise<JobSourceObservation> {
    return this.request<JobSourceObservation>(`/api/v1/recruitment/discovery/postings/${encodeURIComponent(id)}`);
  }

  async listDiscoveryTasks(limit: number = 50): Promise<DiscoveryTaskRecord[]> {
    return this.request<DiscoveryTaskRecord[]>(`/api/v1/recruitment/discovery/tasks?limit=${limit}`);
  }

  async createDiscoveryTask(req: DiscoveryTaskCreateRequest): Promise<DiscoveryTaskRecord> {
    return this.request<DiscoveryTaskRecord>('/api/v1/recruitment/discovery/tasks', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async getDiscoveryTask(id: string): Promise<DiscoveryTaskRecord> {
    return this.request<DiscoveryTaskRecord>(`/api/v1/recruitment/discovery/tasks/${encodeURIComponent(id)}`);
  }

  async cancelDiscoveryTask(id: string): Promise<{ task_id: string; cancelled: boolean }> {
    return this.request<{ task_id: string; cancelled: boolean }>(`/api/v1/recruitment/discovery/tasks/${encodeURIComponent(id)}/cancel`, {
      method: 'POST',
    });
  }

  async getDiscoverySettings(): Promise<DiscoverySettingsConfig> {
    return this.request<DiscoverySettingsConfig>('/api/v1/recruitment/discovery/settings');
  }

  async updateDiscoverySettings(req: DiscoverySettingsConfig): Promise<DiscoverySettingsConfig> {
    return this.request<DiscoverySettingsConfig>('/api/v1/recruitment/discovery/settings', {
      method: 'PUT',
      body: JSON.stringify(req),
    });
  }
}

export const apiClient = new ApiClient();
