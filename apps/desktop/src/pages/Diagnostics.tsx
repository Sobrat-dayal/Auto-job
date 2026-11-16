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
    'AUTONOM Stage 03 execution pipeline active.'
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

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto overflow-y-auto">
      {/* Header Banner */}
      <div className="border-b border-border pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span>Backend Diagnostics & Real-Time Tasks</span>
            <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary-light border border-primary/30 font-mono font-normal">
              Stage 03 Active
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time event streaming (SSE), asynchronous worker pool, task state machine, and
            cooperative cancellation.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono border ${
              sseConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}
          >
            <Radio className={`w-3 h-3 ${sseConnected ? 'animate-pulse text-emerald-400' : ''}`} />
            <span>SSE {sseConnected ? 'Connected' : 'Offline'}</span>
          </div>

          <button
            onClick={fetchStatus}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-elevated hover:bg-slate-700 text-slate-200 text-xs font-medium border border-border transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Metrics Row: Workers, Queue, Uptime */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-primary-light" />
            Worker Pool
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-100">
              {workers?.active_workers ?? 0}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              / {workers?.max_capacity ?? 4} active
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            {workers?.idle_workers ?? 0} idle workers ready
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-cyan" />
            Queue Saturation
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-100">
              {systemStatus?.tasks.queued ?? 0}
            </span>
            <span className="text-xs text-slate-400 font-mono">/ 50 capacity</span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            {systemStatus?.tasks.active ?? 0} running concurrently
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-emerald-400" />
            Backend Uptime
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-100">
              {systemStatus ? Math.floor(systemStatus.uptime_seconds) : 0}s
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            Version {systemStatus?.version ?? '0.1.0'}
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-amber-400" />
            Event Stream
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-slate-100">{events.length}</span>
            <span className="text-xs text-slate-400 font-mono">buffered events</span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            Ring buffer history (200 max)
          </div>
        </div>
      </div>

      {/* Task Dispatcher & Execution Controller */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Task Dispatch Form */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-primary-light" />
              Interactive Task Dispatcher
            </span>
            <span className="text-xs font-mono text-cyan">Async Execution</span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Task Handler</label>
              <select
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-primary-light font-mono"
              >
                <option value="test.sleep_progress">
                  test.sleep_progress (Progress Simulation)
                </option>
                <option value="compute.echo">compute.echo (Synchronous Execution)</option>
              </select>
            </div>

            {taskType === 'test.sleep_progress' ? (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Duration (s)
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    value={durationSeconds}
                    onChange={(e) => setDurationSeconds(Number(e.target.value))}
                    className="w-full bg-surface-elevated border border-border rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-primary-light font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Steps</label>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={stepsCount}
                    onChange={(e) => setStepsCount(Number(e.target.value))}
                    className="w-full bg-surface-elevated border border-border rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-primary-light font-mono"
                  />
                </div>
              </div>
            ) : (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Payload Message
                </label>
                <input
                  type="text"
                  value={echoMessage}
                  onChange={(e) => setEchoMessage(e.target.value)}
                  className="w-full bg-surface-elevated border border-border rounded px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-primary-light font-mono"
                />
              </div>
            )}

            <div className="pt-2">
              <button
                onClick={handleDispatchTask}
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 py-2 rounded bg-primary hover:bg-primary-hover text-white text-xs font-medium transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isSubmitting ? 'Dispatching...' : 'Dispatch Task to Worker Pool'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Live Execution Status & Controls */}
        <div className="p-4 rounded-lg bg-surface border border-border space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan" />
              Live Execution Monitor
            </span>
            {activeTask && (
              <span className="text-xs font-mono text-slate-400">
                ID: {activeTask.task_id.slice(0, 8)}
              </span>
            )}
          </div>

          {activeTask ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-slate-400">Status:</span>
                <span
                  className={`px-2 py-0.5 rounded font-semibold uppercase ${
                    activeTask.state === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : activeTask.state === 'running'
                        ? 'bg-primary/20 text-cyan border border-primary/30 animate-pulse'
                        : activeTask.state === 'cancelled'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-700 text-slate-300'
                  }`}
                >
                  {activeTask.state}
                </span>
              </div>

              {/* Progress bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono text-slate-400">
                  <span>Progress</span>
                  <span className="text-slate-200">{Math.round(activeTask.progress * 100)}%</span>
                </div>
                <div className="w-full bg-surface-elevated rounded-full h-2 overflow-hidden border border-border">
                  <div
                    className="bg-cyan h-2 transition-all duration-300 rounded-full"
                    style={{ width: `${Math.round(activeTask.progress * 100)}%` }}
                  />
                </div>
              </div>

              {executionMessage && (
                <div className="p-2 bg-surface-elevated rounded border border-border text-[11px] font-mono text-slate-300">
                  {executionMessage}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                {activeTask.state === 'running' || activeTask.state === 'queued' ? (
                  <button
                    onClick={handleCancelTask}
                    className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-xs font-medium transition-colors"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    <span>Cancel Task (Cooperative)</span>
                  </button>
                ) : null}
              </div>

              {/* Result Preview */}
              {taskResult && (
                <div className="p-2.5 bg-surface-elevated rounded border border-border space-y-1.5 text-xs font-mono">
                  <div className="text-slate-400 font-semibold text-[11px]">Execution Result:</div>
                  <pre className="text-emerald-400 text-[11px] overflow-x-auto max-h-32">
                    {JSON.stringify(taskResult.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="h-44 flex flex-col items-center justify-center text-slate-500 text-xs text-center space-y-2">
              <Activity className="w-8 h-8 text-slate-600 animate-pulse" />
              <span>
                No task currently being monitored. Dispatch a task to watch real-time execution.
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Real-Time Event Stream Log */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-400" />
            Live Event Stream (SSE / Server-Sent Events)
          </span>
          <button
            onClick={clearEventLog}
            className="flex items-center gap-1 px-2 py-1 rounded bg-surface-elevated hover:bg-slate-700 text-slate-400 text-xs font-mono border border-border transition-colors"
          >
            <Trash2 className="w-3 h-3" />
            <span>Clear</span>
          </button>
        </div>

        <div className="overflow-x-auto max-h-64 overflow-y-auto font-mono text-xs border border-border rounded bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-slate-800/50 text-slate-400 text-[11px]">
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
                    className="border-b border-border/50 hover:bg-slate-800/30 text-[11px]"
                  >
                    <td className="p-2 text-slate-400 whitespace-nowrap">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          evt.event_type.startsWith('task.progress')
                            ? 'bg-cyan/10 text-cyan border border-cyan/20'
                            : evt.event_type.startsWith('task.completed')
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : evt.event_type.startsWith('task.cancelled') ||
                                  evt.event_type.startsWith('task.failed')
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : evt.event_type.startsWith('worker.')
                                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                  : 'bg-primary/10 text-primary-light border border-primary/20'
                        }`}
                      >
                        {evt.event_type}
                      </span>
                    </td>
                    <td className="p-2 text-slate-300 font-mono whitespace-nowrap">
                      {evt.task_id ? evt.task_id.slice(0, 8) : '—'}
                    </td>
                    <td className="p-2 text-slate-400 truncate max-w-xs">
                      {JSON.stringify(evt.payload)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-slate-500 text-xs">
                    No events received yet. Events published on the backend EventBus appear here in
                    real-time.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
