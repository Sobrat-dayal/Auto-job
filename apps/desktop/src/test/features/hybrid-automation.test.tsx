import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  HybridDiagnosticsInfo,
  MethodHealthStatus,
  RoutingDecisionRecord,
  HybridTaskResponse,
} from '@autonom/shared-types';

describe('Hybrid Automation Workspace (Stage 19)', () => {
  let queryClient: QueryClient;

  const mockMethods: MethodHealthStatus[] = [
    {
      method: 'BROWSER_DOM',
      status: 'AVAILABLE',
      success_count: 42,
      failure_count: 1,
      avg_latency_ms: 12.5,
      last_used_at: new Date().toISOString(),
    },
    {
      method: 'WINDOWS_UIA',
      status: 'AVAILABLE',
      success_count: 38,
      failure_count: 2,
      avg_latency_ms: 24.1,
      last_used_at: new Date().toISOString(),
    },
    {
      method: 'WINDOWS_WIN32',
      status: 'AVAILABLE',
      success_count: 15,
      failure_count: 0,
      avg_latency_ms: 8.3,
      last_used_at: new Date().toISOString(),
    },
    {
      method: 'VISUAL_GROUNDING',
      status: 'AVAILABLE',
      success_count: 22,
      failure_count: 3,
      avg_latency_ms: 85.0,
      last_used_at: new Date().toISOString(),
    },
  ];

  const mockDecisions: RoutingDecisionRecord[] = [
    {
      decision_id: 'dec_test_001',
      task_id: 'task_hyb_001',
      target_id: 'tgt_btn_submit',
      selected_method: 'BROWSER_DOM',
      candidate_methods: ['BROWSER_DOM', 'VISUAL_GROUNDING'],
      rejected_methods: {
        WINDOWS_UIA: 'Target is not a native Windows window or control',
        WINDOWS_WIN32: 'HWND missing or inaccessible',
      },
      scoring: {
        BROWSER_DOM: 98.5,
        VISUAL_GROUNDING: 64.0,
      },
      rationale: 'Primary browser DOM target matched with 0.98 confidence',
      decided_at: new Date().toISOString(),
    },
  ];

  const mockTasks: HybridTaskResponse[] = [
    {
      task_id: 'task_hyb_001',
      status: 'completed',
      instruction: 'Click Submit Application button',
      selected_method: 'BROWSER_DOM',
      routing_decision: mockDecisions[0],
      attempts: [
        {
          attempt_index: 0,
          method: 'BROWSER_DOM',
          success: true,
          execution_time_ms: 14.2,
          verification_status: 'success',
        },
      ],
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    },
  ];

  const mockDiagnostics: HybridDiagnosticsInfo = {
    engine_version: '1.0.0',
    is_healthy: true,
    emergency_stop_active: false,
    input_lease_owner: null,
    methods: mockMethods,
    total_tasks: 117,
    active_tasks: 0,
    total_fallbacks: 4,
    recent_routing_decisions: mockDecisions,
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getHybridDiagnostics').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'listHybridMethods').mockResolvedValue(mockMethods.map((m) => m.method));
    vi.spyOn(apiClient, 'listHybridTasks').mockResolvedValue(mockTasks);
    vi.spyOn(apiClient, 'listBrowserSessions').mockResolvedValue([]);
    vi.spyOn(apiClient, 'listDesktopWindows').mockResolvedValue([
      {
        window_ref: 'win_mock_001',
        hwnd: 1024,
        pid: 4096,
        process_name: 'chrome.exe',
        title: 'AUTONOM Desktop Portal',
        window_class: 'Chrome_WidgetWin_1',
        is_visible: true,
        is_enabled: true,
        is_foreground: true,
        is_minimized: false,
        is_maximized: false,
        bounds: { left: 0, top: 0, right: 1280, bottom: 800, width: 1280, height: 800 },
        created_at: new Date().toISOString(),
      },
    ]);
    vi.spyOn(apiClient, 'listVisualSessions').mockResolvedValue([
      {
        session_id: 'vsess_001',
        target_type: 'display',
        display_index: 0,
        provider: 'mss',
        state: 'capturing',
        frame_rate_limit: 30,
        frames_captured: 140,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);
    vi.spyOn(apiClient, 'previewHybridRoute').mockResolvedValue(mockDecisions[0]);
    vi.spyOn(apiClient, 'activateHybridKillswitch').mockResolvedValue({ status: 'active', reason: 'test' });
    vi.spyOn(apiClient, 'deactivateHybridKillswitch').mockResolvedValue({ status: 'deactivated' });
    vi.spyOn(apiClient, 'submitHybridTask').mockResolvedValue(mockTasks[0]);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer/hybrid']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders Hybrid Computer Engine workspace and overview metrics', async () => {
    renderComponent();

    expect(screen.getByText('Computer Control & Automation')).toBeInTheDocument();
    expect(screen.getByText('Stage 19 Production Active')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Hybrid Interaction Engine')).toBeInTheDocument();
    });

    expect(screen.getByText('Context Fallbacks')).toBeInTheDocument();
    expect(screen.getByText('Active Tasks')).toBeInTheDocument();
  });

  it('renders Capability Matrix tab showing all four interaction methods', async () => {
    renderComponent();

    const matrixTabButton = screen.getByRole('button', { name: /Capability Matrix/i });
    fireEvent.click(matrixTabButton);

    await waitFor(() => {
      expect(screen.getByText('Cross-Method Capability & Fallback Matrix')).toBeInTheDocument();
      expect(screen.getByText('Browser DOM')).toBeInTheDocument();
      expect(screen.getByText('Windows UIA')).toBeInTheDocument();
      expect(screen.getByText('Win32')).toBeInTheDocument();
      expect(screen.getByText('Visual Grounding')).toBeInTheDocument();
    });
  });

  it('renders Routing Inspector and simulates route preview calculation', async () => {
    renderComponent();

    const routingTabButton = screen.getByRole('button', { name: /Routing Inspector/i });
    fireEvent.click(routingTabButton);

    await waitFor(() => {
      expect(screen.getByText('Routing Policy Simulator')).toBeInTheDocument();
    });

    const previewButton = screen.getByRole('button', { name: /Preview Routing Decision/i });
    fireEvent.click(previewButton);

    await waitFor(() => {
      expect(apiClient.previewHybridRoute).toHaveBeenCalled();
      expect(screen.getByText(/Selected: BROWSER_DOM/i)).toBeInTheDocument();
      expect(screen.getByText(/Primary browser DOM target matched/i)).toBeInTheDocument();
    });
  });

  it('renders Unified Sessions tab showing cross-method telemetry', async () => {
    renderComponent();

    const sessionsTabButton = screen.getByRole('button', { name: /Unified Sessions/i });
    fireEvent.click(sessionsTabButton);

    await waitFor(() => {
      expect(screen.getByText('Cross-Method Input Ownership Lease')).toBeInTheDocument();
      expect(screen.getByText('AUTONOM Desktop Portal')).toBeInTheDocument();
      expect(screen.getByText('Stream')).toBeInTheDocument();
      expect(screen.getByText('mss')).toBeInTheDocument();
    });
  });

  it('renders Hybrid Tasks tab showing task history and dispatch form', async () => {
    renderComponent();

    const tasksTabButton = screen.getByRole('button', { name: /Hybrid Tasks/i });
    fireEvent.click(tasksTabButton);

    await waitFor(() => {
      expect(screen.getByText('Dispatch Hybrid Computer Task')).toBeInTheDocument();
      expect(screen.getByText('Execution History')).toBeInTheDocument();
      expect(screen.getAllByText('Click Submit Application button').length).toBeGreaterThan(0);
      expect(screen.getAllByText('completed').length).toBeGreaterThan(0);
    });
  });

  it('renders Diagnostics tab and audits routing decision history', async () => {
    renderComponent();

    const diagTabButton = screen.getByRole('button', { name: /Diagnostics & Audit/i });
    fireEvent.click(diagTabButton);

    await waitFor(() => {
      expect(screen.getByText('Hybrid Engine Telemetry & System Diagnostics')).toBeInTheDocument();
      expect(screen.getByText(/1\.0\.0/)).toBeInTheDocument();
      expect(screen.getByText('dec_test_001')).toBeInTheDocument();
    });
  });

  it('triggers emergency hybrid killswitch when clicked', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Hybrid Interaction Engine')).toBeInTheDocument();
    });

    const killswitchBtn = screen.getByRole('button', { name: /^Emergency Stop$/i });
    fireEvent.click(killswitchBtn);

    await waitFor(() => {
      expect(apiClient.activateHybridKillswitch).toHaveBeenCalled();
    });
  });
});
