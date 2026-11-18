import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';
import { apiClient } from '@/lib/api-client';

describe('Desktop Automation Workspace (Stage 17)', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    const mockSession = {
      wts_session_id: 1,
      status: 'active' as any,
      desktop_name: 'Default',
      user_name: 'TestUser',
      resolution: '2560x1440',
      is_interactive: true,
      is_locked: false,
      last_active_at: new Date().toISOString(),
    };

    const mockDiagnostics = {
      session: mockSession,
      uia_available: true,
      win32_available: true,
      active_worker_threads: 1,
      cached_windows: 12,
      registered_applications: 5,
      emergency_stop_active: false,
      diagnostic_timestamp: new Date().toISOString(),
    };

    vi.spyOn(apiClient, 'getDesktopStatus').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'getDesktopDiagnostics').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'getDesktopSession').mockResolvedValue(mockSession);

    vi.spyOn(apiClient, 'listDesktopApplications').mockResolvedValue([
      {
        id: 'app_1',
        name: 'Notepad',
        executable_path: 'C:\\Windows\\System32\\notepad.exe',
        executable_name: 'notepad.exe',
        publisher: 'Microsoft Corporation',
        is_allowed: true,
        risk_level: 'LOW',
        integrity_level: 'medium',
        pids: [1024],
        window_count: 1,
        last_detected_at: new Date().toISOString(),
      },
      {
        id: 'app_2',
        name: 'Windows Terminal',
        executable_path: 'C:\\Program Files\\WindowsApps\\wt.exe',
        executable_name: 'windowsterminal.exe',
        publisher: 'Microsoft Corporation',
        is_allowed: true,
        risk_level: 'LOW',
        integrity_level: 'medium',
        pids: [2048],
        window_count: 1,
        last_detected_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'listDesktopWindows').mockResolvedValue([
      {
        window_ref: 'win_1234_1024',
        hwnd: 1234,
        pid: 1024,
        process_name: 'notepad.exe',
        title: 'Untitled - Notepad',
        window_class: 'Notepad',
        is_visible: true,
        is_enabled: true,
        is_foreground: true,
        is_minimized: false,
        is_maximized: false,
        bounds: { left: 100, top: 100, right: 900, bottom: 700, width: 800, height: 600 },
        created_at: new Date().toISOString(),
        last_inspected_at: null,
      },
    ]);

    vi.spyOn(apiClient, 'inspectDesktopTree').mockResolvedValue({
      window_ref: 'win_1234_1024',
      title: 'Untitled - Notepad',
      root: {
        element: {
          element_ref: 'el_0',
          window_ref: 'win_1234_1024',
          name: 'Untitled - Notepad',
          automation_id: 'TitleBar',
          control_type: 'Window',
          control_type_id: 50032,
          class_name: 'Notepad',
          framework_id: 'Win32',
          is_enabled: true,
          is_offscreen: false,
          has_keyboard_focus: false,
          bounding_box: { left: 100, top: 100, right: 900, bottom: 700, width: 800, height: 600 },
          supported_patterns: ['window', 'transform'],
          value: null,
          toggle_state: null,
          parent_ref: null,
        },
        children: [
          {
            element: {
              element_ref: 'el_1',
              window_ref: 'win_1234_1024',
              name: 'Text Editor',
              automation_id: '15',
              control_type: 'Edit',
              control_type_id: 50004,
              class_name: 'Edit',
              framework_id: 'Win32',
              is_enabled: true,
              is_offscreen: false,
              has_keyboard_focus: true,
              bounding_box: { left: 100, top: 150, right: 900, bottom: 700, width: 800, height: 550 },
              supported_patterns: ['value', 'text'],
              value: 'Hello AUTONOM',
              toggle_state: null,
              parent_ref: 'el_0',
            },
            children: [],
          },
        ],
      },
      total_nodes: 2,
      max_depth_reached: 1,
      is_truncated: false,
      estimated_tokens: 150,
      inspected_at: new Date().toISOString(),
    });

    vi.spyOn(apiClient, 'listDesktopTasks').mockResolvedValue([]);
    vi.spyOn(apiClient, 'listDesktopActions').mockResolvedValue([]);
  });

  it('renders Desktop Overview Tab with session telemetry and allowlist stats', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Header checks
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Computer Control & Automation');
    expect(screen.getByText('Stage 17 Production Active')).toBeInTheDocument();

    // Session telemetry loaded
    await waitFor(() => {
      expect(screen.getByText(/2560x1440/)).toBeInTheDocument();
      expect(screen.getByText(/Interactive Default Desktop/)).toBeInTheDocument();
      expect(screen.getByText(/TestUser/)).toBeInTheDocument();
    });
  });

  it('navigates to Applications Tab and lists discovered processes', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Click Applications tab
    const appsTab = screen.getByRole('button', { name: /Applications/i });
    fireEvent.click(appsTab);

    await waitFor(() => {
      expect(screen.getByText('notepad.exe')).toBeInTheDocument();
      expect(screen.getByText('windowsterminal.exe')).toBeInTheDocument();
    });
  });

  it('navigates to Windows Tab and shows active top-level windows', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Click Windows tab
    const windowsTab = screen.getByRole('button', { name: /Windows/i });
    fireEvent.click(windowsTab);

    await waitFor(() => {
      expect(screen.getByText('Untitled - Notepad')).toBeInTheDocument();
      expect(screen.getByText('win_1234_1024')).toBeInTheDocument();
      expect(screen.getByText('800x600')).toBeInTheDocument();
    });
  });
});
