import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, ShieldAlert, CheckCircle2, ArrowRight, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse, ApprovalRequest } from '@autonom/shared-types';

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
  const navigate = useNavigate();
  const [pendingApprovals, setPendingApprovals] = React.useState<ApprovalRequest[]>([]);

  React.useEffect(() => {
    let isMounted = true;
    const loadPending = async () => {
      try {
        const res = await apiClient.listApprovals({ status: 'pending' });
        if (isMounted) setPendingApprovals(res);
      } catch {
        // ignore errors
      }
    };
    loadPending();
    const interval = setInterval(loadPending, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const totalPending = failedTasks.length + pendingApprovals.length;

  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className={`flex h-8 w-8 items-center justify-center rounded-lg border ${
              pendingApprovals.length > 0
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse'
                : 'bg-primary/10 text-primary border-primary/20'
            }`}>
              <ShieldAlert className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Action Items & Authorization Gates
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                Operator approval requests, sensitive actions, and task exceptions
              </CardDescription>
            </div>
          </div>

          <Badge variant={totalPending > 0 ? 'warning' : 'outline'} className="text-[10px]">
            {totalPending > 0 ? `${totalPending} Pending` : 'All Clear'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-2.5">
        {totalPending === 0 ? (
          <div className="p-4 rounded-lg border border-border/40 bg-surface-elevated/20 text-center space-y-1">
            <CheckCircle2 className="h-5 w-5 text-emerald-400 mx-auto mb-1" />
            <p className="text-xs font-semibold text-foreground">No Pending Action Items</p>
            <p className="text-[11px] text-foreground-muted">
              All background workers, autonomous tasks, and tools are executing within approved policies.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5 max-h-40 overflow-y-auto">
            {/* Pending Approvals */}
            {pendingApprovals.map((appr) => (
              <div
                key={appr.id}
                onClick={() => navigate('/approvals')}
                className="p-2 rounded-lg border border-amber-500/40 bg-amber-500/10 hover:bg-amber-500/20 transition-colors cursor-pointer flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                  <div className="min-w-0">
                    <span className="font-semibold text-foreground truncate block font-mono text-[11px]">
                      Approval: {appr.capability_id}
                    </span>
                    <span className="text-[10px] text-amber-200 truncate block">
                      {appr.reason}
                    </span>
                  </div>
                </div>

                <Badge variant="warning" className="text-[9px] shrink-0 font-mono-tech uppercase">
                  {appr.risk_level}
                </Badge>
              </div>
            ))}

            {/* Failed Tasks */}
            {failedTasks.slice(0, 3).map((task) => (
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

        <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
          {pendingApprovals.length > 0 ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/approvals')}
              className="h-7 text-xs border-amber-500/40 text-amber-300 hover:bg-amber-500/10 gap-1"
            >
              <span>Review Approvals ({pendingApprovals.length})</span>
              <ArrowRight className="h-3 w-3" />
            </Button>
          ) : (
            <span className="text-[10px] text-foreground-muted font-mono-tech flex items-center gap-1">
              <ShieldCheck className="h-3 w-3 text-emerald-400" />
              Authorization: Active
            </span>
          )}

          {failedTasks.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onNavigateToDiagnostics}
              className="h-7 text-xs text-accent-primary hover:text-accent-primary gap-1"
            >
              <span>Review Tasks</span>
              <ArrowRight className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
