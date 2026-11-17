# AUTONOM — AI Model Gateway (Stage 11)

## 1. Overview & Architectural Role

The **AUTONOM AI Model Gateway** is the central inference execution layer for the AUTONOM Windows 11 desktop assistant. It provides a unified, provider-agnostic interface across local quantizations (via Ollama) and cloud inference endpoints (OpenAI and OpenAI-compatible services).

Future specialist agents (Stage 12–24) interact exclusively with the AI Gateway via standardized domain contracts rather than directly connecting to disparate LLM APIs.

```
                    ┌────────────────────────────┐
                    │    Specialist AI Agents    │
                    │   (Job Scout, Resume, etc) │
                    └─────────────┬──────────────┘
                                  │ Unified Inference Contracts
                                  ▼
                    ┌────────────────────────────┐
                    │      AI Model Gateway      │
                    │       (FastAPI Engine)     │
                    └──────┬──────┬──────┬───────┘
                           │      │      │
            ┌──────────────┘      │      └──────────────┐
            ▼                     ▼                     ▼
┌───────────────────────┐ ┌──────────────┐ ┌─────────────────────────┐
│ Local Model Controller│ │ Model Router │ │ Token & Budget Manager  │
│ - Single Model Guard  │ │ - 16 Specs   │ │ - tiktoken cl100k_base  │
│ - RTX 4050 6GB Bounds │ │ - Fallbacks  │ │ - Real Pricing Catalog  │
│ - NVML Real Telemetry │ │ - Privacy    │ │ - Accurate Cost USD     │
└───────────┬───────────┘ └──────┬───────┘ └─────────────────────────┘
            │                    │
            ▼                    ▼
┌────────────────────────────────────────────────────────────────────┐
│                         Provider Adapters                          │
├─────────────────────────┬────────────────────────┬─────────────────┤
│ Local Ollama            │ OpenAI Cloud           │ Compatible API  │
│ 127.0.0.1:11434 (Loop)  │ HTTPS (DPAPI Secured)  │ vLLM / LM Studio│
└─────────────────────────┴────────────────────────┴─────────────────┘
```

---

## 2. Core Functional Capabilities

1. **Unified Request/Response Contracts**: Strongly typed Pydantic models in backend (`services/api/app/ai/contracts.py`) and TypeScript interfaces in frontend (`packages/shared-types/src/ai.ts`).
2. **Provider Discovery & Capability Detection**: Live probing of installed model tags, context window dimensions, quantization levels, and capability flags (`chat`, `streaming`, `structured_output`, `vision`, `tool_calling`, `reasoning`).
3. **Hardware-Guarded Local Inference**: Native C-bindings via NVML (`nvidia-ml-py`) ensuring NVIDIA GeForce RTX 4050 Laptop GPU (6,141 MB total VRAM) is never saturated, strictly restricting local execution to **one active language model in VRAM at a time**.
4. **Intelligent Explainable Routing**: Dynamic multi-strategy router supporting 16 specialization categories, automatic fallback, and strict local privacy enforcement.
5. **Real-Time Streaming**: Server-Sent Events (SSE) delivery via `/api/v1/ai/chat/stream` with token-by-token emission, TTFT calculation, and client-side cooperative cancellation.
6. **Context & Cost Budgeting**: Accurate token calculation with `tiktoken` (cl100k_base), automatic message history pruning, and token pricing accounting.

---

## 3. REST API Specification

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/v1/ai/providers` | `GET` | Lists registered AI providers and their connectivity status. |
| `/api/v1/ai/providers/{id}/health` | `GET` | Real-time health probe and latency measurement. |
| `/api/v1/ai/models` | `GET` | Returns list of discovered models across all providers. |
| `/api/v1/ai/models/{p}/{m}` | `GET` | Detailed capability, specification, and pricing for a model. |
| `/api/v1/ai/models/refresh` | `POST` | Forces rediscovery of models from local Ollama and APIs. |
| `/api/v1/ai/models/local/load` | `POST` | Pre-warms a local model into RTX 4050 VRAM. |
| `/api/v1/ai/models/local/unload` | `POST` | Releases weights from VRAM via `keep_alive=0`. |
| `/api/v1/ai/requests` | `POST` | Synchronous / structured inference execution. |
| `/api/v1/ai/chat/stream` | `POST` | High-performance Server-Sent Events streaming token endpoint. |
| `/api/v1/ai/requests/{id}/cancel`| `POST` | Cooperatively cancels an in-flight inference request. |
| `/api/v1/ai/route/preview` | `POST` | Simulates and explains routing decisions without executing. |
| `/api/v1/ai/resources` | `GET` | Direct NVML GPU VRAM and host RAM telemetry. |
| `/api/v1/ai/usage` | `GET` | Usage analytics, token consumption, and cost attribution. |
| `/api/v1/ai/routing/preferences` | `GET` | Reads current model assignments for 16 task categories. |
| `/api/v1/ai/routing/preferences` | `PATCH` | Updates routing preferences with persistence in SQLite. |

---

## 4. Execution Pipeline & Error Handling

```
InferenceRequest
       │
       ▼
1. Validation & Context Budgeting (ContextBudgetManager checks context_window)
       │
       ▼
2. Routing Decision (IntelligentModelRouter matches category, privacy, & load)
       │
       ▼
3. Local Concurrency Gate (LocalModelResourceController acquires 1-slot semaphore)
       │
       ▼
4. Provider Dispatch (Provider adapter issues local loopback or cloud HTTPS request)
       │
       ▼
5. Output Parsing & Schema Validation (Pydantic / JSON schema validator if requested)
       │
       ▼
6. Token Accounting & Auditing (AIInferenceRequestRecord inserted into SQLite)
       │
       ▼
InferenceResponse / SSE Stream
```

The gateway handles all standard failure modes through a normalized exception hierarchy (`services/api/app/ai/errors.py`):
- `GPUMemoryExhaustedError`: Triggered if local weights exceed memory bounds; routes to cloud fallback if authorized.
- `ContextLimitExceededError`: Triggered if prompt length exceeds model ceiling after auto-pruning.
- `RateLimitError`: Cloud provider 429 backoff handling.
- `ProviderUnavailableError`: Provider offline or unreachable; triggers fallback sequence.

---

## 7. Specialist Agent Integration & Model Profiles (Stage 13)

In Stage 13, the AI Model Gateway serves as the centralized inference backbone for the Specialist Agent Framework.
- **`AgentModelProfile` Binding**: Each specialist agent declares preferred local and cloud models, temperature, reasoning effort, and max output tokens. The AI Gateway consumes these profiles during capability execution.
- **Hardware Semaphore Guardrail**: When multiple specialist agents in a DAG require local LLM reasoning, requests are serialized through `LocalModelResourceController`'s single-active-model semaphore (`asyncio.Semaphore(1)`), preventing memory exhaustion on the NVIDIA RTX 4050 6GB Laptop GPU.
- **Deterministic Capability Fallbacks**: All 32 specialist capabilities include native Python heuristics (AST parsing, regular expressions, structured text extraction), enabling workflows to succeed even when the local model server is unloaded or offline.

For full details, see [docs/AGENT_MODEL_PROFILES.md](file:///e:/proooo/AUTO%20JOB/docs/AGENT_MODEL_PROFILES.md).
