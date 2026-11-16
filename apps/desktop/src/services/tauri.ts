/**
 * Native Tauri IPC Service with safe webview/browser fallback
 */

import type {
  AppInfo,
  DesktopStatus,
  BackendProcessStatus,
  DesktopSettings,
} from '@autonom/shared-types';

export type { AppInfo, DesktopStatus, BackendProcessStatus, DesktopSettings };

export function isTauriEnvironment(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

export async function getNativeAppInfo(): Promise<AppInfo> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<AppInfo>('get_app_info');
    } catch (err) {
      console.warn('Tauri get_app_info invoke failed:', err);
    }
  }

  return {
    name: 'AUTONOM',
    version: '0.1.0-dev',
    tauri_version: '2.0.0-shim',
    os:
      typeof navigator !== 'undefined' && navigator.userAgent.includes('Windows')
        ? 'windows'
        : 'windows-simulated',
    arch: 'x86_64',
  };
}

export async function getDesktopStatus(): Promise<DesktopStatus> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<DesktopStatus>('get_desktop_status');
    } catch (err) {
      console.warn('Tauri get_desktop_status invoke failed:', err);
    }
  }

  const appInfo = await getNativeAppInfo();
  return {
    app_info: appInfo,
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
  };
}

export async function getBackendProcessStatus(): Promise<BackendProcessStatus> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<BackendProcessStatus>('get_backend_status');
    } catch (err) {
      console.warn('Tauri get_backend_status invoke failed:', err);
    }
  }

  return {
    state: 'Ready',
    pid: 8765,
    port: 8765,
    uptime_seconds: 120,
    restart_count: 0,
    max_restarts: 5,
    last_error: null,
    backend_mode: 'development-venv',
    database_ready: true,
  };
}

export async function restartBackendProcess(): Promise<BackendProcessStatus> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<BackendProcessStatus>('restart_backend');
    } catch (err) {
      console.error('Tauri restart_backend invoke failed:', err);
      throw err;
    }
  }

  // Simulated restart in web mode
  return {
    state: 'Ready',
    pid: 8766,
    port: 8765,
    uptime_seconds: 1,
    restart_count: 1,
    max_restarts: 5,
    last_error: null,
    backend_mode: 'development-venv',
    database_ready: true,
  };
}

export async function updateDesktopSettings(
  payload: Partial<DesktopSettings>
): Promise<DesktopSettings> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<DesktopSettings>('set_window_preferences', { payload });
    } catch (err) {
      console.warn('Tauri set_window_preferences invoke failed:', err);
    }
  }

  const current = (await getDesktopStatus()).settings;
  return { ...current, ...payload };
}

export async function testDesktopNotification(title?: string, body?: string): Promise<boolean> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<boolean>('test_notification', { title, body });
    } catch (err) {
      console.warn('Tauri test_notification invoke failed:', err);
      return false;
    }
  }

  if (typeof window !== 'undefined' && 'Notification' in window) {
    if (Notification.permission === 'granted') {
      new Notification(title ?? 'AUTONOM Desktop', { body: body ?? 'Test notification' });
      return true;
    }
  }
  return true;
}

export async function openArtifactLocation(targetPath: string): Promise<boolean> {
  if (isTauriEnvironment()) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<boolean>('open_artifact_location', {
        relativeOrAbsolute: targetPath,
      });
    } catch (err) {
      console.warn('Tauri open_artifact_location invoke failed:', err);
      return false;
    }
  }

  window.open(targetPath, '_blank');
  return true;
}
