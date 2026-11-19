import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobAggregationWorkspace } from '@/features/recruitment/aggregation/JobAggregationWorkspace';

// Mock apiClient methods
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    getAggregationStatus: vi.fn().mockResolvedValue({
      total_source_observations: 42,
      total_canonical_jobs: 30,
      multi_source_canonical_jobs: 12,
      pending_duplicate_reviews: 2,
      confirmed_duplicate_merges: 10,
      unresolved_employer_identities: 1,
      active_field_conflicts: 3,
      running_tasks: 0,
      last_sync_timestamp: '2026-11-19T10:00:00Z',
    }),
    getAggregationDiagnostics: vi.fn().mockResolvedValue({
      status: 'healthy',
      database_connected: true,
      canonical_jobs_count: 30,
      canonical_employers_count: 15,
      active_conflicts_count: 3,
      unresolved_candidates_count: 2,
      recent_tasks: [],
      system_timestamp: '2026-11-19T10:00:00Z',
    }),
    listCanonicalJobs: vi.fn().mockResolvedValue([
      {
        id: 'cjob_test_1',
        employer_name: 'Stripe',
        display_title: 'Senior Staff Engineer',
        normalized_title: 'senior staff engineer',
        requisition_id: 'REQ-1001',
        employment_type: 'full_time',
        location_summary: 'San Francisco, CA',
        work_arrangement: 'hybrid',
        status: 'active',
        version: 2,
        source_count: 2,
        identity_status: 'canonical',
        conflict_state: 'no_conflict',
        sources: [],
        locations: [],
        identifiers: [],
        conflicts: [],
        created_at: '2026-11-19T09:00:00Z',
        updated_at: '2026-11-19T10:00:00Z',
      },
    ]),
    getCanonicalJob: vi.fn().mockResolvedValue(null),
    getCanonicalJobHistory: vi.fn().mockResolvedValue([]),
    listCanonicalEmployers: vi.fn().mockResolvedValue([
      {
        id: 'emp_1',
        name: 'Stripe',
        legal_name: 'Stripe, Inc.',
        organization_type: 'direct_employer',
        identity_status: 'canonical',
        primary_domain: 'stripe.com',
        confidence_score: 0.98,
        aliases: ['Stripe Inc'],
        verified_domains: ['stripe.com'],
        provider_boards: [],
        created_at: '2026-11-19T09:00:00Z',
        updated_at: '2026-11-19T10:00:00Z',
      },
    ]),
    listDuplicateCandidates: vi.fn().mockResolvedValue([]),
    listGlobalFieldConflicts: vi.fn().mockResolvedValue([]),
    listAggregationTasks: vi.fn().mockResolvedValue([]),
    getAggregationSettings: vi.fn().mockResolvedValue({
      auto_merge_enabled: true,
      min_similarity_for_candidate: 0.75,
      min_similarity_for_auto_merge: 0.92,
      require_same_requisition: true,
      enable_ai_assisted_review: true,
      batch_size: 50,
      worker_concurrency: 2,
      updated_at: '2026-11-19T10:00:00Z',
    }),
  },
}));

function renderWorkspace() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <JobAggregationWorkspace />
    </QueryClientProvider>
  );
}

describe('JobAggregationWorkspace Component', () => {
  it('renders workspace header and overview telemetry', async () => {
    renderWorkspace();
    expect(screen.getByText(/Multi-Source Job Aggregation & Canonical Database/i)).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Overview & Telemetry/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Canonical Jobs')).toBeInTheDocument();
      expect(screen.getByText('Source Observations')).toBeInTheDocument();
    });
  });

  it('renders navigation tabs for all functional areas', () => {
    renderWorkspace();
    expect(screen.getByRole('tab', { name: /Overview & Telemetry/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Employers/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Review Queue/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Merge & Split Ops/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Field Conflicts/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Aggregation Tasks/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Aggregation Policy/i })).toBeInTheDocument();
  });

  it('switches to Employers tab when clicked', async () => {
    renderWorkspace();
    const employersTab = screen.getByRole('tab', { name: /Employers/i });
    fireEvent.click(employersTab);

    await waitFor(() => {
      expect(screen.getByText(/Interactive Employer Identity Resolver/i)).toBeInTheDocument();
    });
  });

  it('switches to Merge & Split Ops tab when clicked', async () => {
    renderWorkspace();
    const mergeSplitTab = screen.getByRole('tab', { name: /Merge & Split Ops/i });
    fireEvent.click(mergeSplitTab);

    await waitFor(() => {
      expect(screen.getByText(/Transactional Canonical Job Merge/i)).toBeInTheDocument();
      expect(screen.getByText(/Transactional Canonical Job Split \/ Unmerge/i)).toBeInTheDocument();
    });
  });
});
