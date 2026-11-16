import React, { useEffect, useRef, useState } from 'react';
import {
  Activity,
  Play,
  Square,
  RefreshCw,
  Cpu,
  Radio,
  Layers,
  Terminal,
  Clock,
  Trash2,
  Sliders,
} from 'lucide-react';
import type {
  EventEnvelope,
  SystemStatusResponse,
  TaskResponse,
  TaskResultResponse,
  WorkerListResponse,
} from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { PageContainer } from '@/components/layout/PageContainer';
import { SectionHeader } from '@/components/layout/SectionHeader';
import { MetricCard } from '@/components/data-display/MetricCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export const Diagnostics: React.FC = () => {
  // Live SSE Events
  const [events, setEvents] = useState<EventEnvelope[]>([]);
  const [sseConnected, setSseConnected] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // System & Worker Status
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);
  const [workers, setWorkers] = useState<WorkerListResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Task Dispatcher State
  const [taskType, setTaskType] = useState<string>('test.sleep_progress');
  const [echoMessage, setEchoMessage] = useState<string>(
    'AUTONOM Stage 06 execution pipeline active.'
  );
  const [durationSeconds, setDurationSeconds] = useState<number>(5);
  const [stepsCount, setStepsCount] = useState<number>(5);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Active / Selected Task Execution Tracker
  const [activeTask, setActiveTask] = useState<TaskResponse | null>(null);
  const [taskResult, setTaskResult] = useState<TaskResultResponse | null>(null);
  const [executionMessage, setExecutionMessage] = useState<string>('');

  // Fetch status and worker pool
  const fetchStatus = async () => {
    setIsRefreshing(true);
    try {
      const [sys, wrk] = await Promise.all([apiClient.getSystemStatus(), apiClient.getWorkers()]);
      setSystemStatus(sys);
      setWorkers(wrk);
    } catch {
      // Backend might be offline
    } finally {
      setIsRefreshing(false);
    }
  };

  // Connect to SSE stream on mount
  useEffect(() => {
    fetchStatus();

    // Fetch initial recent events
    apiClient
      .getRecentEvents(30)
      .then((recent) => {
        if (recent && recent.length > 0) {
          setEvents(recent);
        }
      })
      .catch(() => {});

    const streamUrl = apiClient.getEventStreamUrl();
    const es = new EventSource(streamUrl);
    eventSourceRef.current = es;

    es.onopen = () => {
      setSseConnected(true);
    };

    es.onmessage = (event) => {
      try {
        const parsed: EventEnvelope = JSON.parse(event.data);
        setEvents((prev) => [parsed, ...prev.slice(0, 199)]);

        // Live update active task if matching
        if (parsed.task_id && activeTask && parsed.task_id === activeTask.task_id) {
          if (parsed.event_type === 'task.progress') {
            const progressPayload = parsed.payload as { progress?: number; message?: string };
            if (typeof progressPayload.progress === 'number') {
              setActiveTask((prev) =>
                prev ? { ...prev, progress: progressPayload.progress! } : null
              );
            }
            if (progressPayload.message) {
              setExecutionMessage(progressPayload.message);
            }
          } else if (parsed.event_type === 'task.state_changed') {
            const statePayload = parsed.payload as { new_state?: string };
            if (statePayload.new_state) {
              setActiveTask((prev) =>
                prev ? { ...prev, state: statePayload.new_state as any } : null
              );
            }
          } else if (
            parsed.event_type === 'task.completed' ||
            parsed.event_type === 'task.failed' ||
            parsed.event_type === 'task.cancelled'
          ) {
            // Fetch final result
            apiClient
              .getTaskResult(parsed.task_id)
              .then(setTaskResult)
              .catch(() => {});
            fetchStatus();
          }
        }
      } catch {
        // Ping or malformed event
      }
    };

    es.onerror = () => {
      setSseConnected(false);
    };

    const interval = setInterval(fetchStatus, 3000);

    return () => {
      clearInterval(interval);
      es.close();
    };
  }, [activeTask?.task_id]);

  const handleDispatchTask = async () => {
    setIsSubmitting(true);
    setTaskResult(null);
    setExecutionMessage('Submitting task...');

    try {
      const payload: Record<string, unknown> =
        taskType === 'compute.echo'
          ? { message: echoMessage }
          : { duration_seconds: durationSeconds, steps: stepsCount };

      const task = await apiClient.createTask({
        task_type: taskType,
        payload,
        priority: 'normal',
      });

      setActiveTask(task);
      setExecutionMessage(`Task ${task.task_id.slice(0, 8)} queued.`);
      fetchStatus();
    } catch (err) {
      setExecutionMessage(err instanceof Error ? err.message : 'Task dispatch failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelTask = async () => {
    if (!activeTask) return;
    try {
      setExecutionMessage('Cancelling task...');
      await apiClient.cancelTask(activeTask.task_id);
      fetchStatus();
    } catch (err) {
      setExecutionMessage(err instanceof Error ? err.message : 'Cancellation failed');
    }
  };

  const clearEventLog = () => {
    setEvents([]);
  };

  const renderTaskStateBadge = (state: string) => {
    switch (state) {
      case 'completed':
        return (
          <Badge variant="success" dot>
            COMPLETED
          </Badge>
        );
      case 'running':
        return (
          <Badge variant="cyan" dot pulse>
            RUNNING
          </Badge>
        );
      case 'cancelled':
        return (
          <Badge variant="warning" dot>
            CANCELLED
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="error" dot>
            FAILED
          </Badge>
        );
      case 'queued':
      default:
        return (
          <Badge variant="primary" dot>
            QUEUED
          </Badge>
        );
    }
  };

  return (
    <PageContainer
      title="Backend Diagnostics & Real-Time Tasks"
      subtitle="Real-time event streaming (SSE), asynchronous worker pool, task state machine, and cooperative cancellation"
      badge={
        <Badge variant={sseConnected ? 'success' : 'error'} dot pulse={sseConnected}>
          SSE {sseConnected ? 'Connected' : 'Offline'}
        </Badge>
      }
      actions={
        <Button
          variant="outline"
          size="sm"
          onClick={fetchStatus}
          disabled={isRefreshing}
          isLoading={isRefreshing}
          loadingText="Refreshing..."
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh
        </Button>
      }
    >
      {/* Metrics Row: Workers, Queue, Uptime */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3.5">
        <MetricCard
          title="Worker Pool"
          value={workers?.active_workers ?? 0}
          subtitle={`/ ${workers?.max_capacity ?? 4} active (${workers?.idle_workers ?? 0} idle)`}
          icon={<Cpu className="w-4 h-4" />}
          variant="primary"
        />

        <MetricCard
          title="Queue Saturation"
          value={systemStatus?.tasks.queued ?? 0}
          subtitle={`/ 50 capacity (${systemStatus?.tasks.active ?? 0} running)`}
          icon={<Layers className="w-4 h-4" />}
          variant="cyan"
        />

        <MetricCard
          title="Backend Uptime"
          value={systemStatus ? `${Math.floor(systemStatus.uptime_seconds)}s` : '0s'}
          subtitle={`FastAPI v${systemStatus?.version ?? '0.1.0'}`}
          icon={<Clock className="w-4 h-4" />}
          variant="success"
        />

        <MetricCard
          title="Event Stream"
          value={events.length}
          subtitle="Ring buffer history (200 max)"
          icon={<Activity className="w-4 h-4" />}
          variant="default"
        />
      </div>

      {/* Task Dispatcher & Execution Controller */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Task Dispatch Form */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-4">
          <SectionHeader
            title="Interactive Task Dispatcher"
            subtitle="Asynchronous execution and telemetry verification"
            icon={<Sliders className="w-4 h-4 text-primary" />}
          />

          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Task Handler</label>
              <Select value={taskType} onValueChange={setTaskType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select task type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="test.sleep_progress">
                    test.sleep_progress (Progress Simulation)
                  </SelectItem>
                  <SelectItem value="compute.echo">compute.echo (Synchronous Execution)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {taskType === 'test.sleep_progress' ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-compact-label text-foreground-secondary">
                    Duration (seconds)
                  </label>
                  <Input
                    type="number"
                    min={1}
                    max={30}
                    value={durationSeconds}
                    onChange={(e) => setDurationSeconds(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-compact-label text-foreground-secondary">Steps</label>
                  <Input
                    type="number"
                    min={1}
                    max={20}
                    value={stepsCount}
                    onChange={(e) => setStepsCount(Number(e.target.value))}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-1.5">
                <label className="text-compact-label text-foreground-secondary">
                  Payload Message
                </label>
                <Input
                  type="text"
                  value={echoMessage}
                  onChange={(e) => setEchoMessage(e.target.value)}
                />
              </div>
            )}

            <div className="pt-2">
              <Button
                variant="primary"
                onClick={handleDispatchTask}
                disabled={isSubmitting}
                isLoading={isSubmitting}
                loadingText="Dispatching..."
                className="w-full"
              >
                <Play className="w-3.5 h-3.5 mr-1.5 fill-current" />
                Dispatch Task to Worker Pool
              </Button>
            </div>
          </div>
        </div>

        {/* Live Execution Status & Controls */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-4">
          <SectionHeader
            title="Live Execution Monitor"
            subtitle={
              activeTask
                ? `Active Task: ${activeTask.task_id.slice(0, 8)}`
                : 'Awaiting task dispatch'
            }
            icon={<Terminal className="w-4 h-4 text-cyan" />}
          />

          {activeTask ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-foreground-secondary">Execution State:</span>
                {renderTaskStateBadge(activeTask.state)}
              </div>

              {/* Progress bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-foreground-secondary">Progress</span>
                  <span className="font-tabular font-semibold text-foreground">
                    {Math.round(activeTask.progress * 100)}%
                  </span>
                </div>
                <Progress value={Math.round(activeTask.progress * 100)} variant="cyan" />
              </div>

              {executionMessage && (
                <div className="p-2.5 bg-surface-elevated rounded border border-border text-[11px] font-mono-tech text-foreground-secondary">
                  {executionMessage}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-1">
                {(activeTask.state === 'running' || activeTask.state === 'queued') && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleCancelTask}
                    className="w-full"
                  >
                    <Square className="w-3.5 h-3.5 mr-1.5 fill-current" />
                    Cancel Task (Cooperative)
                  </Button>
                )}
              </div>

              {/* Result Preview */}
              {taskResult && (
                <div className="p-2.5 bg-surface-elevated rounded border border-border space-y-1.5 text-xs font-mono-tech">
                  <div className="text-foreground-secondary font-semibold text-[11px]">
                    Execution Result:
                  </div>
                  <pre className="text-status-success text-[11px] overflow-x-auto max-h-32">
                    {JSON.stringify(taskResult.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="h-44 flex flex-col items-center justify-center text-foreground-muted text-xs text-center space-y-2">
              <Activity className="w-8 h-8 text-foreground-muted animate-pulse" />
              <span>
                No task currently being monitored. Dispatch a task above to watch real-time
                execution.
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Real-Time Event Stream Log */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <SectionHeader
            title="Live Event Stream (SSE / Server-Sent Events)"
            subtitle="Ring buffer event stream published by the backend EventBus in real time"
            icon={<Radio className="w-4 h-4 text-status-success" />}
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={clearEventLog}
            className="text-foreground-secondary hover:text-foreground"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1.5" />
            Clear
          </Button>
        </div>

        <div className="overflow-x-auto max-h-64 overflow-y-auto font-mono-tech text-xs border border-border rounded-md bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-surface-secondary/60 text-foreground-muted text-[11px]">
                <th className="p-2">Timestamp</th>
                <th className="p-2">Event Type</th>
                <th className="p-2">Task ID</th>
                <th className="p-2">Payload Summary</th>
              </tr>
            </thead>
            <tbody>
              {events.length > 0 ? (
                events.map((evt, idx) => (
                  <tr
                    key={`${evt.event_id}-${idx}`}
                    className="border-b border-border/40 hover:bg-surface-hover text-[11px] transition-colors"
                  >
                    <td className="p-2 text-foreground-muted whitespace-nowrap">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <Badge
                        variant={
                          evt.event_type.startsWith('task.progress')
                            ? 'cyan'
                            : evt.event_type.startsWith('task.completed')
                              ? 'success'
                              : evt.event_type.startsWith('task.cancelled') ||
                                  evt.event_type.startsWith('task.failed')
                                ? 'error'
                                : evt.event_type.startsWith('worker.')
                                  ? 'warning'
                                  : 'primary'
                        }
                        className="text-[10px] py-0 px-1.5 font-mono-tech"
                      >
                        {evt.event_type}
                      </Badge>
                    </td>
                    <td className="p-2 text-foreground-secondary font-mono-tech whitespace-nowrap">
                      {evt.task_id ? evt.task_id.slice(0, 8) : '—'}
                    </td>
                    <td className="p-2 text-foreground-muted truncate max-w-xs">
                      {JSON.stringify(evt.payload)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-foreground-muted text-xs">
                    No events received yet. Events published on the backend EventBus appear here in
                    real-time.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </PageContainer>
  );
};
