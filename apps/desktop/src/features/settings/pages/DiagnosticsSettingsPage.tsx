import React, { useEffect, useState } from 'react';
import { apiClient, type BackendHealth, type BackendVersion } from '@/lib/api-client';
import {
  getBackendProcessStatus,
  getDesktopStatus,
  type BackendProcessStatus,
  type DesktopStatus,
} from '@/services/tauri';
import type {
  SystemCapabilitiesResponse,
  SystemStatusResponse,
  WorkerListResponse,
} from '@autonom/shared-types';
import { RefreshCw, Download, ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SettingsSection } from '../components';

export const DiagnosticsSettingsPage: React.FC = () => {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [version, setVersion] = useState<BackendVersion | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);
  const [capabilities, setCapabilities] = useState<SystemCapabilitiesResponse | null>(null);
  const [workers, setWorkers] = useState<WorkerListResponse | null>(null);
  const [backendProcess, setBackendProcess] = useState<BackendProcessStatus | null>(null);
  const [desktopStatus, setDesktopStatus] = useState<DesktopStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDiagnostics = async () => {
    setIsLoading(true);
    try {
      const [hData, vData, sData, cData, wData, bpData, dsData] = await Promise.all([
        apiClient.getHealth().catch(() => null),
        apiClient.getVersion().catch(() => null),
        apiClient.getSystemStatus().catch(() => null),
        apiClient.getSystemCapabilities().catch(() => null),
        apiClient.getWorkers().catch(() => null),
        getBackendProcessStatus().catch(() => null),
        getDesktopStatus().catch(() => null),
      ]);
      setHealth(hData);
      setVersion(vData);
      setSystemStatus(sData);
      setCapabilities(cData);
      setWorkers(wData);
      setBackendProcess(bpData);
      setDesktopStatus(dsData);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  const handleExportDiagnostics = () => {
    const report = {
      timestamp: new Date().toISOString(),
      desktop: desktopStatus,
      backend_process: backendProcess,
      health,
      version,
      system_status: systemStatus,
      capabilities,
      workers,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `autonom_diagnostics_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <SettingsSection
        title="Live Diagnostic Telemetry & System Status"
        description="Real-time health telemetry across the Windows desktop shell, Python backend, and SQLite persistence."
        headerAction={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportDiagnostics}
              className="h-7 text-xs px-2.5 gap-1.5"
            >
              <Download className="h-3 w-3" />
              <span>Export Diagnostic Bundle</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDiagnostics}
              disabled={isLoading}
              className="h-7 text-xs px-2.5 gap-1.5"
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
          </div>
        }
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Backend Process
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 flex items-center gap-1.5">
              <span
                className={`h-2 w-2 rounded-full ${backendProcess?.state === 'Ready' ? 'bg-emerald-400' : 'bg-amber-400'}`}
              />
              <span>{backendProcess?.state || 'Unknown'}</span>
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">
              PID: {backendProcess?.pid || '—'} (Port: {backendProcess?.port || 8765})
            </span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Backend Uptime
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 font-mono">
              {health ? `${health.uptime_seconds.toFixed(0)}s` : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">
              Restarts: {backendProcess?.restart_count ?? 0} / {backendProcess?.max_restarts ?? 5}
            </span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Worker Pool
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 font-mono">
              {workers ? `${workers.active_workers} / ${workers.total_workers}` : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">Active Coroutines</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Queue Depth
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 font-mono">
              {systemStatus
                ? `${systemStatus.tasks.queued} / ${systemStatus.workers.max_capacity}`
                : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">Bounded Queue</span>
          </div>
        </div>
      </SettingsSection>

      <SettingsSection
        title="Registered Backend Capabilities"
        description="Features confirmed operational by the running backend service."
      >
        <div className="flex flex-wrap gap-2">
          {capabilities?.supported_task_types.map((cap: string) => (
            <Badge key={cap} variant="cyan" className="text-xs font-mono py-1 px-2.5">
              <ShieldCheck className="h-3 w-3 mr-1 text-cyan" />
              {cap}
            </Badge>
          )) || <p className="text-xs text-muted-foreground">Loading capabilities...</p>}
        </div>
      </SettingsSection>

      <SettingsSection
        title="Environment & Version Information"
        description="Platform runtime mode and build specifics."
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
          <div className="p-2.5 rounded bg-card/50 border border-border/40 space-y-1">
            <div className="text-muted-foreground text-[11px]">Desktop Host:</div>
            <div className="text-foreground">
              {desktopStatus?.app_info.name} v{desktopStatus?.app_info.version} (Tauri{' '}
              {desktopStatus?.app_info.tauri_version})
            </div>
            <div className="text-muted-foreground text-[11px]">
              OS: {desktopStatus?.app_info.os} ({desktopStatus?.app_info.arch})
            </div>
          </div>

          <div className="p-2.5 rounded bg-card/50 border border-border/40 space-y-1">
            <div className="text-muted-foreground text-[11px]">Python Backend Service:</div>
            <div className="text-foreground">
              {version?.app_name} v{version?.version} ({version?.python_version})
            </div>
            <div className="text-muted-foreground text-[11px]">
              API: {version?.api_version} | Loopback: {health?.is_loopback ? 'Verified' : 'False'}
            </div>
          </div>
        </div>
      </SettingsSection>
    </div>
  );
};
