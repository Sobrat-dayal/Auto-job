import * as React from 'react';
import { RefreshCw, Server, Clock, ShieldAlert, Pause, Play } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { apiClient } from '@/lib/api-client';
import type { DashboardOverviewResponse } from '@/types/dashboard';
import type { EmergencyStopState } from '@autonom/shared-types';

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
  const [emergencyState, setEmergencyState] = React.useState<EmergencyStopState | null>(null);
  const [isToggling, setIsToggling] = React.useState(false);

  const fetchEmergencyStatus = React.useCallback(async () => {
    try {
      const state = await apiClient.getEmergencyStopStatus();
      setEmergencyState(state);
    } catch {
      // Backend may be offline
    }
  }, []);

  React.useEffect(() => {
    fetchEmergencyStatus();
    const interval = setInterval(fetchEmergencyStatus, 4000);
    return () => clearInterval(interval);
  }, [fetchEmergencyStatus]);

  const handleToggleEmergencyStop = async () => {
    setIsToggling(true);
    try {
      if (emergencyState?.is_active) {
        const state = await apiClient.clearEmergencyStop();
        setEmergencyState(state);
      } else {
        const state = await apiClient.activateEmergencyStop('Operator manual stop from Command Center');
        setEmergencyState(state);
      }
    } catch (err) {
      console.error('Failed to toggle emergency stop', err);
    } finally {
      setIsToggling(false);
    }
  };

  const handleTogglePause = async () => {
    setIsToggling(true);
    try {
      if (emergencyState?.is_paused) {
        const state = await apiClient.resumeAutomation();
        setEmergencyState(state);
      } else {
        const state = await apiClient.pauseAutomation('Operator pause from Command Center');
        setEmergencyState(state);
      }
    } catch (err) {
      console.error('Failed to toggle automation pause', err);
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <div className="space-y-2">
      {/* Emergency Stop Active Alert Banner */}
      {emergencyState?.is_active && (
        <div className="flex items-center justify-between p-3 px-4 rounded-xl bg-rose-600 text-white shadow-lg animate-pulse">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <div>
              <span className="font-bold text-xs uppercase tracking-wider">Emergency Stop Engaged</span>
              <p className="text-[11px] text-rose-100">
                All autonomous dispatches, tool executions, and external agent operations are halted.
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs bg-white text-rose-700 hover:bg-rose-50 border-transparent font-semibold"
            onClick={handleToggleEmergencyStop}
            disabled={isToggling}
          >
            Disengage Stop
          </Button>
        </div>
      )}

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 rounded-xl border border-border/70 bg-surface/60 backdrop-blur-sm shadow-sm">
        {/* Title & Hierarchy */}
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl font-bold tracking-tight text-foreground font-sans">
              Command Center
            </h1>
            <Badge variant="cyan" dot pulse>
              Stage 14 Active
            </Badge>
            <Badge
              variant={
                emergencyState?.is_active
                  ? 'error'
                  : emergencyState?.is_paused
                    ? 'warning'
                    : systemStatus === 'operational'
                      ? 'success'
                      : systemStatus === 'degraded'
                        ? 'warning'
                        : 'error'
              }
              dot
              pulse={systemStatus === 'operational' && !emergencyState?.is_active}
              className="capitalize font-mono-tech text-[10px]"
            >
              {emergencyState?.is_active
                ? 'EMERGENCY STOP'
                : emergencyState?.is_paused
                  ? 'DISPATCH PAUSED'
                  : `System: ${systemStatus}`}
            </Badge>
          </div>
          <p className="text-xs text-foreground-muted leading-relaxed">
            Primary operational dashboard supervising background execution, worker orchestration, and
            authorization boundaries.
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

          {/* Pause / Resume Automation Button */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                onClick={handleTogglePause}
                disabled={isToggling || emergencyState?.is_active}
                className={`h-8 gap-1.5 text-xs ${
                  emergencyState?.is_paused
                    ? 'border-amber-500/50 bg-amber-500/10 text-amber-300'
                    : 'text-foreground-muted'
                }`}
              >
                {emergencyState?.is_paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                <span>{emergencyState?.is_paused ? 'Resume' : 'Pause'}</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {emergencyState?.is_paused ? 'Resume autonomous task dispatch' : 'Pause autonomous task dispatch without losing state'}
            </TooltipContent>
          </Tooltip>

          {/* Emergency Stop Button */}
          <Button
            variant={emergencyState?.is_active ? 'outline' : 'destructive'}
            size="sm"
            onClick={handleToggleEmergencyStop}
            disabled={isToggling}
            className="h-8 gap-1.5 text-xs font-semibold"
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>{emergencyState?.is_active ? 'Clear Stop' : 'Emergency Stop'}</span>
          </Button>

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
    </div>
  );
};
