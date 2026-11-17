import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AIWorkspace } from '@/features/ai/AIWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  HardwareTelemetry,
  ModelInfo,
  ProviderSummary,
  AIRoutingPreference,
  AIUsageSummary,
  RoutingDecision,
} from '@autonom/shared-types';

describe('AIWorkspace (Stage 11)', () => {
  const mockTelemetry: HardwareTelemetry = {
    system_ram_total_mb: 16384,
    system_ram_available_mb: 8192,
    system_ram_used_mb: 8192,
    system_ram_percent: 50,
    gpu_name: 'NVIDIA GeForce RTX 4050 Laptop GPU',
    gpu_vram_total_mb: 6141,
    gpu_vram_used_mb: 2048,
    gpu_vram_available_mb: 4093,
    gpu_vram_percent: 33,
    active_local_model: 'llama3:8b',
    active_inference_count: 0,
    local_concurrency_limit: 1,
    timestamp: new Date().toISOString(),
  };

  const mockModels: ModelInfo[] = [
    {
      id: 'ollama:llama3:8b',
      provider_id: 'ollama',
      model_id: 'llama3:8b',
      display_name: 'Llama 3 8B Instruct (Local)',
      provider_type: 'local',
      is_available: true,
      context_window: 8192,
      max_output_tokens: 4096,
      capabilities: ['chat', 'streaming', 'structured_output'],
      pricing: { input_cost_per_million: 0, output_cost_per_million: 0 },
      quantization: 'Q4_K_M',
      reported_size_bytes: 4700000000,
      last_discovered_at: new Date().toISOString(),
    },
    {
      id: 'openai:gpt-4o',
      provider_id: 'openai',
      model_id: 'gpt-4o',
      display_name: 'GPT-4o (Omni Cloud)',
      provider_type: 'cloud',
      is_available: true,
      context_window: 128000,
      max_output_tokens: 4096,
      capabilities: ['chat', 'streaming', 'structured_output', 'vision', 'tool_calling'],
      pricing: { input_cost_per_million: 2.5, output_cost_per_million: 10.0 },
      last_discovered_at: new Date().toISOString(),
    },
  ];

  const mockProviders: ProviderSummary[] = [
    {
      provider_id: 'ollama',
      display_name: 'Ollama (Local Runtime)',
      provider_type: 'local',
      is_healthy: true,
      status: 'available',
      latency_ms: 12,
    },
    {
      provider_id: 'openai',
      display_name: 'OpenAI Cloud Platform',
      provider_type: 'cloud',
      is_healthy: true,
      status: 'available',
      latency_ms: 180,
    },
  ];

  const mockPreferences: AIRoutingPreference[] = [
    {
      category: 'job_description_analysis',
      preferred_provider: 'ollama',
      preferred_model: 'llama3:8b',
      fallback_provider: 'openai',
      fallback_model: 'gpt-4o-mini',
      is_local_only: false,
      updated_at: new Date().toISOString(),
    },
  ];

  const mockUsage: AIUsageSummary = {
    time_range_days: 30,
    total_requests: 42,
    successful_requests: 40,
    failed_requests: 2,
    cancelled_requests: 0,
    success_rate_percent: 95.2,
    total_prompt_tokens: 25000,
    total_completion_tokens: 15000,
    total_tokens: 40000,
    total_estimated_cost_usd: 0.052,
    average_latency_ms: 680,
    local_requests: 35,
    cloud_requests: 7,
    by_provider: [
      { provider_id: 'ollama', requests: 35, tokens: 32000, cost_usd: 0 },
      { provider_id: 'openai', requests: 7, tokens: 8000, cost_usd: 0.052 },
    ],
    by_model: [
      { provider_id: 'ollama', model_id: 'llama3:8b', requests: 35, tokens: 32000, cost_usd: 0 },
      { provider_id: 'openai', model_id: 'gpt-4o', requests: 7, tokens: 8000, cost_usd: 0.052 },
    ],
  };

  const mockDecision: RoutingDecision = {
    selected_provider_id: 'ollama',
    selected_model_id: 'llama3:8b',
    strategy_used: 'local_first',
    rule_applied: 'Local Preferred (Active in VRAM)',
    explanation: 'Category job_description_analysis preferred model ollama:llama3:8b is already loaded in VRAM.',
    candidates_considered: ['ollama:llama3:8b', 'openai:gpt-4o'],
    fallbacks_available: ['openai:gpt-4o-mini'],
    is_local: true,
  };

  beforeEach(() => {
    vi.spyOn(apiClient, 'getAIHardwareResources').mockResolvedValue(mockTelemetry);
    vi.spyOn(apiClient, 'getAIModels').mockResolvedValue(mockModels);
    vi.spyOn(apiClient, 'getAIProviders').mockResolvedValue(mockProviders);
    vi.spyOn(apiClient, 'getAIRoutingPreferences').mockResolvedValue(mockPreferences);
    vi.spyOn(apiClient, 'getAIUsageSummary').mockResolvedValue(mockUsage);
    vi.spyOn(apiClient, 'listInferenceRequests').mockResolvedValue({ items: [], total: 0 });
    vi.spyOn(apiClient, 'previewAIRoute').mockResolvedValue(mockDecision);
  });

  it('renders AI Gateway workspace header and hardware telemetry', async () => {
    render(
      <MemoryRouter initialEntries={['/ai/playground']}>
        <AIWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('AI Model Gateway');

    await waitFor(() => {
      expect(screen.getByText('HARDWARE & LOCAL VRAM TELEMETRY')).toBeInTheDocument();
      expect(screen.getByText('Single-Model VRAM Guard Active')).toBeInTheDocument();
      expect(screen.getByText(/NVIDIA GeForce RTX 4050/)).toBeInTheDocument();
      expect(screen.getByText(/llama3:8b/)).toBeInTheDocument();
    });
  });

  it('renders all 4 gateway tabs', async () => {
    render(
      <MemoryRouter initialEntries={['/ai/playground']}>
        <AIWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /AI Playground/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Model Management/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Model Routing/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /AI Usage/i })).toBeInTheDocument();
    });
  });

  it('renders Model Management tab with discovered models and Ollama provider', async () => {
    render(
      <MemoryRouter initialEntries={['/ai/models']}>
        <AIWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Llama 3 8B Instruct (Local)')).toBeInTheDocument();
      expect(screen.getByText('GPT-4o (Omni Cloud)')).toBeInTheDocument();
      expect(screen.getByText('Ollama (Local Runtime)')).toBeInTheDocument();
    });
  });

  it('renders Model Routing tab with 16 categories table and routing preview', async () => {
    render(
      <MemoryRouter initialEntries={['/ai/routing']}>
        <AIWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Intelligent Model Routing Simulator')).toBeInTheDocument();
      expect(screen.getByText(/Category Routing Preferences/)).toBeInTheDocument();
    });
  });

  it('renders AI Usage tab with KPIs and tokens', async () => {
    render(
      <MemoryRouter initialEntries={['/ai/usage']}>
        <AIWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Total Inferences')).toBeInTheDocument();
      expect(screen.getByText('Local Execution Ratio')).toBeInTheDocument();
      expect(screen.getByText('Cloud Spend (USD)')).toBeInTheDocument();
      expect(screen.getByText('40,000')).toBeInTheDocument(); // total tokens
    });
  });
});
