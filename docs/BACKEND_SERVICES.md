# AUTONOM — Backend Service Architecture (Stage 03)

This document specifies the layered service architecture, dependency directions, lifecycle management, and API gateway routing for the **AUTONOM** Python backend (`services/api`).

---

## 1. Architectural Philosophy & Constraints

AUTONOM's backend is engineered to run locally as an integrated desktop service on Windows 11 hardware (e.g., AMD/Intel x64, RTX 4050 6GB VRAM, 16GB RAM) without requiring heavy distributed infrastructure (no Docker, Kubernetes, Redis, RabbitMQ, or Celery).

### Core Design Tenets:

1. **Local-First & Resource-Constrained**: Single process event loop (`asyncio`) managing asynchronous background workers with strict concurrency limits (default: 4 workers, 50 task queue capacity).
2. **Strict Layered Separation**: High-level modules depend on abstractions, never on low-level implementation details.
3. **No Heavy External Brokers**: In-process bounded queue and asynchronous event bus provide zero-overhead event distribution and queueing.
4. **Cooperative Multitasking**: Long-running automation actions yield control, check cancellation tokens, and stream granular progress.

---

## 2. Layered Architecture Overview

The backend is structured into distinct, decoupled architectural layers:

```mermaid
graph TD
    Client[Desktop UI / Tauri Shell] -->|HTTP / SSE| APIGateway[FastAPI API Gateway]

    subgraph Layer 1: API & Security Boundary
        APIGateway --> Security[Security & Token Auth Dependency]
        APIGateway --> Errors[Global Exception Handler]
        APIGateway --> Dependencies[Dependency Injection Container]
    end

    subgraph Layer 2: Service Orchestration
        Dependencies --> ServiceContainer[ServiceContainer Singleton]
        ServiceContainer --> TaskManager[TaskExecutionManager]
        ServiceContainer --> WorkerPool[WorkerManager Pool]
        ServiceContainer --> EventBusInstance[EventBus]
        ServiceContainer --> Registry[HandlerRegistry]
    end

    subgraph Layer 3: Execution Engine & State Machine
        TaskManager --> StateMachine[TaskStateMachine (11 States)]
        TaskManager --> Context[TaskExecutionContext]
        WorkerPool -->|Consumes Queue| TaskManager
        TaskManager -->|Dispatches| Handlers[TaskHandler Implementations]
    end

    subgraph Layer 4: Real-Time Event Fan-Out
        TaskManager -->|Publishes Events| EventBusInstance
        WorkerPool -->|Publishes Events| EventBusInstance
        EventBusInstance -->|Fan-Out Queue| SSEStream[SSE Event Streaming]
        EventBusInstance -->|Persists (Max 200)| RingBuffer[In-Memory Ring Buffer]
    end
```

---

## 3. Component Responsibilities

### 3.1. API Gateway (`app/api/v1`)

- **Routing**: Clean, versioned endpoint prefix `/api/v1` for tasks, workers, system health, and event streaming.
- **Backwards Compatibility**: Transparent routing for legacy `/api/health` aliases.
- **Request Validation**: Pydantic v2 schemas strictly validate every incoming payload and reject malformed schemas with 422 Unprocessable Entity.
- **Loopback Enforcement**: Local loopback socket binding (`127.0.0.1:8765`) preventing unauthorized LAN exposure.

### 3.2. Service Container (`app/services/service_container.py`)

- Centralized dependency injection hub managing singletons: `EventBus`, `WorkerManager`, `HandlerRegistry`, and `TaskExecutionManager`.
- Provides explicit `startup()` and `shutdown()` lifecycles.
- Includes `reset()` capabilities ensuring complete test isolation across concurrent test suites.

### 3.3. Task Execution Manager (`app/execution/manager.py`)

- Tracks tasks in-memory by UUID.
- Validates task type availability against `HandlerRegistry`.
- Coordinates state transitions using `TaskStateMachine`.
- Dispatches tasks to the `WorkerManager` queue.
- Enforces execution timeouts and cooperative task cancellation.

### 3.4. Worker Manager (`app/workers/manager.py`)

- Maintains an `asyncio.Queue` bounded to `max_queue_size` (default: 50).
- Spawns a fixed pool of background worker tasks (`concurrency=4`).
- Rejects requests when the queue is saturated with `QueueFullError` (HTTP 429).
- Tracks worker states (`idle`, `busy`, `stopped`), uptime, and task throughput.

### 3.5. Event Bus (`app/events/bus.py`)

- Non-blocking pub/sub system for real-time decoupling.
- Fan-out to multiple subscriber queues with slow-subscriber isolation (drops slow frames to protect worker loops).
- Bounded ring buffer retains the most recent 200 events for newly connected frontends.

---

## 4. Service Lifespan & Graceful Teardown

Backend startup and shutdown are managed via the FastAPI async lifespan context manager (`app/core/lifespan.py`):

1. **Startup Sequence**:
   - Initialize `ServiceContainer`.
   - Register default built-in task handlers (`compute.echo`, `test.sleep_progress`).
   - Start `WorkerManager` consumer loops.
   - Publish `system.startup` event to `EventBus`.
   - Log service readiness on `127.0.0.1:8765`.

2. **Shutdown Sequence**:
   - Receive SIGINT, SIGTERM, or application exit event.
   - Stop accepting new tasks.
   - Signal cooperative cancellation to all running tasks.
   - Allow active workers up to 5 seconds to gracefully finalize.
   - Drain and close `EventBus` subscriber queues.
   - Close in-memory resources and log clean termination.
