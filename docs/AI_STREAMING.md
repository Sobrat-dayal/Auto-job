# AUTONOM — AI Streaming Architecture (Stage 11)

## 1. Real-Time Token Delivery Protocol

AUTONOM delivers live token output to the desktop client via **Server-Sent Events (SSE)** over `POST /api/v1/ai/chat/stream`.

### Event Stream Format
The server streams chunks conforming to the standard SSE event protocol:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: start
data: {"request_id": "c7a8...", "provider_id": "ollama", "model_id": "llama3:8b"}

event: delta
data: {"request_id": "c7a8...", "delta": "Here "}

event: delta
data: {"request_id": "c7a8...", "delta": "is "}

event: complete
data: {"request_id": "c7a8...", "content": "Here is...", "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20}, "latency_ms": 420, "estimated_cost_usd": 0.0}
```

---

## 2. Cooperative Cancellation

Users can interrupt in-flight generation at any millisecond:
1. Clicking **Stop Generation** in the UI calls `apiClient.cancelAIRequest(requestId)`.
2. The FastAPI `CancellationManager` sets an `asyncio.Event` associated with that request ID.
3. The background streaming generator detects the cancellation token, gracefully terminates the provider connection, emits a `cancelled` event, and unloads any locked resource slots.
4. Token usage accumulated prior to cancellation is recorded for auditing.
