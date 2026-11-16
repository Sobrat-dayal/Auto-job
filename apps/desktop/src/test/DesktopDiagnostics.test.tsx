import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DesktopDiagnostics } from '../pages/DesktopDiagnostics';

vi.mock('@/services/tauri', () => ({
  isTauriEnvironment: vi.fn().mockReturnValue(false),
  getNativeAppInfo: vi.fn().mockResolvedValue({
    name: 'AUTONOM',
    version: '0.1.0-dev',
    tauri_version: '2.0.0-shim',
    os: 'windows',
    arch: 'x86_64',
  }),
  getDesktopStatus: vi.fn().mockResolvedValue({
    app_info: {
      name: 'AUTONOM',
      version: '0.1.0-dev',
      tauri_version: '2.0.0-shim',
      os: 'windows',
      arch: 'x86_64',
    },
    active_tasks_count: 0,
    settings: {
      close_to_tray: true,
      start_at_login: false,
      notifications_enabled: true,
      notify_on_task_completion: true,
      notify_on_backend_events: true,
      window: {
        x: 100,
        y: 100,
        width: 1440,
        height: 900,
        maximized: false,
        selected_module: 'command-center',
      },
    },
  }),
  getBackendProcessStatus: vi.fn().mockResolvedValue({
    state: 'Ready',
    pid: 8765,
    port: 8765,
    uptime_seconds: 120,
    restart_count: 0,
    max_restarts: 5,
    last_error: null,
    backend_mode: 'packaged-sidecar',
    database_ready: true,
  }),
  restartBackendProcess: vi.fn().mockResolvedValue({
    state: 'Ready',
    pid: 8766,
    port: 8765,
    uptime_seconds: 1,
    restart_count: 1,
    max_restarts: 5,
    last_error: null,
    backend_mode: 'packaged-sidecar',
    database_ready: true,
  }),
  updateDesktopSettings: vi.fn().mockResolvedValue({
    close_to_tray: true,
    start_at_login: false,
    notifications_enabled: true,
    notify_on_task_completion: true,
    notify_on_backend_events: true,
    window: {
      x: 100,
      y: 100,
      width: 1440,
      height: 900,
      maximized: false,
      selected_module: 'command-center',
    },
  }),
  testDesktopNotification: vi.fn().mockResolvedValue(true),
  openArtifactLocation: vi.fn().mockResolvedValue(true),
}));

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    getReadiness: vi.fn().mockResolvedValue({
      ready: true,
      status: 'Ready',
      checks: { database: true, workers: true, storage: true },
      timestamp: '2026-11-16T21:00:00Z',
    }),
  },
}));

describe('DesktopDiagnostics Component', () => {
  it('renders desktop shell overview and supervisor controls', async () => {
    render(<DesktopDiagnostics />);

    expect(screen.getByText('Desktop Shell & Process Supervision')).toBeInTheDocument();
    expect(screen.getByText('Stage 05')).toBeInTheDocument();
    expect(screen.getByText('Tauri Native Host')).toBeInTheDocument();
    expect(screen.getByText('Backend Sidecar')).toBeInTheDocument();
    expect(screen.getByText('Job Object Limits')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Ready / Online')).toBeInTheDocument();
      expect(screen.getByText('packaged-sidecar')).toBeInTheDocument();
      expect(screen.getByText('Restart Backend Process')).toBeInTheDocument();
      expect(screen.getByText('Dispatch Toast Notification')).toBeInTheDocument();
    });
  });
});
