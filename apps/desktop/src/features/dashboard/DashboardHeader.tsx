import * as React from 'react';
import { RefreshCw, Server, Cpu, Clock, Radio } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { DashboardOverviewResponse } from '@/types/dashboard';

interface DashboardHeaderProps {
  overview?: DashboardOverviewResponse;
  isLoading: boolean;
  isFetching: boolean;
  isConnected: boolean;
  onRefresh: () => void;
  lastUpdated?: Date;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  overview,
  isLoading,
  isFetching,
  isConnected,
  onRefresh,
  lastUpdated,
}) => {
  const systemStatus = overview?.system_status || (isConnected ? 'operational' : 'disconnected');

  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 rounded-xl border border-border/70 bg-surface/60 backdrop-blur-sm shadow-sm">
      {/* Title & Hierarchy */}
      <div className="space-y-1">
        <div className="flex flex-wrap items-center gap-2.5">
          <h1 className="text-xl font-bold tracking-tight text-foreground font-sans">
            Command Center
          </h1>
          <Badge variant="cyan" dot pulse>
            Stage 08 Active
          </Badge>
          <Badge
            variant={
              systemStatus === 'operational'
                ? 'success'
                : systemStatus === 'degraded'
                  ? 'warning'
                  : 'error'
            }
            dot
            pulse={systemStatus === 'operational'}
            className="capitalize font-mono-tech text-[10px]"
          >
            System: {systemStatus}
          </Badge>
        </div>
        <p className="text-xs text-foreground-muted leading-relaxed">
          Primary operational dashboard supervising background execution, worker orchestration, and
          persistent storage.
        </p>
      </div>

      {/* Operational Signals & Controls */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {/* Backend Connectivity Status */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-elevated/70 border border-border/50 font-mono-tech text-[11px]">
          <Server className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-400' : 'text-rose-500'}`} />
          <span className="text-foreground">{isConnected ? 'HTTP 8765' : 'DISCONNECTED'}</span>
          {overview && (
            <span className="text-foreground-muted text-[10px] pl-1 border-l border-border/40">
              {Math.floor(overview.uptime_seconds)}s uptime
            </span>
          )}
        </div>

        {/* Global Dispatch Status */}
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-elevated/70 border border-border/50 text-[11px] cursor-default">
              <Radio className="h-3.5 w-3.5 text-accent-cyan" />
              <span className="text-foreground-secondary">
                Dispatch: <span className="text-accent-cyan font-medium">Active</span>
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            Stage 03 Task Execution Manager & Worker Pool is actively dispatching registered tasks.
          </TooltipContent>
        </Tooltip>

        {/* AI Swarm Capability Status */}
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-elevated/70 border border-border/50 text-[11px] cursor-default">
              <Cpu className="h-3.5 w-3.5 text-accent-primary" />
              <span className="text-foreground-secondary">
                Swarm: <span className="text-foreground-muted font-mono-tech">Stage 12</span>
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            Autonomous multi-agent orchestration runtime is scheduled for Stage 12.
          </TooltipContent>
        </Tooltip>

        {/* Last Sync Timestamp */}
        {lastUpdated && (
          <div className="hidden md:flex items-center gap-1 text-[11px] text-foreground-muted font-mono-tech">
            <Clock className="h-3 w-3" />
            <span>{lastUpdated.toLocaleTimeString()}</span>
          </div>
        )}

        {/* Refresh Action */}
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          disabled={isFetching || isLoading}
          isLoading={isFetching}
          loadingText="Syncing..."
          className="h-8 gap-1.5 text-xs font-medium"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Sync</span>
        </Button>
      </div>
    </div>
  );
};
