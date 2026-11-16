# AUTONOM — Real-Time Event System & Streaming (Stage 03)

This document specifies the internal publish-subscribe Event Bus, Server-Sent Events (SSE) streaming protocol, subscriber isolation, and event ring buffering in **AUTONOM**.

---

## 1. Event Bus Architecture

AUTONOM implements an in-memory asynchronous `EventBus` (`app/events/bus.py`) designed for zero-latency communication between agent execution workers, background managers, and desktop UI clients.

```mermaid
graph LR
    subgraph Producers
        TM[Task Execution Manager]
        WM[Worker Manager]
        Sys[System Lifespan]
    end

    EB[EventBus (Asyncio Fan-Out)]

    subgraph Buffer & Subscribers
        RB[(Ring Buffer - 200 Max)]
        Q1[Subscriber Queue 1: Web UI SSE]
        Q2[Subscriber Queue 2: Diagnostics]
        Q3[Subscriber Queue 3: Internal Logger]
    end

    TM -->|publish| EB
    WM -->|publish| EB
    Sys -->|publish| EB

    EB -->|append| RB
    EB -->|put_nowait| Q1
    EB -->|put_nowait| Q2
    EB -->|put_nowait| Q3
```

### Key Capabilities:

1. **Non-Blocking Publishing**: `event_bus.publish()` puts events into each subscriber queue using `put_nowait()`. Publishers never wait on subscribers.
2. **Slow Subscriber Protection**: If a client connection stutters or fails to read from its queue (`QueueFull`), the oldest unread event is dropped or the event is skipped for that subscriber, ensuring slow clients cannot backpressure active worker threads.
3. **In-Memory Ring Buffer**: Retains the last 200 events (`event_buffer_size`). Frontends reconnecting or loading a fresh view can fetch recent history with `GET /api/v1/events/recent` without missing diagnostic context.

---

## 2. Server-Sent Events (SSE) Protocol

Real-time streaming is exposed over HTTP Server-Sent Events via `GET /api/v1/events/stream`.

### SSE Frame Format:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no

: connected

event: task.progress
id: 550e8400-e29b-41d4-a716-446655440000
data: {"event_id":"...","event_type":"task.progress","timestamp":"2026-11-16T14:00:00Z","task_id":"...","payload":{"progress":0.4,"message":"Step 2/5 completed"}}

event: system.heartbeat
id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
data: {"event_id":"...","event_type":"system.heartbeat","timestamp":"2026-11-16T14:00:15Z","payload":{"uptime_seconds":152.0}}
```

### Protocol Details:

- **Immediate Connection Line**: Yields `: connected\n\n` immediately upon client handshake so the UI knows the stream is healthy before events fire.
- **Heartbeat Keep-Alive**: Emits a `system.heartbeat` ping every 15 seconds to prevent browser or proxy socket timeouts.
- **Ordered Teardown**: Automatically unregisters and frees client queues when the client aborts or closes the connection (`GeneratorExit`).

---

## 3. Standard Event Taxonomy

All events use the structured `EventEnvelope` schema:

| Event Type           | Producer             | Description                               |
| :------------------- | :------------------- | :---------------------------------------- |
| `system.startup`     | Lifespan             | Service container initialized and ready   |
| `system.shutdown`    | Lifespan             | Graceful shutdown initiated               |
| `system.heartbeat`   | SSE Generator        | 15s keep-alive ping with uptime info      |
| `worker.idle`        | WorkerManager        | Worker became available for task dispatch |
| `worker.busy`        | WorkerManager        | Worker claimed a task for execution       |
| `task.created`       | TaskManager          | New task registered in memory             |
| `task.queued`        | TaskManager          | Task enqueued in worker queue             |
| `task.state_changed` | TaskManager          | Task progressed through state machine     |
| `task.progress`      | TaskExecutionContext | Granular percent completion (0.0 to 1.0)  |
| `task.completed`     | TaskManager          | Task executed and verified successfully   |
| `task.failed`        | TaskManager          | Task encountered an unrecoverable failure |
| `task.cancelled`     | TaskManager          | Task cancelled cooperatively              |
