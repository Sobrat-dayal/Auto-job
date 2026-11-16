import React, { useEffect, useState } from 'react';
import { Server, RefreshCw, Cpu, Layers, HardDrive, Activity, Shield } from 'lucide-react';
import { useBackendHealth } from '@/hooks/use-backend-health';
import { getNativeAppInfo, AppInfo } from '@/services/tauri';
import { PageContainer } from '@/components/layout/PageContainer';
import { SectionHeader } from '@/components/layout/SectionHeader';
import { StatusCard } from '@/components/data-display/StatusCard';
import { MetricCard } from '@/components/data-display/MetricCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export const Overview: React.FC = () => {
  const { connectionStatus, health, refetch, isFetching } = useBackendHealth();
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    getNativeAppInfo().then(setAppInfo);
  }, []);

  const isConnected = connectionStatus === 'connected';

  return (
    <PageContainer
      title="Command Center"
      subtitle="Operational supervision, native desktop runtime diagnostics, and system health status"
      badge={
        <Badge variant="primary" dot pulse>
          Stage 06 Active
        </Badge>
      }
      actions={
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
          isLoading={isFetching}
          loadingText="Verifying..."
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Check Status
        </Button>
      }
    >
      {/* High-Level Metric Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <MetricCard
          title="Backend Service"
          value={isConnected ? 'ONLINE' : 'OFFLINE'}
          subtitle="Loopback HTTP 127.0.0.1:8765"
          icon={<Server className="w-4 h-4" />}
          variant={isConnected ? 'success' : 'default'}
        />
        <MetricCard
          title="Service Uptime"
          value={health ? `${Math.floor(health.uptime_seconds)}s` : '0s'}
          subtitle="FastAPI async event loop"
          icon={<Activity className="w-4 h-4" />}
          variant="cyan"
        />
        <MetricCard
          title="Desktop Engine"
          value="Tauri 2"
          subtitle={appInfo ? `${appInfo.os} (${appInfo.arch})` : 'Windows 11 x64'}
          icon={<Cpu className="w-4 h-4" />}
          variant="primary"
        />
        <MetricCard
          title="Security Perimeter"
          value="ENFORCED"
          subtitle="DPAPI + Local Loopback Check"
          icon={<Shield className="w-4 h-4" />}
          variant="default"
        />
      </div>

      {/* Layer Cards */}
      <div className="space-y-3">
        <SectionHeader
          title="Subsystem Operational Status"
          subtitle="Real-time introspection across the backend sidecar, native desktop harness, and persistence layers"
          icon={<Layers className="w-4 h-4 text-cyan" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Backend Status Card */}
          <StatusCard
            title="Backend Service"
            icon={<Server className="w-4 h-4 text-primary" />}
            statusBadge={{
              label: isConnected ? 'Healthy / WAL Active' : 'Offline / Unreachable',
              variant: isConnected ? 'success' : 'error',
              pulse: isConnected,
            }}
            properties={[
              { label: 'Host Endpoint', value: 'http://127.0.0.1:8765', mono: true },
              { label: 'Connection State', value: connectionStatus.toUpperCase() },
              {
                label: 'Service Uptime',
                value: health ? `${health.uptime_seconds}s` : 'N/A',
                mono: true,
              },
              { label: 'API Version', value: health?.version || 'v0.1.0-dev', mono: true },
              {
                label: 'Loopback Guard',
                value: health?.is_loopback ? 'Strictly Enforced' : 'Unverified',
              },
            ]}
          />

          {/* Native Desktop Layer Card */}
          <StatusCard
            title="Desktop Runtime"
            icon={<Cpu className="w-4 h-4 text-cyan" />}
            statusBadge={{
              label: 'Tauri 2 / Rust Bridge',
              variant: 'cyan',
            }}
            properties={[
              { label: 'Application Name', value: appInfo?.name || 'AUTONOM' },
              { label: 'Target Platform', value: appInfo?.os || 'Windows 11' },
              { label: 'CPU Architecture', value: appInfo?.arch || 'x86_64', mono: true },
              { label: 'Tauri Framework', value: appInfo?.tauri_version || '2.0.0', mono: true },
              { label: 'IPC Communication', value: 'Win32 Named Pipes & In-Proc' },
            ]}
          />

          {/* Architecture Card */}
          <StatusCard
            title="Layer Architecture"
            icon={<Layers className="w-4 h-4 text-primary" />}
            statusBadge={{
              label: '6-Layer Autonomous Model',
              variant: 'neutral',
            }}
            properties={[
              { label: 'Frontend Shell', value: 'React 19 / TS / Vite' },
              { label: 'Native Bridge', value: 'Rust / Win32 / UIA' },
              { label: 'Backend Worker', value: 'FastAPI / Asyncio' },
              { label: 'Persistent DB', value: 'SQLite (WAL) + DPAPI' },
              { label: 'Design System', value: 'Dark Tokens / High-DPI' },
            ]}
          />
        </div>
      </div>

      {/* Under Active Development Notice */}
      <div className="p-4 rounded-lg bg-surface border border-border/80 flex items-start gap-3">
        <HardDrive className="w-5 h-5 text-cyan shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Development Notice — 50-Stage Roadmap Progression
            </h3>
            <Badge variant="cyan" className="text-[10px] py-0 px-1 font-mono-tech">
              Stage 06 Complete
            </Badge>
          </div>
          <p className="text-xs text-foreground-secondary leading-relaxed">
            The design tokens, centralized color system, accessible React components, and responsive
            desktop layouts are operational. The multi-agent swarm, autonomous computer control, job
            discovery scrapers, and application pipelines integrate on top of this verified design
            system foundation.
          </p>
        </div>
      </div>
    </PageContainer>
  );
};
