import React, { useEffect, useState } from 'react';
import {
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
import { PageContainer } from '@/components/layout/PageContainer';
import { SectionHeader } from '@/components/layout/SectionHeader';
import { MetricCard } from '@/components/data-display/MetricCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';

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

  const renderProcessStatusBadge = (state?: string) => {
    switch (state) {
      case 'Ready':
        return (
          <Badge variant="success" dot pulse>
            Ready / Online
          </Badge>
        );
      case 'Starting':
      case 'Connecting':
      case 'Restarting':
        return (
          <Badge variant="warning" dot pulse>
            {state}...
          </Badge>
        );
      case 'Failed':
      case 'Degraded':
        return (
          <Badge variant="error" dot>
            {state}
          </Badge>
        );
      default:
        return <Badge variant="neutral">{state || 'Unknown'}</Badge>;
    }
  };

  return (
    <PageContainer
      title="Desktop Shell & Process Supervision"
      subtitle="Windows 11 desktop integration, Tauri 2 host, Win32 Job Object containment, and sidecar supervision"
      badge={
        <Badge variant="cyan" dot>
          Stage 05
        </Badge>
      }
      actions={
        <Button
          variant="outline"
          size="sm"
          onClick={fetchData}
          disabled={isLoading}
          isLoading={isLoading}
          loadingText="Refreshing..."
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh
        </Button>
      }
    >
      {/* Action / Notification Banner */}
      {(actionMessage || notificationStatus) && (
        <div className="p-3 bg-surface border border-primary/40 rounded-lg text-xs font-mono-tech text-cyan flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
          <span>{actionMessage || notificationStatus}</span>
        </div>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <MetricCard
          title="Tauri Native Host"
          value={isTauriEnvironment() ? 'Native Win32' : 'Web Dev'}
          subtitle={
            desktopStatus?.app_info
              ? `${desktopStatus.app_info.os} (${desktopStatus.app_info.arch})`
              : 'Windows x64'
          }
          icon={<Cpu className="w-4 h-4" />}
          variant="cyan"
        />

        <MetricCard
          title="Backend Sidecar"
          value={renderProcessStatusBadge(backendProcess?.state)}
          subtitle={
            <span>
              Mode:{' '}
              <span className="font-mono-tech">{backendProcess?.backend_mode || 'unknown'}</span>{' '}
              (Port {backendProcess?.port || 8765})
            </span>
          }
          icon={<Server className="w-4 h-4" />}
          variant={backendProcess?.state === 'Ready' ? 'success' : 'default'}
        />

        <MetricCard
          title="Job Object Limits"
          value="KILL_ON_CLOSE"
          subtitle={`Restarts: ${backendProcess?.restart_count || 0}/${backendProcess?.max_restarts || 5} max`}
          icon={<ShieldCheck className="w-4 h-4" />}
          variant="primary"
        />

        <MetricCard
          title="Native Integration"
          value={desktopStatus?.settings.close_to_tray ? 'Tray Enabled' : 'Standard'}
          subtitle={`Active Tasks: ${desktopStatus?.active_tasks_count || 0}`}
          icon={<Layers className="w-4 h-4" />}
          variant="default"
        />
      </div>

      {/* Process Control & Native Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Supervisor Management */}
        <div className="p-4 bg-surface rounded-lg border border-border space-y-4">
          <SectionHeader
            title="Process Supervisor Controls"
            subtitle="Manage the background sidecar process lifecycle directly through Tauri Rust command bridges"
            icon={<Power className="w-4 h-4 text-primary" />}
          />

          <div className="flex flex-wrap gap-2.5 pt-1">
            <Button
              variant="primary"
              size="sm"
              onClick={handleRestartBackend}
              disabled={isRestarting}
              isLoading={isRestarting}
              loadingText="Restarting..."
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Restart Backend Process
            </Button>

            <Button variant="outline" size="sm" onClick={handleTestNotification}>
              <Bell className="w-3.5 h-3.5 mr-1.5 text-status-warning" />
              Dispatch Toast Notification
            </Button>
          </div>

          <div className="pt-3 border-t border-border space-y-2">
            <span className="text-xs font-semibold text-foreground-secondary">
              Open Artifact & Configuration Locations:
            </span>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleOpenFolder('data')}
                className="text-[11px]"
              >
                <FolderOpen className="w-3.5 h-3.5 mr-1.5 text-cyan" />
                Data Directory (%LOCALAPPDATA%\AUTONOM\data)
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleOpenFolder('logs')}
                className="text-[11px]"
              >
                <FolderOpen className="w-3.5 h-3.5 mr-1.5 text-status-warning" />
                Logs Directory
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleOpenFolder('config')}
                className="text-[11px]"
              >
                <FolderOpen className="w-3.5 h-3.5 mr-1.5 text-primary" />
                Config Directory
              </Button>
            </div>
          </div>
        </div>

        {/* Desktop Preferences */}
        <div className="p-4 bg-surface rounded-lg border border-border space-y-4">
          <SectionHeader
            title="Native Preferences & Window Management"
            subtitle="Saved to %LOCALAPPDATA%\AUTONOM\config\desktop_settings.json"
            icon={<Maximize2 className="w-4 h-4 text-cyan" />}
          />

          <div className="space-y-3 pt-1">
            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>Close to System Tray (Keep running in background)</span>
              <Switch
                checked={desktopStatus?.settings.close_to_tray ?? true}
                onCheckedChange={(c) => handleSettingToggle('close_to_tray', c)}
              />
            </div>

            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>Launch AUTONOM on Windows Startup</span>
              <Switch
                checked={desktopStatus?.settings.start_at_login ?? false}
                onCheckedChange={(c) => handleSettingToggle('start_at_login', c)}
              />
            </div>

            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>Enable Native Desktop Notifications</span>
              <Switch
                checked={desktopStatus?.settings.notifications_enabled ?? true}
                onCheckedChange={(c) => handleSettingToggle('notifications_enabled', c)}
              />
            </div>

            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>Notify upon Long-Running Task Completion</span>
              <Switch
                checked={desktopStatus?.settings.notify_on_task_completion ?? true}
                onCheckedChange={(c) => handleSettingToggle('notify_on_task_completion', c)}
              />
            </div>

            <div className="flex items-center justify-between text-xs text-foreground-secondary">
              <span>Notify upon Backend Supervisor Events</span>
              <Switch
                checked={desktopStatus?.settings.notify_on_backend_events ?? true}
                onCheckedChange={(c) => handleSettingToggle('notify_on_backend_events', c)}
              />
            </div>
          </div>

          <div className="pt-2 border-t border-border text-[11px] text-foreground-muted flex items-center justify-between font-mono-tech">
            <span>Saved Geometry:</span>
            <span>
              {desktopStatus?.settings.window.width}x{desktopStatus?.settings.window.height} at (
              {desktopStatus?.settings.window.x},{desktopStatus?.settings.window.y})
            </span>
          </div>
        </div>
      </div>

      {/* Backend Readiness & Health Diagnostics */}
      <div className="p-4 bg-surface rounded-lg border border-border space-y-4">
        <SectionHeader
          title="Backend Readiness Diagnostics"
          subtitle="Probed live against the /health/ready endpoint"
          icon={<Activity className="w-4 h-4 text-status-success" />}
        />

        {readiness ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            <div className="p-3 bg-surface-elevated rounded-md border border-border">
              <span className="text-compact-label text-foreground-muted block mb-1">
                Overall Status:
              </span>
              <div className="flex items-center gap-2">
                <Badge variant={readiness.ready ? 'success' : 'error'} dot>
                  {readiness.status.toUpperCase()}
                </Badge>
              </div>
            </div>

            <div className="p-3 bg-surface-elevated rounded-md border border-border">
              <span className="text-compact-label text-foreground-muted block mb-1">
                Subsystem Checks:
              </span>
              <div className="space-y-1">
                {Object.entries(readiness.checks).map(([name, pass]) => (
                  <div
                    key={name}
                    className="flex items-center justify-between text-xs font-mono-tech"
                  >
                    <span className="text-foreground-secondary">{name}:</span>
                    <Badge
                      variant={pass ? 'success' : 'error'}
                      className="text-[10px] py-0 px-1 font-mono-tech"
                    >
                      {pass ? 'PASS' : 'FAIL'}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 bg-surface-elevated rounded-md border border-border">
              <span className="text-compact-label text-foreground-muted block mb-1">
                Supervisor Error State:
              </span>
              <span className="text-xs font-mono-tech text-foreground-secondary break-words">
                {backendProcess?.last_error || 'None (Healthy)'}
              </span>
            </div>
          </div>
        ) : (
          <div className="p-3.5 bg-surface-elevated border border-status-warning/40 rounded-lg text-xs text-status-warning flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-status-warning" />
            Backend readiness endpoint is currently unreachable or initializing.
          </div>
        )}
      </div>
    </PageContainer>
  );
};
