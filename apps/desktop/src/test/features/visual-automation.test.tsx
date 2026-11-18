import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  DisplayInfo,
  VisualActionResult,
  VisualDiagnosticsInfo,
  VisualGroundingResult,
} from '@autonom/shared-types';

describe('Visual Automation Workspace (Stage 18)', () => {
  let queryClient: QueryClient;

  const mockDiagnostics: VisualDiagnosticsInfo = {
    active_provider: 'mss',
    available_providers: ['mss', 'gdi', 'wgc'],
    active_sessions_count: 1,
    monitors_count: 1,
    primary_display_resolution: '1920x1080',
    dpi_scaling_factor: 1.0,
    offline_windows_ocr_available: true,
    vlm_grounding_available: true,
    gpu_acceleration: true,
    last_capture_latency_ms: 15.2,
    last_ocr_latency_ms: 42.1,
    active_emergency_stop: false,
  };

  const mockMonitors: DisplayInfo[] = [
    {
      display_index: 0,
      name: '\\\\.\\DISPLAY1',
      width: 1920,
      height: 1080,
      left: 0,
      top: 0,
      right: 1920,
      bottom: 1080,
      is_primary: true,
      scale_factor: 1.0,
      dpi: 96,
    },
  ];

  const mockGroundingResult: VisualGroundingResult = {
    success: true,
    query: 'Start button',
    target_point: { x: 30, y: 1050 },
    bounding_box: { left: 10, top: 1030, width: 40, height: 40 },
    category: 'button',
    confidence: 0.95,
    explanation: 'Matched Windows Start button in taskbar via visual bounding box and OCR icon heuristic',
  };

  const mockActionResult: VisualActionResult = {
    success: true,
    action_type: 'click',
    execution_time_ms: 4.8,
    verification_status: 'verified',
    visual_difference: 0.082,
    verification_notes: 'Visual state change confirmed with 8.2% pixel difference',
    post_action_frame_id: 'frame_post_1',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getVisualDiagnostics').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'listVisualMonitors').mockResolvedValue(mockMonitors);
    vi.spyOn(apiClient, 'createVisualSession').mockResolvedValue({
      session_id: 'vsess_mock_1',
      target_type: 'display',
      display_index: 0,
      provider: 'mss',
      state: 'capturing',
      frame_rate_limit: 5.0,
      frames_captured: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
    vi.spyOn(apiClient, 'closeVisualSession').mockResolvedValue({ session_id: 'vsess_mock_1', closed: true });
    vi.spyOn(apiClient, 'captureVisualFrame').mockResolvedValue({
      frame_id: 'vframe_1',
      session_id: 'vsess_mock_1',
      metadata: { width: 1920, height: 1080, dpi_scale: 1.0, content_hash: 'abc123hash' },
      thumbnail_b64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    });
    vi.spyOn(apiClient, 'groundVisualQuery').mockResolvedValue(mockGroundingResult);
    vi.spyOn(apiClient, 'quickVisualClick').mockResolvedValue(mockActionResult);
    vi.spyOn(apiClient, 'listVisualTasks').mockResolvedValue([]);
    vi.spyOn(apiClient, 'listVisualRecoveryEvents').mockResolvedValue([]);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer/visual']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders ComputerWorkspace with Stage 18 active indicators', async () => {
    renderComponent();

    expect(screen.getByText('Computer Control & Automation')).toBeInTheDocument();
    expect(screen.getByText('Stage 18 Production Active')).toBeInTheDocument();
    expect(screen.getByText('Visual Engine: Operational')).toBeInTheDocument();
  });

  it('renders Visual Overview metrics and OCR status', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Connected Displays')).toBeInTheDocument();
      expect(screen.getByText('Windows Media OCR')).toBeInTheDocument();
      expect(screen.getByText('100% Offline')).toBeInTheDocument();
    });
  });

  it('allows entering a visual grounding query and displays target point', async () => {
    renderComponent();

    const input = await screen.findByPlaceholderText(/Find visual UI element/i);
    fireEvent.change(input, { target: { value: 'Start button' } });

    const groundBtn = screen.getByRole('button', { name: /Ground Element/i });
    fireEvent.click(groundBtn);

    await waitFor(() => {
      expect(screen.getByText(/Grounded Successfully/i)).toBeInTheDocument();
      expect(screen.getByText(/Matched Windows Start button/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Click \(30, 1050\)/i })).toBeInTheDocument();
    });
  });

  it('executes click on grounded target with verification badge', async () => {
    renderComponent();

    const input = await screen.findByPlaceholderText(/Find visual UI element/i);
    fireEvent.change(input, { target: { value: 'Start button' } });
    fireEvent.click(screen.getByRole('button', { name: /Ground Element/i }));

    const clickBtn = await screen.findByRole('button', { name: /Click \(30, 1050\)/i });
    fireEvent.click(clickBtn);

    await waitFor(() => {
      expect(screen.getByText(/Action Executed \(click\)/i)).toBeInTheDocument();
    });
  });

  it('navigates through visual subtabs', async () => {
    renderComponent();

    // Click Screen Perception & Capture subtab
    const captureTabBtn = await screen.findByRole('tab', { name: /Screen Perception & Capture/i });
    fireEvent.click(captureTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Capture Target & Engine Configuration/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Capture Snapshot/i })).toBeInTheDocument();
    });

    // Click Actions & Verification subtab
    const actionsTabBtn = screen.getByRole('tab', { name: /Actions & Verification/i });
    fireEvent.click(actionsTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Coordinate-Based Input Dispatcher & Visual Action Verifier/i)).toBeInTheDocument();
    });
  });
});
