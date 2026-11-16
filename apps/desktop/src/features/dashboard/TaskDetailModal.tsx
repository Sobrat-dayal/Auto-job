import * as React from 'react';
import { useState, useEffect } from 'react';
import { AlertTriangle, Copy, Check, History, Terminal, StopCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse } from '@autonom/shared-types';
import type { TaskHistoryEvent } from '@/types/dashboard';

interface TaskDetailModalProps {
  task: TaskResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onCancelTask?: (taskId: string) => Promise<void>;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  task,
  isOpen,
  onClose,
  onCancelTask,
}) => {
  const [history, setHistory] = useState<TaskHistoryEvent[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    if (task && isOpen) {
      setIsLoadingHistory(true);
      const taskId = task.task_id || (task as any).id || '';
      apiClient
        .getTaskHistory(taskId)
        .then((res) => setHistory(res || []))
        .catch(() => setHistory([]))
        .finally(() => setIsLoadingHistory(false));
    } else {
      setHistory([]);
    }
  }, [task, isOpen]);

  if (!task) return null;

  const taskId = task.task_id || (task as any).id || '';

  const handleCopyId = () => {
    navigator.clipboard.writeText(taskId);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const handleCancel = async () => {
    if (!onCancelTask) return;
    setIsCancelling(true);
    try {
      await onCancelTask(taskId);
      onClose();
    } finally {
      setIsCancelling(false);
    }
  };

  const getStatusBadge = (state: string) => {
    switch (state) {
      case 'running':
        return (
          <Badge variant="cyan" dot pulse>
            RUNNING
          </Badge>
        );
      case 'queued':
        return (
          <Badge variant="warning" dot>
            QUEUED
          </Badge>
        );
      case 'completed':
        return (
          <Badge variant="success" dot>
            COMPLETED
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="error" dot>
            FAILED
          </Badge>
        );
      case 'cancelled':
        return (
          <Badge variant="neutral" dot>
            CANCELLED
          </Badge>
        );
      default:
        return (
          <Badge variant="neutral" dot>
            {state.toUpperCase()}
          </Badge>
        );
    }
  };

  const isEligibleForCancellation =
    task.state === 'running' || task.state === 'queued' || task.state === 'planning';

  // Calculate duration
  let durationStr = 'N/A';
  if (task.started_at && task.completed_at) {
    const diff =
      (new Date(task.completed_at).getTime() - new Date(task.started_at).getTime()) / 1000;
    durationStr = `${diff.toFixed(2)}s`;
  } else if (task.started_at) {
    const diff = (Date.now() - new Date(task.started_at).getTime()) / 1000;
    durationStr = `${diff.toFixed(1)}s (running)`;
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl bg-surface-elevated/95 backdrop-blur-md border border-border shadow-2xl p-6 text-foreground">
        <DialogHeader className="space-y-2 pb-3 border-b border-border/50">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-accent-primary" />
              <DialogTitle className="text-base font-bold text-foreground">
                Task Execution Details
              </DialogTitle>
            </div>
            {getStatusBadge(task.state)}
          </div>

          <DialogDescription className="text-xs text-foreground-muted">
            Durable task state, worker parameters, and SQLite transition ledger.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2 text-xs">
          {/* Identifiers & Meta */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded-lg bg-surface/60 border border-border/40">
            <div>
              <span className="text-[10px] text-foreground-muted uppercase font-mono-tech block">
                Task Identifier
              </span>
              <div className="flex items-center gap-2 mt-0.5">
                <code className="font-mono-tech text-accent-cyan text-xs truncate max-w-[220px]">
                  {taskId}
                </code>
                <button
                  onClick={handleCopyId}
                  className="p-1 rounded hover:bg-surface-elevated text-foreground-muted hover:text-foreground"
                  title="Copy Task ID"
                >
                  {copiedId ? (
                    <Check className="h-3 w-3 text-emerald-400" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <span className="text-[10px] text-foreground-muted uppercase font-mono-tech block">
                Handler Type
              </span>
              <span className="font-mono-tech font-semibold text-foreground mt-0.5 block">
                {task.task_type}
              </span>
            </div>

            <div>
              <span className="text-[10px] text-foreground-muted uppercase font-mono-tech block">
                Priority
              </span>
              <span className="font-mono-tech text-foreground capitalize mt-0.5 block">
                {task.priority || 'Normal'}
              </span>
            </div>

            <div>
              <span className="text-[10px] text-foreground-muted uppercase font-mono-tech block">
                Duration
              </span>
              <span className="font-mono-tech text-foreground mt-0.5 block">{durationStr}</span>
            </div>
          </div>

          {/* Progress message */}
          <div className="space-y-1.5 p-3 rounded-lg bg-surface/40 border border-border/30">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-foreground">
                Progress: {task.message || (task as any).progress_message || 'In progress'}
              </span>
              <span className="font-mono-tech text-[11px] text-accent-cyan font-bold">
                {Math.round(task.progress)}%
              </span>
            </div>
            <Progress value={task.progress} className="h-2 bg-surface" />
          </div>

          {/* Error Message if Failed */}
          {task.error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1">
              <div className="flex items-center gap-1.5 font-semibold text-rose-400">
                <AlertTriangle className="h-4 w-4" />
                <span>
                  Error (
                  {typeof task.error === 'object' && (task.error as any).code
                    ? (task.error as any).code
                    : 'FAILED'}
                  )
                </span>
              </div>
              <p className="text-[11px] font-mono-tech break-words">
                {typeof task.error === 'string'
                  ? task.error
                  : (task.error as any).message || String(task.error)}
              </p>
            </div>
          )}

          {/* Result Output if Completed */}
          {((task as any).result || (task as any).output) && (
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-mono-tech text-foreground-muted block">
                Execution Output
              </span>
              <pre className="p-3 rounded-lg bg-surface/70 border border-border/40 font-mono-tech text-[11px] text-foreground max-h-32 overflow-y-auto whitespace-pre-wrap">
                {JSON.stringify((task as any).result || (task as any).output, null, 2)}
              </pre>
            </div>
          )}

          {/* State History Ledger */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-1 text-[11px] font-semibold text-foreground">
              <History className="h-3.5 w-3.5 text-accent-cyan" />
              <span>Durable State Transitions (SQLite Ledger)</span>
            </div>

            {isLoadingHistory ? (
              <div className="py-4 text-center text-xs text-foreground-muted font-mono-tech">
                Loading audit events...
              </div>
            ) : history.length === 0 ? (
              <div className="p-3 rounded bg-surface/40 border border-border/30 text-[11px] text-foreground-muted">
                Initial enqueued state recorded.
              </div>
            ) : (
              <div className="max-h-36 overflow-y-auto border border-border/40 rounded-lg divide-y divide-border/30">
                {history.map((ev, idx) => (
                  <div
                    key={ev.id || idx}
                    className="p-2 flex items-center justify-between text-[11px]"
                  >
                    <div className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-accent-primary" />
                      <span className="font-mono-tech text-foreground">{ev.event_type}</span>
                      {ev.state_transition && (
                        <span className="text-foreground-muted text-[10px]">
                          ({ev.state_transition})
                        </span>
                      )}
                    </div>
                    <span className="text-foreground-muted font-mono-tech text-[10px]">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between pt-3 border-t border-border/50">
          <Button variant="outline" size="sm" onClick={onClose} className="text-xs">
            Close
          </Button>

          {isEligibleForCancellation && onCancelTask && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleCancel}
              disabled={isCancelling}
              isLoading={isCancelling}
              className="text-xs gap-1.5"
            >
              <StopCircle className="h-3.5 w-3.5" />
              <span>Cancel Task</span>
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
