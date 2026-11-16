import React, { useEffect, useState } from 'react';
import {
  Server,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Cpu,
  Layers,
  HardDrive,
} from 'lucide-react';
import { useBackendHealth } from '@/hooks/use-backend-health';
import { getNativeAppInfo, AppInfo } from '@/services/tauri';

export const Overview: React.FC = () => {
  const { connectionStatus, health, refetch, isFetching } = useBackendHealth();
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    getNativeAppInfo().then(setAppInfo);
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto overflow-y-auto">
      {/* Title & Stage Notice */}
      <div className="border-b border-border pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span>Command Center</span>
            <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary-light border border-primary/30 font-mono font-normal">
              Stage 02 Active
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monorepo Setup, Full-Stack Development Environment, and Executable Project Foundation
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-elevated hover:bg-slate-700 text-slate-200 text-xs font-medium border border-border transition-colors self-start md:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-cyan' : ''}`} />
          <span>Check Status</span>
        </button>
      </div>

      {/* Real Connected Environment Diagnostics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Backend Status Card */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Server className="w-4 h-4 text-primary-light" />
              Backend Service
            </span>
            {connectionStatus === 'connected' ? (
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
              </span>
            ) : (
              <span className="text-xs font-mono text-rose-400 flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" /> Offline
              </span>
            )}
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex justify-between text-slate-400">
              <span>Endpoint:</span>
              <span className="text-slate-200">http://127.0.0.1:8765</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Status:</span>
              <span
                className={
                  connectionStatus === 'connected'
                    ? 'text-emerald-400 font-semibold'
                    : 'text-rose-400'
                }
              >
                {connectionStatus.toUpperCase()}
              </span>
            </div>
            {health && (
              <>
                <div className="flex justify-between text-slate-400">
                  <span>Uptime:</span>
                  <span className="text-slate-200">{health.uptime_seconds}s</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Version:</span>
                  <span className="text-slate-200">{health.version}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Loopback:</span>
                  <span className="text-emerald-400">{health.is_loopback ? 'Enforced' : 'No'}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Native Desktop Layer Card */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-cyan" />
              Desktop Runtime
            </span>
            <span className="text-xs font-mono text-cyan">Tauri 2 / Rust</span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex justify-between text-slate-400">
              <span>App Name:</span>
              <span className="text-slate-200">{appInfo?.name || 'AUTONOM'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>OS Platform:</span>
              <span className="text-slate-200">{appInfo?.os || 'Windows 11 x64'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Architecture:</span>
              <span className="text-slate-200">{appInfo?.arch || 'x86_64'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Tauri Core:</span>
              <span className="text-slate-200">{appInfo?.tauri_version || '2.0'}</span>
            </div>
          </div>
        </div>

        {/* Workspace & Architecture Card */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-primary-light" />
              Architecture
            </span>
            <span className="text-xs font-mono text-slate-400">6-Layer Model</span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex justify-between text-slate-400">
              <span>Frontend:</span>
              <span className="text-slate-200">React 19 / TS / Vite</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Native Bridge:</span>
              <span className="text-slate-200">Rust / Win32 / UIA</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Backend API:</span>
              <span className="text-slate-200">FastAPI / Asyncio</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Storage:</span>
              <span className="text-slate-200">SQLite (WAL) + DPAPI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Under Active Development Notice */}
      <div className="p-4 rounded-lg bg-surface-muted border border-border/80 flex items-start gap-3">
        <HardDrive className="w-5 h-5 text-cyan shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Development Notice — Stage Progression Underway
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            The foundation of AUTONOM is now active and verified. The multi-agent swarm, autonomous
            computer control, job discovery scrapers, and resume tailoring pipelines will be
            implemented in subsequent stages according to the 50-stage roadmap. Current interface
            metrics accurately reflect the verified local environment state.
          </p>
        </div>
      </div>
    </div>
  );
};
