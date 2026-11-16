import * as React from 'react';
import { Server, Cpu, Database, Monitor, ExternalLink, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { DashboardOverviewResponse } from '@/types/dashboard';

interface SystemHealthPanelProps {
  overview?: DashboardOverviewResponse;
  isConnected: boolean;
  onNavigateToDiagnostics?: () => void;
  onNavigateToDesktop?: () => void;
  onNavigateToStorage?: () => void;
}

export const SystemHealthPanel: React.FC<SystemHealthPanelProps> = ({
  overview,
  isConnected,
  onNavigateToDiagnostics,
  onNavigateToDesktop,
  onNavigateToStorage,
}) => {
  const subsystems = [
    {
      name: 'Backend Sidecar API',
      status: isConnected ? 'OPERATIONAL' : 'DISCONNECTED',
      detail: 'HTTP 127.0.0.1:8765 loopback',
      icon: Server,
      color: isConnected ? 'text-emerald-400' : 'text-rose-500',
      badgeVariant: isConnected ? ('success' as const) : ('error' as const),
      action: onNavigateToDiagnostics,
    },
    {
      name: 'Worker Thread Manager',
      status: isConnected ? 'OPERATIONAL' : 'OFFLINE',
      detail: overview?.workers
        ? `${overview.workers.active} active / ${overview.workers.total} threads`
        : '4 concurrent workers',
      icon: Cpu,
      color: isConnected ? 'text-accent-cyan' : 'text-rose-500',
      badgeVariant: isConnected ? ('success' as const) : ('error' as const),
      action: onNavigateToDiagnostics,
    },
    {
      name: 'SQLite Database & WAL',
      status: isConnected ? 'SYNCHRONIZED' : 'UNREACHABLE',
      detail: 'Local WAL engine + DPAPI vault',
      icon: Database,
      color: isConnected ? 'text-accent-primary' : 'text-rose-500',
      badgeVariant: isConnected ? ('success' as const) : ('error' as const),
      action: onNavigateToStorage,
    },
    {
      name: 'Tauri Desktop Supervisor',
      status: 'SUPERVISED',
      detail: 'Win32 Job Object containment',
      icon: Monitor,
      color: 'text-accent-cyan',
      badgeVariant: 'cyan' as const,
      action: onNavigateToDesktop,
    },
  ];

  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Subsystem Health & Lifecycle
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                Process containment, WAL journal, and service health
              </CardDescription>
            </div>
          </div>

          <Badge
            variant={isConnected ? 'success' : 'error'}
            dot
            pulse={isConnected}
            className="text-[10px]"
          >
            {isConnected ? '4/4 ONLINE' : 'DEGRADED'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-2.5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {subsystems.map((sub) => {
            const Icon = sub.icon;

            return (
              <div
                key={sub.name}
                onClick={sub.action}
                className="p-2.5 rounded-lg border border-border/40 bg-surface-elevated/30 hover:bg-surface-elevated/60 transition-colors cursor-pointer group flex items-start justify-between gap-2"
              >
                <div className="flex items-start gap-2 min-w-0">
                  <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${sub.color}`} />
                  <div className="min-w-0 space-y-0.5">
                    <span className="font-semibold text-xs text-foreground truncate block">
                      {sub.name}
                    </span>
                    <span className="text-[10px] text-foreground-muted truncate block font-mono-tech">
                      {sub.detail}
                    </span>
                  </div>
                </div>

                <Badge
                  variant={sub.badgeVariant}
                  className="text-[9px] py-0 px-1 shrink-0 font-mono-tech"
                >
                  {sub.status}
                </Badge>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
          <span className="text-[10px] text-foreground-muted font-mono-tech">
            Loopback authorization active
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={onNavigateToDiagnostics}
            className="h-7 text-xs text-accent-primary hover:text-accent-primary gap-1"
          >
            <span>Open System Diagnostics</span>
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
