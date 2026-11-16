import * as React from 'react';
import { useState } from 'react';
import {
  Play,
  Briefcase,
  Send,
  Bot,
  Activity,
  Monitor,
  Database,
  RefreshCw,
  Terminal,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';

interface QuickActionsProps {
  onRefresh: () => void;
  onNavigate: (path: string) => void;
  onTaskDispatched?: () => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  onRefresh,
  onNavigate,
  onTaskDispatched,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDispatchTestTask = async () => {
    setIsSubmitting(true);
    try {
      await apiClient.createTask({
        task_type: 'test.sleep_progress',
        priority: 'normal',
        payload: {
          duration_seconds: 4,
          steps: 4,
          message: 'Stage 08 live command center verification task',
        },
      });
      onTaskDispatched?.();
      onRefresh();
    } catch (err) {
      console.error('Failed to dispatch test task:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const actionItems = [
    {
      label: 'Dispatch Test Task',
      desc: 'Execute real 4s worker task',
      icon: Play,
      color: 'text-accent-cyan',
      onClick: handleDispatchTestTask,
      isLoading: isSubmitting,
    },
    {
      label: 'Job Discovery',
      desc: 'Scouted listings (Stage 26)',
      icon: Briefcase,
      color: 'text-accent-primary',
      onClick: () => onNavigate('/recruitment'),
    },
    {
      label: 'Applications',
      desc: 'Pipeline tracker (Stage 31)',
      icon: Send,
      color: 'text-emerald-400',
      onClick: () => onNavigate('/applications'),
    },
    {
      label: 'Agents Swarm',
      desc: 'Fleet supervisor (Stage 12)',
      icon: Bot,
      color: 'text-accent-cyan',
      onClick: () => onNavigate('/agents'),
    },
    {
      label: 'Backend Diagnostics',
      desc: 'Worker threads & SSE events',
      icon: Activity,
      color: 'text-accent-primary',
      onClick: () => onNavigate('/diagnostics'),
    },
    {
      label: 'Desktop Shell',
      desc: 'Tauri supervisor runtime',
      icon: Monitor,
      color: 'text-accent-cyan',
      onClick: () => onNavigate('/desktop-diagnostics'),
    },
    {
      label: 'Database Storage',
      desc: 'SQLite WAL & snapshots',
      icon: Database,
      color: 'text-emerald-400',
      onClick: () => onNavigate('/storage'),
    },
    {
      label: 'Sync Metrics',
      desc: 'Instant state refresh',
      icon: RefreshCw,
      color: 'text-foreground',
      onClick: onRefresh,
    },
  ];

  return (
    <Card className="border-border/60 bg-surface/50 select-none">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-accent-primary" />
          <div>
            <CardTitle className="text-sm font-semibold text-foreground">
              Operational Quick Actions
            </CardTitle>
            <CardDescription className="text-[11px] text-foreground-muted">
              Direct execution dispatch and navigation shortcuts
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2">
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {actionItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.label}
                onClick={item.onClick}
                disabled={item.isLoading}
                className="p-2.5 rounded-lg border border-border/40 bg-surface-elevated/30 hover:bg-surface-elevated/70 active:scale-[0.98] transition-all flex flex-col items-center justify-center text-center group disabled:opacity-50"
              >
                <Icon
                  className={`h-4 w-4 mb-1.5 transition-transform group-hover:scale-110 ${item.color}`}
                />
                <span className="text-xs font-semibold text-foreground truncate max-w-full">
                  {item.label}
                </span>
                <span className="text-[9px] text-foreground-muted truncate max-w-full">
                  {item.desc}
                </span>
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
