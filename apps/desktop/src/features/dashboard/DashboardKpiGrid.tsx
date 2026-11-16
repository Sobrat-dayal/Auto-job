import * as React from 'react';
import {
  Activity,
  Clock,
  Briefcase,
  Send,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Cpu,
} from 'lucide-react';
import { MetricCard } from '@/components/data-display/MetricCard';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import type { DashboardOverviewResponse } from '@/types/dashboard';

interface DashboardKpiGridProps {
  overview?: DashboardOverviewResponse;
  isLoading: boolean;
  isConnected: boolean;
  onSelectTaskFilter?: (status: string) => void;
  onNavigateToRecruitment?: () => void;
}

export const DashboardKpiGrid: React.FC<DashboardKpiGridProps> = ({
  overview,
  isLoading,
  isConnected,
  onSelectTaskFilter,
  onNavigateToRecruitment,
}) => {
  if (isLoading && !overview) {
    return (
      <div className="space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 rounded-lg border border-border bg-surface p-4 space-y-3">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-3 w-36" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const tasks = overview?.tasks_summary;
  const recruitment = overview?.recruitment;
  const workers = overview?.workers;

  const runningTasks = isConnected && tasks ? tasks.running : 0;
  const queuedTasks = isConnected && tasks ? tasks.queued : 0;
  const completedTasks = isConnected && tasks ? tasks.completed : 0;
  const failedTasks = isConnected && tasks ? tasks.failed : 0;
  const jobsDiscovered = isConnected && recruitment ? recruitment.jobs_discovered : 0;
  const appsSubmitted = isConnected && recruitment ? recruitment.applications_submitted : 0;
  const activeWorkers = isConnected && workers ? `${workers.active}/${workers.total}` : '0/4';

  return (
    <div className="space-y-3 select-none">
      {/* Primary KPI Row (4 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Running Tasks */}
        <div
          onClick={() => onSelectTaskFilter?.('running')}
          className="cursor-pointer group transition-transform active:scale-[0.99]"
        >
          <MetricCard
            title="Running Tasks"
            value={isConnected ? runningTasks : 'N/A'}
            subtitle={isConnected ? 'Active background workers' : 'Backend unavailable'}
            icon={<Activity className="w-4 h-4 text-accent-cyan" />}
            variant={runningTasks > 0 ? 'cyan' : 'default'}
          />
        </div>

        {/* Queued Tasks */}
        <div
          onClick={() => onSelectTaskFilter?.('queued')}
          className="cursor-pointer group transition-transform active:scale-[0.99]"
        >
          <MetricCard
            title="Queued Tasks"
            value={isConnected ? queuedTasks : 'N/A'}
            subtitle={isConnected ? 'Awaiting worker thread' : 'Backend unavailable'}
            icon={<Clock className="w-4 h-4 text-accent-primary" />}
            variant="default"
          />
        </div>

        {/* Jobs Discovered */}
        <div
          onClick={onNavigateToRecruitment}
          className="cursor-pointer group transition-transform active:scale-[0.99]"
        >
          <MetricCard
            title="Jobs Discovered"
            value={
              <div className="flex items-baseline gap-2">
                <span>{isConnected ? jobsDiscovered : '0'}</span>
                <Badge
                  variant="outline"
                  className="text-[9px] py-0 px-1 border-accent-primary/40 text-accent-primary"
                >
                  Stage 26
                </Badge>
              </div>
            }
            subtitle={
              isConnected && jobsDiscovered > 0
                ? `${jobsDiscovered} listings in SQLite`
                : 'Scouting scheduled Stage 26'
            }
            icon={<Briefcase className="w-4 h-4 text-accent-primary" />}
            variant="default"
          />
        </div>

        {/* Applications Submitted */}
        <div
          onClick={onNavigateToRecruitment}
          className="cursor-pointer group transition-transform active:scale-[0.99]"
        >
          <MetricCard
            title="Applications Submitted"
            value={
              <div className="flex items-baseline gap-2">
                <span>{isConnected ? appsSubmitted : '0'}</span>
                <Badge
                  variant="outline"
                  className="text-[9px] py-0 px-1 border-accent-primary/40 text-accent-primary"
                >
                  Stage 31
                </Badge>
              </div>
            }
            subtitle={
              isConnected && appsSubmitted > 0
                ? `${appsSubmitted} verified submissions`
                : 'Submissions scheduled Stage 31'
            }
            icon={<Send className="w-4 h-4 text-accent-cyan" />}
            variant={appsSubmitted > 0 ? 'success' : 'default'}
          />
        </div>
      </div>

      {/* Secondary Metrics Strip (4 Supporting Cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Completed Tasks */}
        <div
          onClick={() => onSelectTaskFilter?.('completed')}
          className="cursor-pointer p-3 rounded-lg border border-border/50 bg-surface/40 hover:bg-surface-elevated/50 transition-colors"
        >
          <div className="flex items-center justify-between text-xs text-foreground-muted">
            <span>Completed Tasks</span>
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-bold text-foreground font-mono-tech mt-1">
            {isConnected ? completedTasks : '0'}
          </div>
          <div className="text-[10px] text-foreground-muted">Durable task completions</div>
        </div>

        {/* Failed Tasks */}
        <div
          onClick={() => onSelectTaskFilter?.('failed')}
          className="cursor-pointer p-3 rounded-lg border border-border/50 bg-surface/40 hover:bg-surface-elevated/50 transition-colors"
        >
          <div className="flex items-center justify-between text-xs text-foreground-muted">
            <span>Failed Tasks</span>
            <AlertTriangle
              className={`h-3.5 w-3.5 ${failedTasks > 0 ? 'text-rose-500' : 'text-foreground-muted'}`}
            />
          </div>
          <div
            className={`text-lg font-bold font-mono-tech mt-1 ${failedTasks > 0 ? 'text-rose-400' : 'text-foreground'}`}
          >
            {isConnected ? failedTasks : '0'}
          </div>
          <div className="text-[10px] text-foreground-muted">
            {failedTasks > 0 ? 'Requires operator review' : 'No execution failures'}
          </div>
        </div>

        {/* Pending Approvals */}
        <div className="p-3 rounded-lg border border-border/50 bg-surface/40">
          <div className="flex items-center justify-between text-xs text-foreground-muted">
            <span>Pending Approvals</span>
            <ShieldAlert className="h-3.5 w-3.5 text-accent-primary" />
          </div>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span className="text-lg font-bold text-foreground font-mono-tech">0</span>
            <span className="text-[9px] text-foreground-muted font-mono-tech">Stage 14</span>
          </div>
          <div className="text-[10px] text-foreground-muted">Advance authorization gate</div>
        </div>

        {/* Worker Threads */}
        <div className="p-3 rounded-lg border border-border/50 bg-surface/40">
          <div className="flex items-center justify-between text-xs text-foreground-muted">
            <span>Worker Threads</span>
            <Cpu className="h-3.5 w-3.5 text-accent-cyan" />
          </div>
          <div className="text-lg font-bold text-foreground font-mono-tech mt-1">
            {isConnected ? activeWorkers : '0/4'}
          </div>
          <div className="text-[10px] text-foreground-muted">Concurrent Python workers</div>
        </div>
      </div>
    </div>
  );
};
