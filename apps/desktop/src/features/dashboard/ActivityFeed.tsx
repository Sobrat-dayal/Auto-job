import * as React from 'react';
import { useState } from 'react';
import { Radio, Activity, CheckCircle2, AlertTriangle, Clock, Cpu, Trash2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { EventEnvelope } from '@autonom/shared-types';
import type { EventStreamStatus } from '@/hooks/use-dashboard';

interface ActivityFeedProps {
  events: EventEnvelope[];
  streamStatus: EventStreamStatus;
  onClear?: () => void;
  onSelectTask?: (taskId: string) => void;
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({
  events,
  streamStatus,
  onClear,
  onSelectTask,
}) => {
  const [filter, setFilter] = useState<'all' | 'tasks' | 'workers' | 'system'>('all');

  const filteredEvents = events.filter((ev) => {
    if (filter === 'tasks') return ev.event_type.startsWith('task.');
    if (filter === 'workers') return ev.event_type.startsWith('worker.');
    if (filter === 'system') return ev.event_type.startsWith('system.');
    return true;
  });

  const getEventIcon = (type: string) => {
    if (type.includes('completed'))
      return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />;
    if (type.includes('failed'))
      return <AlertTriangle className="h-3.5 w-3.5 text-rose-500 shrink-0" />;
    if (type.includes('worker')) return <Cpu className="h-3.5 w-3.5 text-accent-cyan shrink-0" />;
    if (type.includes('system'))
      return <Activity className="h-3.5 w-3.5 text-accent-primary shrink-0" />;
    return <Clock className="h-3.5 w-3.5 text-accent-primary shrink-0" />;
  };

  const getEventSummary = (ev: EventEnvelope) => {
    const payload = ev.payload as Record<string, unknown> | undefined;
    if (ev.event_type === 'task.progress' && payload?.message) {
      return String(payload.message);
    }
    if (ev.event_type === 'task.state_changed' && payload?.new_state) {
      return `Transitioned to state: ${String(payload.new_state).toUpperCase()}`;
    }
    if (ev.event_type === 'task.completed') {
      return 'Task completed execution successfully.';
    }
    if (ev.event_type === 'task.failed') {
      return payload?.error
        ? String((payload.error as any).message || 'Execution error')
        : 'Task execution failed.';
    }
    if (ev.event_type === 'task.cancelled') {
      return 'Task cooperatively cancelled by operator.';
    }
    if (ev.event_type === 'system.started') {
      return 'Backend service initialized and event bus online.';
    }
    if (ev.event_type === 'worker.started') {
      return `Worker started: ${payload?.worker_id || 'thread'}`;
    }
    return payload ? JSON.stringify(payload).slice(0, 80) : ev.event_type;
  };

  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
              <Radio className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Real-Time Event Stream
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                Live SSE dispatch feed with client-side deduplication
              </CardDescription>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Stream Connection Pill */}
            <Badge
              variant={
                streamStatus === 'connected'
                  ? 'success'
                  : streamStatus === 'connecting'
                    ? 'warning'
                    : 'error'
              }
              dot
              pulse={streamStatus === 'connected' || streamStatus === 'connecting'}
              className="text-[10px] font-mono-tech"
            >
              {streamStatus === 'connected'
                ? 'LIVE SSE (8765)'
                : streamStatus === 'connecting'
                  ? 'CONNECTING...'
                  : 'DISCONNECTED'}
            </Badge>

            {onClear && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClear}
                className="h-7 w-7 text-foreground-muted hover:text-foreground"
                title="Clear Activity Feed"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 pt-2 border-t border-border/30">
          {(['all', 'tasks', 'workers', 'system'] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-2 py-0.5 rounded text-[11px] transition-colors capitalize ${
                filter === cat
                  ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/40 font-medium'
                  : 'text-foreground-muted hover:text-foreground hover:bg-surface-elevated/40'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-0">
        {filteredEvents.length === 0 ? (
          <div className="py-12 text-center rounded-lg border border-border/40 bg-surface/30 space-y-1.5">
            <Radio className="h-6 w-6 text-foreground-muted/60 mx-auto animate-pulse" />
            <p className="text-xs font-medium text-foreground">
              Awaiting live background events...
            </p>
            <p className="text-[10px] text-foreground-muted font-mono-tech">
              Connected to loopback SSE stream at 127.0.0.1:8765
            </p>
          </div>
        ) : (
          <div className="max-h-[320px] overflow-y-auto space-y-1.5 pr-1 scrollbar-thin">
            {filteredEvents.map((ev, idx) => (
              <div
                key={ev.event_id || `${ev.event_type}-${idx}`}
                onClick={() => ev.task_id && onSelectTask?.(ev.task_id)}
                className={`p-2 rounded-lg border border-border/40 bg-surface/60 hover:bg-surface-elevated/50 transition-colors flex items-start justify-between gap-3 text-xs ${
                  ev.task_id ? 'cursor-pointer' : ''
                }`}
              >
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className="mt-0.5">{getEventIcon(ev.event_type)}</div>
                  <div className="space-y-0.5 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-mono-tech font-semibold text-[11px] text-foreground">
                        {ev.event_type}
                      </span>
                      {ev.task_id && (
                        <span className="text-[9px] font-mono-tech text-accent-cyan bg-accent-cyan/10 px-1 rounded border border-accent-cyan/20 truncate max-w-[120px]">
                          {ev.task_id.slice(0, 10)}...
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-foreground-secondary break-words line-clamp-2">
                      {getEventSummary(ev)}
                    </p>
                  </div>
                </div>

                <span className="text-[10px] text-foreground-muted font-mono-tech shrink-0 mt-0.5">
                  {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="pt-2 text-[10px] text-foreground-muted font-mono-tech flex items-center justify-between">
          <span>{filteredEvents.length} events in memory</span>
          <span>Bounded buffer (max 100)</span>
        </div>
      </CardContent>
    </Card>
  );
};
