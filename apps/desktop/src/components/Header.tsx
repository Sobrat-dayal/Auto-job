import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, Terminal, Cpu } from 'lucide-react';
import { useBackendHealth, ConnectionStatus } from '@/hooks/use-backend-health';
import { getNativeAppInfo, AppInfo } from '@/services/tauri';

export const Header: React.FC = () => {
  const { connectionStatus, health } = useBackendHealth();
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    getNativeAppInfo().then(setAppInfo);
  }, []);

  const getStatusBadge = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-800/80 text-emerald-400 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>CONNECTED (8765)</span>
          </div>
        );
      case 'connecting':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-950/60 border border-amber-800/80 text-amber-400 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
            <span>CONNECTING...</span>
          </div>
        );
      case 'disconnected':
      default:
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-950/60 border border-rose-800/80 text-rose-400 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span>DISCONNECTED</span>
          </div>
        );
    }
  };

  return (
    <header className="h-12 border-b border-border bg-surface px-4 flex items-center justify-between select-none">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-primary-light" />
          <span className="font-bold tracking-wider text-sm text-slate-100">AUTONOM</span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-surface-elevated text-slate-400 font-mono">
            v0.1.0-dev
          </span>
        </div>

        <div className="h-4 w-px bg-border mx-1" />

        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
          <Cpu className="w-3.5 h-3.5 text-cyan" />
          <span>{appInfo ? `${appInfo.os} (${appInfo.arch})` : 'Windows x64'}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-primary-light" />
          <span>Stage 02 Foundation</span>
        </div>

        {health && (
          <span className="text-[11px] font-mono text-slate-400 hidden lg:inline">
            Uptime: {Math.floor(health.uptime_seconds)}s
          </span>
        )}

        {getStatusBadge(connectionStatus)}

        <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono bg-surface-elevated px-2 py-1 rounded border border-border">
          <Activity className="w-3 h-3 text-slate-400" />
          <span>Ctrl+Shift+Esc</span>
        </div>
      </div>
    </header>
  );
};
