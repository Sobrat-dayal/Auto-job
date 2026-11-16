import * as React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, ArrowRight, Info } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { TaskResponse } from '@autonom/shared-types';

interface PendingActionsPanelProps {
  failedTasks: TaskResponse[];
  onSelectTask?: (taskId: string) => void;
  onNavigateToDiagnostics?: () => void;
}

export const PendingActionsPanel: React.FC<PendingActionsPanelProps> = ({
  failedTasks,
  onSelectTask,
  onNavigateToDiagnostics,
}) => {
  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Action Items & Operator Gates
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                Task failures, system exceptions, and advance authorization
              </CardDescription>
            </div>
          </div>

          <Badge variant={failedTasks.length > 0 ? 'warning' : 'outline'} className="text-[10px]">
            {failedTasks.length > 0 ? `${failedTasks.length} Pending` : 'All Clear'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-2.5">
        {failedTasks.length === 0 ? (
          <div className="p-4 rounded-lg border border-border/40 bg-surface-elevated/20 text-center space-y-1">
            <CheckCircle2 className="h-5 w-5 text-emerald-400 mx-auto mb-1" />
            <p className="text-xs font-semibold text-foreground">No Pending Action Items</p>
            <p className="text-[11px] text-foreground-muted">
              All background workers and durable tasks are operating within normal parameters.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5 max-h-36 overflow-y-auto">
            {failedTasks.slice(0, 4).map((task) => (
              <div
                key={task.task_id}
                onClick={() => onSelectTask?.(task.task_id)}
                className="p-2 rounded-lg border border-rose-500/30 bg-rose-500/5 hover:bg-rose-500/10 transition-colors cursor-pointer flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <AlertTriangle className="h-3.5 w-3.5 text-rose-500 shrink-0" />
                  <div className="min-w-0">
                    <span className="font-semibold text-foreground truncate block">
                      Failed: {task.task_type}
                    </span>
                    <span className="text-[10px] text-rose-300 font-mono-tech truncate block">
                      {(typeof task.error === 'string'
                        ? task.error
                        : (task.error as any)?.message) ||
                        task.message ||
                        'Execution error'}
                    </span>
                  </div>
                </div>

                <Badge variant="error" className="text-[9px] shrink-0 font-mono-tech">
                  REVIEW
                </Badge>
              </div>
            ))}
          </div>
        )}

        {/* Advance Authorization Gate Notice */}
        <div className="p-2.5 rounded-lg border border-border/40 bg-surface/40 flex items-start gap-2 text-xs">
          <Info className="h-3.5 w-3.5 text-accent-cyan mt-0.5 shrink-0" />
          <p className="text-[11px] text-foreground-muted leading-relaxed">
            Autonomous multi-agent approval gates, sensitive question prompts, and human-in-the-loop
            policies will activate in <strong className="text-foreground">Stage 14</strong>.
          </p>
        </div>

        <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
          <span className="text-[10px] text-foreground-muted font-mono-tech">
            Autonomy Guard: Normal
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={onNavigateToDiagnostics}
            className="h-7 text-xs text-accent-primary hover:text-accent-primary gap-1"
          >
            <span>Review Failed Tasks</span>
            <ArrowRight className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
