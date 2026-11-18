import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';
import { apiClient } from '@/lib/api-client';

describe('Browser Automation Workspace (Stage 16)', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getBrowserRuntimeStatus').mockResolvedValue({
      playwright_available: true,
      installed_browsers: ['chromium', 'msedge', 'chrome'],
      system_browsers_detected: ['msedge', 'chrome'],
      active_sessions_count: 1,
      max_concurrent_sessions: 5,
      default_headless: true,
      downloads_dir: 'C:/AppData/AUTONOM/downloads',
      screenshots_dir: 'C:/AppData/AUTONOM/screenshots',
    });

    vi.spyOn(apiClient, 'listBrowserSessions').mockResolvedValue([
      {
        id: 'sess_prod_12345678',
        browser_type: 'chromium',
        channel: null,
        status: 'running',
        is_headless: true,
        active_tab_id: 'tab_1',
        tab_count: 1,
        current_url: 'https://boards.greenhouse.io/demo/jobs/100',
        current_title: 'Senior Software Engineer',
        created_at: new Date().toISOString(),
        last_activity_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'getBrowserSession').mockResolvedValue({
      id: 'sess_prod_12345678',
      profile_id: null,
      browser_type: 'chromium',
      channel: null,
      status: 'running',
      is_headless: true,
      active_tab_id: 'tab_1',
      pid: 14500,
      viewport_width: 1280,
      viewport_height: 800,
      user_agent: 'AUTONOM-Browser/1.0',
      locale: 'en-US',
      timezone_id: 'America/New_York',
      created_at: new Date().toISOString(),
      last_activity_at: new Date().toISOString(),
      closed_at: null,
      error_message: null,
      metadata: {},
      tabs: [
        {
          id: 'tab_1',
          session_id: 'sess_prod_12345678',
          tab_index: 0,
          title: 'Senior Software Engineer',
          url: 'https://boards.greenhouse.io/demo/jobs/100',
          status: 'ready',
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          closed_at: null,
        },
      ],
    });

    vi.spyOn(apiClient, 'listBrowserProfiles').mockResolvedValue([
      {
        id: 'prof_default',
        name: 'Default Recruiter Profile',
        description: 'Persistent profile for job boards',
        storage_path: 'C:/AppData/AUTONOM/profiles/prof_default.enc',
        is_authenticated: true,
        domain_scopes: ['linkedin.com', 'greenhouse.io'],
        last_used_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'listBrowserDownloads').mockResolvedValue([
      {
        id: 'dl_sample_1',
        session_id: 'sess_prod_12345678',
        tab_id: 'tab_1',
        suggested_filename: 'job_spec.pdf',
        destination_path: 'C:/AppData/AUTONOM/downloads/job_spec.pdf',
        file_size_bytes: 1048576,
        sha256_checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        mime_type: 'application/pdf',
        source_url: 'https://boards.greenhouse.io/download/spec',
        status: 'completed',
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        error_message: null,
      },
    ]);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer/browser']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders Browser Automation overview with telemetry and active engines', async () => {
    renderComponent();

    expect(screen.getByText('Computer Control & Automation')).toBeDefined();
    expect(screen.getByText('Stage 17 Production Active')).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText('Operational')).toBeDefined();
      expect(screen.getByText('3 Engines')).toBeDefined();
      expect(screen.getByText('Stage 14 Gate')).toBeDefined();
    });

    expect(screen.getByText('Launch Browser Session')).toBeDefined();
    expect(screen.getByText('sess_pro')).toBeDefined();
  });

  it('switches to Live Controller tab and displays session controls', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Live Controller & Canvas')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Live Controller & Canvas'));

    await waitFor(() => {
      expect(screen.getByText('Navigate')).toBeDefined();
      expect(screen.getByText('Live Page Viewport')).toBeDefined();
      expect(screen.getByText('Dispatch Click Action')).toBeDefined();
      expect(screen.getByText('Dispatch Fill Action')).toBeDefined();
    });
  });

  it('switches to DOM Inspector tab and shows structured inspection triggers', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('DOM & Form Inspector')).toBeDefined();
    });

    fireEvent.click(screen.getByText('DOM & Form Inspector'));

    await waitFor(() => {
      expect(screen.getByText('Structured DOM & Accessibility Inspector')).toBeDefined();
      expect(screen.getByText('Inspect Live Page')).toBeDefined();
    });
  });

  it('switches to Downloads tab and displays SHA-256 integrity records', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Downloads & Artifacts')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Downloads & Artifacts'));

    await waitFor(() => {
      expect(screen.getByText('job_spec.pdf')).toBeDefined();
      expect(screen.getByText(/SHA-256:/)).toBeDefined();
      expect(screen.getByText('1 MB')).toBeDefined();
    });
  });

  it('switches to Profiles & Vault tab and shows authenticated profiles', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Profiles & Vault')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Profiles & Vault'));

    await waitFor(() => {
      expect(screen.getByText('Default Recruiter Profile')).toBeDefined();
      expect(screen.getByText('Authenticated')).toBeDefined();
      expect(screen.getByText('linkedin.com')).toBeDefined();
    });
  });
});
