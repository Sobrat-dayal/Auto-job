import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GitHubPortfolioWorkspace } from '@/features/recruitment/github/GitHubPortfolioWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  GitHubConnection,
  GitHubStatusSummary,
  GitHubDiagnostics,
  RepositoryMetadata,
  CandidateSkill,
  CandidateProject,
  TechnologyFinding,
  CommitEvidence,
  PullRequestEvidence,
  ContributionFinding,
  SyncJobRecord,
} from '@autonom/shared-types';

describe('GitHub & Technical Portfolio Intelligence (Stage 22)', () => {
  let queryClient: QueryClient;

  const mockStatus: GitHubStatusSummary = {
    status: 'ready',
    total_connections: 1,
    active_user: 'octocat',
    total_discovered_repositories: 12,
    total_selected_repositories: 3,
    total_analyzed_repositories: 2,
    rate_limit: {
      remaining: 4950,
      limit: 5000,
    },
    review_queue: {
      pending_skills: 4,
      pending_projects: 2,
      confirmed_claims: 8,
    },
    cache_entries: 14,
    errors: 0,
  };

  const mockConnection: GitHubConnection = {
    id: 'ghc_test_01',
    login: 'octocat',
    github_id: 583231,
    name: 'The Octocat',
    email: 'octocat@github.com',
    avatar_url: 'https://avatars.githubusercontent.com/u/583231?v=4',
    mode: 'personal_access_token',
    status: 'connected',
    scopes: ['repo:status', 'public_repo', 'read:user'],
    can_access_private: true,
    public_repos_count: 8,
    total_private_repos_count: 4,
    followers_count: 4500,
    following_count: 9,
    connected_at: '2026-11-18T10:00:00Z',
    last_validated_at: '2026-11-18T18:00:00Z',
  };

  const mockRepos: RepositoryMetadata[] = [
    {
      id: 'repo_autonom_core',
      github_repo_id: 10101,
      owner: 'octocat',
      name: 'autonom-core',
      full_name: 'octocat/autonom-core',
      html_url: 'https://github.com/octocat/autonom-core',
      description: 'Production distributed multi-agent orchestrator written in Rust and Python.',
      visibility: 'public',
      is_fork: false,
      is_archived: false,
      is_disabled: false,
      default_branch: 'main',
      default_branch_commit_sha: 'a1b2c3d4e5f6',
      primary_language: 'Rust',
      languages: { Rust: 120500, Python: 45200 },
      topics: ['rust', 'multi-agent', 'distributed-systems'],
      stars_count: 142,
      forks_count: 18,
      open_issues_count: 2,
      size_kb: 450,
      is_selected: true,
      allow_source_inspection: true,
      sync_status: 'completed',
      last_synced_at: '2026-11-18T19:00:00Z',
    },
    {
      id: 'repo_fastapi_service',
      github_repo_id: 10102,
      owner: 'octocat',
      name: 'fastapi-service',
      full_name: 'octocat/fastapi-service',
      html_url: 'https://github.com/octocat/fastapi-service',
      description: 'High-throughput async API service with PostgreSQL and Redis.',
      visibility: 'public',
      is_fork: false,
      is_archived: false,
      is_disabled: false,
      default_branch: 'main',
      primary_language: 'Python',
      languages: { Python: 89000 },
      topics: ['fastapi', 'postgresql', 'redis'],
      stars_count: 85,
      forks_count: 7,
      open_issues_count: 0,
      size_kb: 310,
      is_selected: true,
      allow_source_inspection: true,
      sync_status: 'completed',
    },
  ];

  const mockSkills: CandidateSkill[] = [
    {
      id: 'csk_rust_01',
      name: 'Rust',
      category: 'programming_language',
      version: '1.78.0',
      proficiency_hint: 'advanced',
      evidence_repo_id: 'repo_autonom_core',
      evidence_repo_name: 'autonom-core',
      evidence_file_path: 'Cargo.toml',
      confidence: 'strongly_supported',
      status: 'awaiting_review',
      created_at: '2026-11-18T19:05:00Z',
    },
    {
      id: 'csk_fastapi_01',
      name: 'FastAPI',
      category: 'framework',
      version: '0.115.0',
      proficiency_hint: 'expert',
      evidence_repo_id: 'repo_fastapi_service',
      evidence_repo_name: 'fastapi-service',
      evidence_file_path: 'pyproject.toml',
      confidence: 'strongly_supported',
      status: 'awaiting_review',
      created_at: '2026-11-18T19:05:00Z',
    },
  ];

  const mockProjects: CandidateProject[] = [
    {
      id: 'cpj_autonom_01',
      title: 'autonom-core',
      description: 'Production distributed multi-agent orchestrator written in Rust and Python.',
      repo_id: 'repo_autonom_core',
      repo_name: 'autonom-core',
      repo_url: 'https://github.com/octocat/autonom-core',
      technologies: ['Rust', 'Python', 'Tokio'],
      architecture_type: 'backend_api',
      stars: 142,
      is_fork: false,
      status: 'awaiting_review',
      created_at: '2026-11-18T19:05:00Z',
    },
  ];

  const mockDiagnostics: GitHubDiagnostics = {
    total_connections: 1,
    active_connection_user: 'octocat',
    total_discovered_repositories: 12,
    total_selected_repositories: 3,
    total_analyzed_repositories: 2,
    rate_limit_remaining: 4950,
    rate_limit_limit: 5000,
    pending_skill_candidates: 2,
    pending_project_candidates: 1,
    confirmed_claims_count: 8,
    cached_etag_entries: 14,
    sync_error_count: 0,
  };

  const mockSyncJobs: SyncJobRecord[] = [
    {
      job_id: 'sjb_test_01',
      repo_id: 'repo_autonom_core',
      repo_name: 'autonom-core',
      status: 'completed',
      started_at: '2026-11-18T19:00:00Z',
      completed_at: '2026-11-18T19:02:00Z',
      files_analyzed: 45,
      bytes_analyzed: 165700,
      api_calls_made: 5,
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    vi.spyOn(apiClient, 'getGitHubStatus').mockResolvedValue(mockStatus);
    vi.spyOn(apiClient, 'listGitHubConnections').mockResolvedValue([mockConnection]);
    vi.spyOn(apiClient, 'listGitHubRepositories').mockResolvedValue(mockRepos);
    vi.spyOn(apiClient, 'listGitHubSkillCandidates').mockResolvedValue(mockSkills);
    vi.spyOn(apiClient, 'listGitHubProjectCandidates').mockResolvedValue(mockProjects);
    vi.spyOn(apiClient, 'getGitHubDiagnostics').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'listGitHubAnalysisJobs').mockResolvedValue(mockSyncJobs);
    vi.spyOn(apiClient, 'getGitHubRepositoryTechnologies').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getGitHubRepositoryArchitecture').mockResolvedValue(null);
    vi.spyOn(apiClient, 'getGitHubRepositoryCommits').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getGitHubRepositoryPullRequests').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getGitHubRepositoryContributions').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getGitHubRepositoryTree').mockResolvedValue([]);
    vi.spyOn(apiClient, 'confirmGitHubSkillCandidate').mockResolvedValue({
      ...mockSkills[0],
      status: 'confirmed',
    });
    vi.spyOn(apiClient, 'rejectGitHubCandidate').mockResolvedValue({
      status: 'rejected',
      candidate_id: 'csk_rust_01',
    });
  });

  it('renders the GitHub Intelligence workspace with header and tabs', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      screen.getAllByText('GitHub & Technical Portfolio Intelligence').length
    ).toBeGreaterThan(0);
    expect(screen.getByText(/Stage 22 of 50/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Connected as @octocat/i)).toBeInTheDocument();
    });
  });

  it('displays discovered and analyzed repository counts', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Discovered Repos')).toBeInTheDocument();
      expect(screen.getByText('Analyzed Repos')).toBeInTheDocument();
      expect(screen.getByText('API Rate Limit')).toBeInTheDocument();
    });
  });

  it('switches to Connections tab and displays active connection and DPAPI protection', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const connTabBtn = screen.getByRole('tab', { name: /Connections/i });
    fireEvent.click(connTabBtn);

    await waitFor(() => {
      expect(screen.getByText('The Octocat')).toBeInTheDocument();
      expect(screen.getByText('@octocat')).toBeInTheDocument();
      expect(screen.getAllByText(/DPAPI Encrypted/i).length).toBeGreaterThan(0);
    });
  });

  it('switches to Repositories tab and lists accessible repositories', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const reposTabBtn = screen.getByRole('tab', { name: /Repositories/i });
    fireEvent.click(reposTabBtn);

    await waitFor(() => {
      expect(screen.getByText('octocat/autonom-core')).toBeInTheDocument();
      expect(screen.getByText('octocat/fastapi-service')).toBeInTheDocument();
    });
  });

  it('switches to Candidates tab and allows confirming skill into profile', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const candidatesTabBtn = screen.getByRole('tab', { name: /Review Queue/i });
    fireEvent.click(candidatesTabBtn);

    await waitFor(() => {
      expect(screen.getByText('Human-in-the-Loop Review Queue')).toBeInTheDocument();
      expect(screen.getByText('Rust')).toBeInTheDocument();
      expect(screen.getByText('FastAPI')).toBeInTheDocument();
    });

    const confirmBtns = screen.getAllByRole('button', { name: /Confirm & Add to Profile/i });
    expect(confirmBtns.length).toBeGreaterThan(0);
    fireEvent.click(confirmBtns[0]);

    await waitFor(() => {
      expect(apiClient.confirmGitHubSkillCandidate).toHaveBeenCalledWith(
        'csk_rust_01',
        { profile_id: 'prof_primary_applicant' }
      );
    });
  });

  it('switches to Diagnostics tab and verifies telemetry metrics', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <GitHubPortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const diagTabBtn = screen.getByRole('tab', { name: /Diagnostics/i });
    fireEvent.click(diagTabBtn);

    await waitFor(() => {
      expect(screen.getByText('GitHub Subsystem Diagnostics')).toBeInTheDocument();
      expect(screen.getByText('ETag Cached Entries')).toBeInTheDocument();
      expect(screen.getByText('sjb_test_01')).toBeInTheDocument();
    });
  });
});
