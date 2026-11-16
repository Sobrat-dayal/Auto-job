import React, { useEffect, useState } from 'react';
import {
  Monitor,
  Cpu,
  Server,
  Bell,
  RefreshCw,
  FolderOpen,
  Power,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Activity,
  Maximize2,
  ShieldCheck,
} from 'lucide-react';
import type { DesktopStatus, BackendProcessStatus, DesktopSettings } from '@autonom/shared-types';
import {
  getDesktopStatus,
  getBackendProcessStatus,
  restartBackendProcess,
  updateDesktopSettings,
  testDesktopNotification,
  openArtifactLocation,
  isTauriEnvironment,
} from '@/services/tauri';
import { apiClient, BackendReadiness } from '@/lib/api-client';

export const DesktopDiagnostics: React.FC = () => {
  const [desktopStatus, setDesktopStatus] = useState<DesktopStatus | null>(null);
  const [backendProcess, setBackendProcess] = useState<BackendProcessStatus | null>(null);
  const [readiness, setReadiness] = useState<BackendReadiness | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRestarting, setIsRestarting] = useState<boolean>(false);
  const [notificationStatus, setNotificationStatus] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [dStatus, bProc] = await Promise.all([getDesktopStatus(), getBackendProcessStatus()]);
      setDesktopStatus(dStatus);
      setBackendProcess(bProc);

      try {
        const readyData = await apiClient.getReadiness();
        setReadiness(readyData);
      } catch {
        setReadiness(null);
      }
    } catch (err) {
      console.warn('Failed to fetch desktop status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleRestartBackend = async () => {
    setIsRestarting(true);
    setActionMessage('Sending restart command to sidecar supervisor...');
    try {
      const newStatus = await restartBackendProcess();
      setBackendProcess(newStatus);
      setActionMessage('Sidecar restarted successfully.');
      setTimeout(fetchData, 1000);
    } catch (err) {
      setActionMessage(`Restart failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsRestarting(false);
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  const handleTestNotification = async () => {
    setNotificationStatus('Sending test notification...');
    try {
      const success = await testDesktopNotification(
        'AUTONOM Desktop Shell',
        'Windows 11 notification center test successful!'
      );
      if (success) {
        setNotificationStatus('Notification sent successfully.');
      } else {
        setNotificationStatus('Notification request completed.');
      }
    } catch (err) {
      setNotificationStatus(`Failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setTimeout(() => setNotificationStatus(null), 4000);
    }
  };

  const handleSettingToggle = async (key: keyof DesktopSettings, value: boolean) => {
    if (!desktopStatus) return;
    try {
      const updated = await updateDesktopSettings({ [key]: value });
      setDesktopStatus((prev) => (prev ? { ...prev, settings: updated } : null));
    } catch (err) {
      console.error('Failed to update setting:', err);
    }
  };

  const handleOpenFolder = async (folder: string) => {
    setActionMessage(`Opening location: ${folder}`);
    await openArtifactLocation(folder);
    setTimeout(() => setActionMessage(null), 3000);
  };

  const getStatusBadge = (state?: string) => {
    switch (state) {
      case 'Ready':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Ready / Online
          </span>
        );
      case 'Starting':
      case 'Connecting':
      case 'Restarting':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
            {state}...
          </span>
        );
      case 'Failed':
      case 'Degraded':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertTriangle className="w-3 h-3 text-red-400" />
            {state}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            {state || 'Unknown'}
          </span>
        );
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Monitor className="w-6 h-6 text-primary" />
              Desktop Shell & Process Supervision
            </h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-primary/10 text-primary border border-primary/20">
              Stage 05
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Windows 11 desktop integration, Tauri 2 host, Win32 Job Object containment, and sidecar
            supervision.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-surface hover:bg-surface-hover text-slate-200 border border-border rounded transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Action / Notification Banner */}
      {(actionMessage || notificationStatus) && (
        <div className="p-3 bg-primary/10 border border-primary/20 rounded-md text-xs text-primary flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
          <span>{actionMessage || notificationStatus}</span>
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Host App Card */}
        <div className="p-4 bg-surface rounded-lg border border-border flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/50">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Tauri Native Host
            </div>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded border border-border">
              {isTauriEnvironment() ? 'Native Win32' : 'Web Dev'}
            </span>
          </div>
          <div className="space-y-1 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">App Name:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.app_info.name || 'AUTONOM'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">App Version:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.app_info.version || '0.1.0'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Tauri Version:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.app_info.tauri_version || '2.0.0'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Platform:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.app_info.os} ({desktopStatus?.app_info.arch})
              </span>
            </div>
          </div>
        </div>

        {/* Backend Process Card */}
        <div className="p-4 bg-surface rounded-lg border border-border flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/50">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
              <Server className="w-4 h-4 text-primary" />
              Backend Sidecar
            </div>
            {getStatusBadge(backendProcess?.state)}
          </div>
          <div className="space-y-1 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Mode:</span>
              <span
                className="font-mono text-primary text-[11px] truncate max-w-[130px]"
                title={backendProcess?.backend_mode}
              >
                {backendProcess?.backend_mode || 'unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Process ID:</span>
              <span className="font-mono text-slate-200">{backendProcess?.pid ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Port / Host:</span>
              <span className="font-mono text-slate-200">
                127.0.0.1:{backendProcess?.port || 8765}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Uptime:</span>
              <span className="font-mono text-slate-200">
                {backendProcess?.uptime_seconds || 0}s
              </span>
            </div>
          </div>
        </div>

        {/* Process Containment Card */}
        <div className="p-4 bg-surface rounded-lg border border-border flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/50">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Job Object Limits
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/20">
              KILL_ON_CLOSE
            </span>
          </div>
          <div className="space-y-1 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Crash Recovery:</span>
              <span className="text-emerald-400 font-medium">Automatic Backoff</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Restarts:</span>
              <span className="font-mono text-slate-200">
                {backendProcess?.restart_count || 0} / {backendProcess?.max_restarts || 5} max
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Active Tasks:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.active_tasks_count || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">DB Ready:</span>
              <span
                className={`font-medium ${backendProcess?.database_ready ? 'text-emerald-400' : 'text-amber-400'}`}
              >
                {backendProcess?.database_ready ? 'Ready (SQLite WAL)' : 'Connecting'}
              </span>
            </div>
          </div>
        </div>

        {/* Shell Integration Card */}
        <div className="p-4 bg-surface rounded-lg border border-border flex flex-col justify-between">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-border/50">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
              <Layers className="w-4 h-4 text-indigo-400" />
              Native Shell
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 bg-indigo-500/10 text-indigo-400 rounded border border-indigo-500/20">
              Active
            </span>
          </div>
          <div className="space-y-1 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">System Tray:</span>
              <span className="text-emerald-400 font-medium">Initialized</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Single Instance:</span>
              <span className="text-emerald-400 font-medium">Enforced</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Close to Tray:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.settings.close_to_tray ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Notifications:</span>
              <span className="font-mono text-slate-200">
                {desktopStatus?.settings.notifications_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Process Control & Native Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Supervisor Management */}
        <div className="p-5 bg-surface rounded-lg border border-border space-y-4">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2 border-b border-border/50 pb-2">
            <Power className="w-4 h-4 text-primary" />
            Process Supervisor Controls
          </h2>
          <p className="text-xs text-slate-400">
            Manage the background sidecar process lifecycle directly through Tauri Rust command
            bridges.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={handleRestartBackend}
              disabled={isRestarting}
              className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold bg-primary hover:bg-primary-hover text-white rounded-md shadow transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRestarting ? 'animate-spin' : ''}`} />
              {isRestarting ? 'Restarting...' : 'Restart Backend Process'}
            </button>

            <button
              onClick={handleTestNotification}
              className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold bg-surface-hover hover:bg-slate-700 text-slate-200 border border-border rounded-md transition-colors"
            >
              <Bell className="w-3.5 h-3.5 text-amber-400" />
              Dispatch Toast Notification
            </button>
          </div>

          <div className="pt-3 border-t border-border/50 space-y-2">
            <span className="text-xs font-semibold text-slate-300">
              Open Artifact & Configuration Locations:
            </span>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleOpenFolder('data')}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-border rounded transition-colors"
              >
                <FolderOpen className="w-3.5 h-3.5 text-cyan-400" />
                Data Directory (%LOCALAPPDATA%\AUTONOM\data)
              </button>
              <button
                onClick={() => handleOpenFolder('logs')}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-border rounded transition-colors"
              >
                <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
                Logs Directory
              </button>
              <button
                onClick={() => handleOpenFolder('config')}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-border rounded transition-colors"
              >
                <FolderOpen className="w-3.5 h-3.5 text-indigo-400" />
                Config Directory
              </button>
            </div>
          </div>
        </div>

        {/* Desktop Preferences */}
        <div className="p-5 bg-surface rounded-lg border border-border space-y-4">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2 border-b border-border/50 pb-2">
            <Maximize2 className="w-4 h-4 text-cyan-400" />
            Native Preferences & Window Management
          </h2>
          <p className="text-xs text-slate-400">
            Saved to{' '}
            <code className="text-slate-300 bg-slate-800 px-1 py-0.5 rounded text-[11px]">
              %LOCALAPPDATA%\AUTONOM\config\desktop_settings.json
            </code>
            .
          </p>

          <div className="space-y-3 pt-1">
            <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
              <span>Close to System Tray (Keep running in background)</span>
              <input
                type="checkbox"
                checked={desktopStatus?.settings.close_to_tray ?? true}
                onChange={(e) => handleSettingToggle('close_to_tray', e.target.checked)}
                className="rounded border-border text-primary focus:ring-primary h-4 w-4 bg-slate-900"
              />
            </label>

            <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
              <span>Launch AUTONOM on Windows Startup</span>
              <input
                type="checkbox"
                checked={desktopStatus?.settings.start_at_login ?? false}
                onChange={(e) => handleSettingToggle('start_at_login', e.target.checked)}
                className="rounded border-border text-primary focus:ring-primary h-4 w-4 bg-slate-900"
              />
            </label>

            <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
              <span>Enable Native Desktop Notifications</span>
              <input
                type="checkbox"
                checked={desktopStatus?.settings.notifications_enabled ?? true}
                onChange={(e) => handleSettingToggle('notifications_enabled', e.target.checked)}
                className="rounded border-border text-primary focus:ring-primary h-4 w-4 bg-slate-900"
              />
            </label>

            <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
              <span>Notify upon Long-Running Task Completion</span>
              <input
                type="checkbox"
                checked={desktopStatus?.settings.notify_on_task_completion ?? true}
                onChange={(e) => handleSettingToggle('notify_on_task_completion', e.target.checked)}
                className="rounded border-border text-primary focus:ring-primary h-4 w-4 bg-slate-900"
              />
            </label>

            <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
              <span>Notify upon Backend Supervisor Events</span>
              <input
                type="checkbox"
                checked={desktopStatus?.settings.notify_on_backend_events ?? true}
                onChange={(e) => handleSettingToggle('notify_on_backend_events', e.target.checked)}
                className="rounded border-border text-primary focus:ring-primary h-4 w-4 bg-slate-900"
              />
            </label>
          </div>

          <div className="pt-2 border-t border-border/50 text-[11px] text-slate-400 flex items-center justify-between font-mono">
            <span>Saved Geometry:</span>
            <span>
              {desktopStatus?.settings.window.width}x{desktopStatus?.settings.window.height} at (
              {desktopStatus?.settings.window.x},{desktopStatus?.settings.window.y})
            </span>
          </div>
        </div>
      </div>

      {/* Backend Readiness & Health Diagnostics */}
      <div className="p-5 bg-surface rounded-lg border border-border space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2 border-b border-border/50 pb-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          Backend Readiness Diagnostics
        </h2>

        {readiness ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            <div className="p-3 bg-slate-900/60 rounded border border-border/60">
              <span className="text-xs text-slate-400 block mb-1">Overall Status:</span>
              <span
                className={`text-sm font-semibold ${readiness.ready ? 'text-emerald-400' : 'text-amber-400'}`}
              >
                {readiness.status}
              </span>
            </div>

            <div className="p-3 bg-slate-900/60 rounded border border-border/60">
              <span className="text-xs text-slate-400 block mb-1">Subsystem Checks:</span>
              <div className="space-y-1">
                {Object.entries(readiness.checks).map(([name, pass]) => (
                  <div key={name} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-300">{name}:</span>
                    <span
                      className={
                        pass ? 'text-emerald-400 font-semibold' : 'text-red-400 font-semibold'
                      }
                    >
                      {pass ? 'PASS' : 'FAIL'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 bg-slate-900/60 rounded border border-border/60">
              <span className="text-xs text-slate-400 block mb-1">Supervisor Error State:</span>
              <span className="text-xs font-mono text-slate-300 break-words">
                {backendProcess?.last_error || 'None (Healthy)'}
              </span>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded text-xs text-amber-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
            Backend readiness endpoint is currently unreachable or initializing.
          </div>
        )}
      </div>
    </div>
  );
};
