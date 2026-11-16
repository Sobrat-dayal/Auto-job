/**
 * Typed API Client for AUTONOM Backend Service
 */

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

  async getHealth(): Promise<BackendHealth> {
    return this.request<BackendHealth>('/api/v1/health');
  }

  async getVersion(): Promise<BackendVersion> {
    return this.request<BackendVersion>('/api/v1/version');
  }

  async getReadiness(): Promise<BackendReadiness> {
    return this.request<BackendReadiness>('/api/v1/ready');
  }
}

export const apiClient = new ApiClient();
