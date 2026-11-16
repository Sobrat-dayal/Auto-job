# AUTONOM — Real-Time SSE Event Streaming & Deduplication (Stage 08)

## 1. Event Streaming Architecture

Real-time telemetry and task status synchronization in AUTONOM uses Server-Sent Events (SSE) over loopback HTTP:

```
+---------------------------+                      +-----------------------------------+
|      FastAPI Backend      |                      |           React Desktop           |
| (services/api/app)        |                      | (apps/desktop/src)                |
|                           |                      |                                   |
|   Internal EventBus       |                      |   useLiveEventStream Hook         |
|   (asyncio.Queue)         |                      |                                   |
|          |                |                      |          |                        |
|   SSE Streaming Endpoint  |  GET /api/v1/events  |    EventSource Listener           |
|   (StreamingResponse)     |=====================>|    (127.0.0.1:8765/api/v1/...)    |
|                           |  text/event-stream   |          |                        |
+---------------------------+                      |    Client Deduplication Set       |
                                                   |    (Bounded LRU 500 IDs)          |
                                                   |          |                        |
                                                   |    TanStack Query Invalidator     |
                                                   |    ['dashboard-overview']         |
                                                   |    ['dashboard-tasks']            |
                                                   |          |                        |
                                                   |    Activity Feed State            |
                                                   |    (Bounded Buffer 100 entries)   |
                                                   +-----------------------------------+
```

---

## 2. Event Envelope Specification

Events emitted over the stream conform to the `EventEnvelope` model:

```json
{
  "event_id": "c7a88fc2-921d-4001-a189-e15a78283301",
  "event_type": "task.progress",
  "timestamp": "2026-11-16T22:25:03.123456Z",
  "payload": {
    "task_id": "8a067a90-7d6f-4221-a02e-9d854ce695ec",
    "task_type": "test.sleep_progress",
    "progress": 75,
    "message": "Completed step 3 of 4"
  }
}
```

### Standard Event Categories

- `task.*`: `task.created`, `task.state_changed`, `task.progress`, `task.completed`, `task.failed`, `task.cancelled`.
- `worker.*`: `worker.started`, `worker.completed`, `worker.idle`, `worker.busy`.
- `system.*`: `system.started`, `system.ready`, `system.heartbeat`, `system.shutting_down`.

---

## 3. Client-Side Deduplication & Cache Invalidation

Implemented in `apps/desktop/src/hooks/use-dashboard.ts` via `useLiveEventStream`:

### 3.1 Bounded Set Deduplication

```typescript
const eventId = parsed.event_id || `${parsed.event_type}-${parsed.timestamp}`;

if (seenIdsRef.current.has(eventId)) {
  return;
}
seenIdsRef.current.add(eventId);

// Maintain bounded memory (max 500 IDs)
if (seenIdsRef.current.size > 500) {
  const arr = Array.from(seenIdsRef.current);
  seenIdsRef.current = new Set(arr.slice(arr.length - 250));
}
```

### 3.2 Selective Cache Reconciliation

When task state events arrive (`task.created`, `task.completed`, `task.failed`, `task.cancelled`), TanStack Query query keys are immediately invalidated:

- `['dashboard-overview']`
- `['dashboard-tasks']`
- `['dashboard-task-trends']`

This provides instantaneous UI updates without high-frequency polling loops.

---

## 4. Reconnection & Recovery Behavior

1. **Connection Drop**: When the backend terminates or restarts, the browser `EventSource` automatically attempts reconnection.
2. **Exponential Backoff**: If `onerror` fires, the hook transitions state to `disconnected` and schedules a reconnect attempt.
3. **Cache Invalidation on Reconnect**: On `es.onopen`, the hook immediately invalidates all dashboard queries to reconcile state accumulated while offline.
