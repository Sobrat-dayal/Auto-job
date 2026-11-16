import { useEffect, useRef, useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { EventEnvelope, TaskResponse } from '@autonom/shared-types';
import type { DashboardOverviewResponse, DashboardTaskTrendsResponse } from '@/types/dashboard';

export type EventStreamStatus = 'connected' | 'connecting' | 'disconnected';

export interface UseDashboardOverviewOptions {
  refetchInterval?: number;
}

export function useDashboardOverview(options: UseDashboardOverviewOptions = {}) {
  const { refetchInterval = 4000 } = options;

  return useQuery<DashboardOverviewResponse, Error>({
    queryKey: ['dashboard-overview'],
    queryFn: () => apiClient.getDashboardOverview(),
    refetchInterval,
    staleTime: 2000,
  });
}

export function useDashboardTaskTrends(window: 'today' | '7d' | '30d' = '7d') {
  return useQuery<DashboardTaskTrendsResponse, Error>({
    queryKey: ['dashboard-task-trends', window],
    queryFn: () => apiClient.getDashboardTaskTrends(window),
    staleTime: 5000,
  });
}

export interface UseDashboardTasksOptions {
  limit?: number;
  state?: string;
}

export function useDashboardTasks(options: UseDashboardTasksOptions = {}) {
  const { limit = 50 } = options;

  return useQuery<TaskResponse[], Error>({
    queryKey: ['dashboard-tasks', limit],
    queryFn: async () => {
      const res = await apiClient.listTasks();
      return res.tasks || [];
    },
    refetchInterval: 3000,
    staleTime: 2000,
  });
}

export function useLiveEventStream(maxEvents: number = 100) {
  const queryClient = useQueryClient();
  const [events, setEvents] = useState<EventEnvelope[]>([]);
  const [status, setStatus] = useState<EventStreamStatus>('connecting');
  const seenIdsRef = useRef<Set<string>>(new Set());
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (typeof EventSource === 'undefined') {
      setStatus('disconnected');
      return;
    }

    setStatus('connecting');
    const url = apiClient.getEventStreamUrl();
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => {
      setStatus('connected');
      // Reconcile authoritative queries on reconnect
      queryClient.invalidateQueries({ queryKey: ['dashboard-overview'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-tasks'] });
    };

    es.onmessage = (event) => {
      try {
        const parsed: EventEnvelope = JSON.parse(event.data);
        const eventId = parsed.event_id || `${parsed.event_type}-${parsed.timestamp}`;

        // Deduplication
        if (seenIdsRef.current.has(eventId)) {
          return;
        }
        seenIdsRef.current.add(eventId);

        // Keep seen set bounded
        if (seenIdsRef.current.size > 500) {
          const arr = Array.from(seenIdsRef.current);
          seenIdsRef.current = new Set(arr.slice(arr.length - 250));
        }

        setEvents((prev) => [parsed, ...prev.slice(0, maxEvents - 1)]);

        // Targeted cache invalidation based on event domain
        if (parsed.event_type.startsWith('task.')) {
          queryClient.invalidateQueries({ queryKey: ['dashboard-overview'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard-tasks'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard-task-trends'] });
        } else if (parsed.event_type.startsWith('worker.')) {
          queryClient.invalidateQueries({ queryKey: ['dashboard-overview'] });
        } else if (parsed.event_type.startsWith('system.')) {
          queryClient.invalidateQueries({ queryKey: ['dashboard-overview'] });
        }
      } catch {
        // Ignore unparseable frames
      }
    };

    es.onerror = () => {
      setStatus('disconnected');
      if (es.readyState === EventSource.CLOSED) {
        es.close();
        eventSourceRef.current = null;
        // Exponential/bounded retry after 3 seconds
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, 3000);
        }
      }
    };
  }, [queryClient, maxEvents]);

  useEffect(() => {
    // Initial fetch of recent persisted events
    apiClient
      .getRecentEvents(25)
      .then((recent) => {
        if (recent && recent.length > 0) {
          for (const ev of recent) {
            const evId = ev.event_id || `${ev.event_type}-${ev.timestamp}`;
            seenIdsRef.current.add(evId);
          }
          setEvents(recent);
        }
      })
      .catch(() => {});

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [connect]);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return {
    events,
    status,
    clearEvents,
  };
}
