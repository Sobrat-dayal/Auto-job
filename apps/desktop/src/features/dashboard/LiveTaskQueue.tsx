import * as React from 'react';
import { useState } from 'react';
import { Activity, RefreshCw, Clock, StopCircle, Eye, Terminal, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { TaskDetailModal } from './TaskDetailModal';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse } from '@autonom/shared-types';

interface LiveTaskQueueProps {
  tasks: TaskResponse[];
  isLoading: boolean;
  onRefresh: () => void;
  activeFilter?: string;
  onFilterChange?: (filter: string) => void;
  onNavigateToDiagnostics?: () => void;
}

export const LiveTaskQueue: React.FC<LiveTaskQueueProps> = ({
  tasks,
  isLoading,
  onRefresh,
  activeFilter = 'all',
  onFilterChange,
  onNavigateToDiagnostics,
}) => {
  const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  const filterTabs = [
    { id: 'all', label: 'All Tasks', count: tasks.length },
    { id: 'running', label: 'Running', count: tasks.filter((t) => t.state === 'running').length },
    { id: 'queued', label: 'Queued', count: tasks.filter((t) => t.state === 'queued').length },
    {
      id: 'completed',
      label: 'Completed',
      count: tasks.filter((t) => t.state === 'completed').length,
    },
    { id: 'failed', label: 'Failed', count: tasks.filter((t) => t.state === 'failed').length },
  ];

  const filteredTasks = tasks.filter((t) => {
    if (activeFilter === 'all') return true;
    return t.state.toLowerCase() === activeFilter.toLowerCase();
  });

  const handleInspect = (task: TaskResponse) => {
    setSelectedTask(task);
    setIsDetailOpen(true);
  };

  const handleCancelTask = async (taskId: string) => {
    setCancellingId(taskId);
    try {
      await apiClient.cancelTask(taskId);
      onRefresh();
    } catch (err) {
      console.error('Failed to cancel task:', err);
    } finally {
      setCancellingId(null);
    }
  };

  const getStatusBadge = (state: string) => {
    switch (state.toLowerCase()) {
      case 'running':
        return (
          <Badge variant="cyan" dot pulse className="text-[10px]">
            RUNNING
          </Badge>
        );
      case 'queued':
        return (
          <Badge variant="warning" dot className="text-[10px]">
            QUEUED
          </Badge>
        );
      case 'completed':
        return (
          <Badge variant="success" dot className="text-[10px]">
            COMPLETED
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="error" dot className="text-[10px]">
            FAILED
          </Badge>
        );
      case 'cancelled':
        return (
          <Badge variant="neutral" dot className="text-[10px]">
            CANCELLED
          </Badge>
        );
      default:
        return (
          <Badge variant="neutral" className="text-[10px]">
            {state.toUpperCase()}
          </Badge>
        );
    }
  };

  return (
    <>
      <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
        <CardHeader className="p-4 pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
                <Activity className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-sm font-semibold text-foreground">
                  Live Background Task Queue
                </CardTitle>
                <CardDescription className="text-[11px] text-foreground-muted">
                  Active execution queue and persistent task ledger from Stage 03/04
                </CardDescription>
              </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center gap-1 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
              {filterTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => onFilterChange?.(tab.id)}
                  className={`px-2.5 py-1 rounded text-xs transition-colors shrink-0 flex items-center gap-1.5 ${
                    activeFilter === tab.id
                      ? 'bg-accent-primary text-white font-medium shadow-sm'
                      : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated'
                  }`}
                >
                  <span>{tab.label}</span>
                  <span
                    className={`text-[10px] px-1 py-0.2 rounded-full font-mono-tech ${
                      activeFilter === tab.id
                        ? 'bg-white/20 text-white'
                        : 'bg-surface-elevated text-foreground-muted'
                    }`}
                  >
                    {tab.count}
                  </span>
                </button>
              ))}

              <Button
                variant="ghost"
                size="icon"
                onClick={onRefresh}
                disabled={isLoading}
                className="h-7 w-7 text-foreground-muted hover:text-foreground shrink-0 ml-1"
                title="Refresh Task Queue"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-4 pt-0">
          {filteredTasks.length === 0 ? (
            <div className="py-10 text-center rounded-lg border border-border/40 bg-surface/30 space-y-2">
              <Clock className="h-6 w-6 text-foreground-muted/60 mx-auto" />
              <p className="text-xs font-medium text-foreground">
                No {activeFilter !== 'all' ? activeFilter : ''} tasks found
              </p>
              <p className="text-[11px] text-foreground-muted max-w-sm mx-auto">
                Tasks dispatched by background workers or diagnostics will appear in this live
                queue.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto border border-border/40 rounded-lg">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-elevated/70 text-[10px] font-mono-tech uppercase text-foreground-muted border-b border-border/40">
                  <tr>
                    <th className="py-2 px-3">Task Handler</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Progress</th>
                    <th className="py-2 px-3 hidden md:table-cell">Created</th>
                    <th className="py-2 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30">
                  {filteredTasks.slice(0, 15).map((task) => {
                    const taskId = task.task_id || (task as any).id || '';
                    const isCancellable =
                      task.state === 'running' ||
                      task.state === 'queued' ||
                      task.state === 'planning';
                    const isBeingCancelled = cancellingId === taskId;

                    return (
                      <tr
                        key={taskId}
                        className="hover:bg-surface-elevated/30 transition-colors cursor-pointer group"
                        onClick={() => handleInspect(task)}
                      >
                        <td className="py-2.5 px-3">
                          <div className="flex items-center gap-2">
                            <Terminal className="h-3.5 w-3.5 text-accent-primary shrink-0" />
                            <div className="min-w-0">
                              <span className="font-mono-tech font-semibold text-foreground truncate block max-w-[160px] sm:max-w-none">
                                {task.task_type}
                              </span>
                              <span className="text-[10px] text-foreground-muted font-mono-tech truncate block">
                                {taskId.slice(0, 16)}...
                              </span>
                            </div>
                          </div>
                        </td>

                        <td className="py-2.5 px-3">{getStatusBadge(task.state)}</td>

                        <td className="py-2.5 px-3 min-w-[120px]">
                          <div className="space-y-1">
                            <div className="flex items-center justify-between text-[10px]">
                              <span className="text-foreground-muted truncate max-w-[100px]">
                                {task.message || (task as any).progress_message || 'Progress'}
                              </span>
                              <span className="font-mono-tech text-foreground font-semibold">
                                {Math.round(task.progress)}%
                              </span>
                            </div>
                            <Progress value={task.progress} className="h-1.5 bg-surface" />
                          </div>
                        </td>

                        <td className="py-2.5 px-3 hidden md:table-cell text-[11px] text-foreground-muted font-mono-tech">
                          {new Date(task.created_at).toLocaleTimeString()}
                        </td>

                        <td className="py-2.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleInspect(task)}
                              className="h-7 w-7 p-0 text-foreground-secondary hover:text-foreground"
                              title="Inspect Task Details"
                            >
                              <Eye className="h-3.5 w-3.5" />
                            </Button>

                            {isCancellable && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCancelTask(taskId)}
                                disabled={isBeingCancelled}
                                className="h-7 w-7 p-0 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
                                title="Cancel Task"
                              >
                                <StopCircle
                                  className={`h-3.5 w-3.5 ${isBeingCancelled ? 'animate-spin' : ''}`}
                                />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Footer note & link */}
          <div className="flex items-center justify-between pt-3 text-xs">
            <span className="text-[10px] text-foreground-muted font-mono-tech">
              Showing {filteredTasks.length} of {tasks.length} durable tasks
            </span>

            <Button
              variant="ghost"
              size="sm"
              onClick={onNavigateToDiagnostics}
              className="h-7 text-xs text-accent-primary hover:text-accent-primary gap-1"
            >
              <span>Full Task History & Dispatcher</span>
              <ExternalLink className="h-3 w-3" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Task Details Dialog */}
      <TaskDetailModal
        task={selectedTask}
        isOpen={isDetailOpen}
        onClose={() => {
          setIsDetailOpen(false);
          setSelectedTask(null);
        }}
        onCancelTask={handleCancelTask}
      />
    </>
  );
};
