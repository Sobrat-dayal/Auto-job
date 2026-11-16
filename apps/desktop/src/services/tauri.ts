/**
 * Native Tauri IPC Service with safe webview/browser fallback
 */

export interface AppInfo {
  name: string;
  version: string;
  tauri_version: string;
  os: string;
  arch: string;
}

export async function getNativeAppInfo(): Promise<AppInfo> {
  // Check if running within a Tauri desktop runtime
  if (typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window) {
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke<AppInfo>('get_app_info');
    } catch (err) {
      console.warn('Tauri invoke failed:', err);
    }
  }

  // Fallback for Vite web browser development
  return {
    name: 'AUTONOM (Web Dev Mode)',
    version: '0.1.0-dev',
    tauri_version: '2.0.0-shim',
    os: navigator.userAgent.includes('Windows') ? 'Windows (Simulated)' : navigator.platform,
    arch: 'x86_64',
  };
}
