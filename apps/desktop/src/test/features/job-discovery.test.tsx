/**
 * Vitest Integration Suite for Stage 26 Multi-Source Job Discovery Engine Workspace.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobDiscoveryWorkspace } from '@/features/recruitment/discovery/JobDiscoveryWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  DiscoveryOverviewStats,
  JobSourceConfig,
  ConnectorManifest,
  EmployerCareerSource,
  JobSourceObservation,
  DiscoveryTaskRecord,
  DiscoverySettingsConfig,
} from '@autonom/shared-types';

describe('Job Discovery Engine Desktop Workspace (Stage 26)', () => {
  let queryClient: QueryClient;

  const mockOverviewStats: DiscoveryOverviewStats = {
    total_sources: 5,
    enabled_sources: 4,
    total_observations: 42,
    active_postings_count: 38,
    recently_discovered_count: 12,
    failed_sources_count: 0,
    rate_limited_sources_count: 0,
    active_tasks_count: 1,
  };

  const mockSources: JobSourceConfig[] = [
    {
      id: 'src_greenhouse_stripe',
      name: 'Stripe Careers (Greenhouse)',
      connector_id: 'greenhouse',
      category: 'employer_ats_board',
      official_domain: 'boards-api.greenhouse.io',
      board_token: 'stripe',
      employer_name: 'Stripe',
      access_status: 'available_public',
      is_enabled: true,
      rate_limit_rpm: 30,
      custom_headers: {},
      custom_params: {},
      created_at: '2026-03-30T10:00:00Z',
      updated_at: '2026-03-30T10:00:00Z',
    },
    {
      id: 'src_lever_netflix',
      name: 'Netflix Careers (Lever)',
      connector_id: 'lever',
      category: 'employer_ats_board',
      official_domain: 'api.lever.co',
      board_token: 'netflix',
      employer_name: 'Netflix',
      access_status: 'available_public',
      is_enabled: true,
      rate_limit_rpm: 30,
      custom_headers: {},
      custom_params: {},
      created_at: '2026-03-30T10:00:00Z',
      updated_at: '2026-03-30T10:00:00Z',
    },
  ];

  const mockConnectors: ConnectorManifest[] = [
    {
      connector_id: 'greenhouse',
      version: '1.0.0',
      provider_name: 'Greenhouse Job Board API',
      endpoint_category: 'employer_ats_board',
      authentication_method: 'none',
      required_permissions: [],
      supported_capabilities: ['list_postings', 'get_posting_details'],
      provider_restrictions: [],
      last_verified_doc_url: 'https://developers.greenhouse.io',
      last_verified_at: '2026-03-30T10:00:00Z',
    },
  ];

  const mockEmployers: EmployerCareerSource[] = [
    {
      id: 'emp_stripe',
      employer_name: 'Stripe',
      career_url: 'https://boards.greenhouse.io/stripe',
      provider_type: 'greenhouse',
      board_token: 'stripe',
      approved_origin: 'boards.greenhouse.io',
      access_status: 'available_public',
      is_enabled: true,
      created_at: '2026-03-30T10:00:00Z',
    },
  ];

  const mockPostings: JobSourceObservation[] = [
    {
      id: 'obs_1',
      source_id: 'src_greenhouse_stripe',
      provider: 'greenhouse',
      native_posting_id: '998877',
      source_url: 'https://boards.greenhouse.io/stripe/jobs/998877',
      title: 'Staff Distributed Systems Engineer',
      employer: 'Stripe',
      location: {
        city: 'San Francisco',
        country: 'United States',
        is_remote: true,
        workplace_type: 'remote',
      },
      employment_type: 'full_time',
      compensation: {
        min_amount: 190000,
        max_amount: 250000,
        currency: 'USD',
      },
      description_text: 'Design distributed storage and consensus protocols.',
      discovered_at: '2026-03-30T10:00:00Z',
      last_fetched_at: '2026-03-30T10:00:00Z',
      availability: 'available',
      prefilter_status: 'prefilter_accepted',
      prefilter_reasons: ['Matches active strategy'],
      extraction_version: '1.0.0',
    },
  ];

  const mockTasks: DiscoveryTaskRecord[] = [
    {
      id: 'task_abc_1',
      requested_sources: ['src_greenhouse_stripe'],
      selected_sources: ['src_greenhouse_stripe'],
      status: 'completed',
      started_at: '2026-03-30T10:00:00Z',
      completed_at: '2026-03-30T10:01:00Z',
      total_postings_found: 12,
      new_postings_count: 3,
      errors: [],
      cancellation_requested: false,
      source_snapshots: {},
    },
  ];

  const mockSettings: DiscoverySettingsConfig = {
    max_concurrent_sources: 4,
    per_source_request_rpm: 30,
    request_timeout_seconds: 20,
    max_postings_per_task: 200,
    max_browser_sessions: 1,
    cache_duration_minutes: 60,
    allow_browser_fallback: true,
    enforce_ssrf_protection: true,
    local_only_preference: false,
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });
    vi.clearAllMocks();

    vi.spyOn(apiClient, 'getDiscoveryOverview').mockResolvedValue(mockOverviewStats);
    vi.spyOn(apiClient, 'listJobSources').mockResolvedValue(mockSources);
    vi.spyOn(apiClient, 'listDiscoveryConnectors').mockResolvedValue(mockConnectors);
    vi.spyOn(apiClient, 'listEmployerCareerSources').mockResolvedValue(mockEmployers);
    vi.spyOn(apiClient, 'listJobObservations').mockResolvedValue(mockPostings);
    vi.spyOn(apiClient, 'listDiscoveryTasks').mockResolvedValue(mockTasks);
    vi.spyOn(apiClient, 'getDiscoveryDiagnostics').mockResolvedValue({ source_health: [] });
    vi.spyOn(apiClient, 'getDiscoverySettings').mockResolvedValue(mockSettings);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JobDiscoveryWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders discovery workspace header and summary KPI metrics', async () => {
    renderComponent();

    expect(screen.getAllByText('Multi-Source Job Discovery Engine').length).toBeGreaterThanOrEqual(1);
    await waitFor(() => {
      expect(screen.getByText('Configured Sources')).toBeDefined();
      expect(screen.getByText('Observed Postings')).toBeDefined();
      expect(screen.getByText('42')).toBeDefined();
    });
  });

  it('navigates to Job Sources tab and displays configured sources', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Sources')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Job Sources'));

    await waitFor(() => {
      expect(screen.getByText('Stripe Careers (Greenhouse)')).toBeDefined();
      expect(screen.getByText('Netflix Careers (Lever)')).toBeDefined();
    });
  });

  it('navigates to Discovered Jobs tab and displays vacancies', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Discovered Jobs')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Discovered Jobs'));

    await waitFor(() => {
      expect(screen.getByText('Staff Distributed Systems Engineer')).toBeDefined();
      expect(screen.getByText('Stripe')).toBeDefined();
      expect(screen.getByText('prefilter accepted')).toBeDefined();
    });
  });

  it('navigates to Single Job Import tab and switches between URL and manual modes', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Single Job Import')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Single Job Import'));

    await waitFor(() => {
      expect(screen.getByText('Import from Job URL')).toBeDefined();
      expect(screen.getByText('Manual Job Posting Entry')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Manual Job Posting Entry'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText('e.g. Distributed Systems Engineer')).toBeDefined();
    });
  });

  it('navigates to Tasks Monitor and displays background executions', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Tasks Monitor')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Tasks Monitor'));

    await waitFor(() => {
      expect(screen.getByText('task_abc_1')).toBeDefined();
      expect(screen.getByText('completed')).toBeDefined();
    });
  });
});
