# AUTONOM — AI Provider Configuration & Model Resource Management

## 1. Overview & Architectural Role

The AI Provider Configuration system established in **Stage 10** defines the configuration schema, resource boundary controls, and persistence mechanisms for all local and cloud-based Large Language Model (LLM) engines powering AUTONOM.

While full inference dispatch, streaming token handling, and fallback orchestration are scheduled for **Stage 11 (Unified AI Model Gateway)**, Stage 10 establishes the operational settings plane, strong validation contracts, Windows DPAPI credential references, and physical hardware boundary enforcement.

```
+-----------------------------------------------------------------------------------------+
|                                FRONTEND: /settings/ai                                   |
| - Default Provider Selector (Local Ollama, Anthropic Claude, OpenAI, DeepSeek)          |
| - Model Parameter Controls (Temperature, Top-P, Context Window, Output Limit)          |
| - VRAM Hardware Guardrails (RTX 4050 6GB profile, Single Active Model Policy)           |
| - Cloud API Key DPAPI Vault Linkage                                                     |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v PATCH /api/v1/settings/ai
+-----------------------------------------------------------------------------------------+
|                               FASTAPI LOCAL BACKEND (8765)                              |
| - AISettings Pydantic Schema Validation                                                 |
| - GPU Resource Guardrail Validation (VRAM limits <= 6.0 GB, Context <= 8192 for local)  |
| - SettingsRepository (Atomic JSON serialization to SQLite WAL `app_settings`)           |
+-----------------------------------------------------------------------------------------+
                                             |
                     +-----------------------+-----------------------+
                     v                                               v
+------------------------------------------+    +-----------------------------------------+
|           SQLITE `app_settings`          |    |       WINDOWS DPAPI CREDENTIAL VAULT    |
| - `default_provider`: "ollama"           |    | - `api_key_anthropic`: DPAPI ciphertext |
| - `ollama_base_url`: "http://127.0.0.1"  |    | - `api_key_openai`: DPAPI ciphertext    |
| - `vram_budget_gb`: 5.0                  |    | - Zero plaintext keys in SQLite WAL     |
| - `single_active_model`: true            |    +-----------------------------------------+
+------------------------------------------+
```

---

## 2. Hardware Resource Boundaries: NVIDIA RTX 4050 6GB VRAM

A core requirement of AUTONOM's target deployment environment is reliable local inference on modern laptop workstations equipped with an **NVIDIA GeForce RTX 4050 Mobile (6GB VRAM)**.

### 2.1 Physical Limits & Allocation Profile

- **Total Physical VRAM**: 6,144 MB (6.0 GB).
- **Windows DWM & Display Reserve**: ~1,000 MB reserved by Windows Desktop Window Manager and system display compositing.
- **Max Usable Inference VRAM Budget**: 5,144 MB (~5.0 GB default setting in `vram_budget_gb`).
- **Safety Margin**: A 1,000 MB buffer prevents CUDA Out-Of-Memory (OOM) driver crashes and desktop freezing.

### 2.2 Local Model Quantization Matrix

To remain within the 5.0 GB budget, local models configured in AUTONOM must conform to the following quantization boundaries:

| Model Architecture    | Quantization Format | Weights VRAM | 4K KV Cache | 8K KV Cache | Total VRAM | Status                       |
| --------------------- | ------------------- | ------------ | ----------- | ----------- | ---------- | ---------------------------- |
| **Llama 3.1 8B**      | Q4_K_M (4-bit)      | 4.6 GB       | 0.4 GB      | 0.8 GB      | 5.4 GB     | Supported (4K context)       |
| **Mistral 7B v0.3**   | Q4_K_M (4-bit)      | 4.1 GB       | 0.3 GB      | 0.6 GB      | 4.7 GB     | Supported (8K context)       |
| **Qwen 2.5 7B**       | Q4_K_M (4-bit)      | 4.4 GB       | 0.3 GB      | 0.7 GB      | 5.1 GB     | Supported (4K context)       |
| **Phi-3.5 Mini 3.8B** | Q4_K_M (4-bit)      | 2.2 GB       | 0.2 GB      | 0.4 GB      | 2.6 GB     | Supported (High Concurrency) |
| **Llama 3.1 70B**     | Any Quantization    | >35 GB       | -           | -           | >35 GB     | Cloud / Remote Only          |

### 2.3 Strict Single Active Model Rule

Concurrent loading of multiple local model weights is explicitly forbidden on 6GB VRAM configurations:

- When `single_active_model: true` (default), the backend prevents concurrent background task dispatch across differing local weights.
- Switching between task types requiring distinct models (e.g. general orchestration vs. specialized coding models) initiates an explicit model unload request to the local daemon before loading the replacement weights.

---

## 3. Configuration Schema Specification (`AISettings`)

The complete schema is declared in `services/api/app/schemas/settings.py` and mirrored in `packages/shared-types/src/settings.ts`:

```typescript
export interface AISettings {
  // Provider Selection
  default_provider: 'ollama' | 'anthropic' | 'openai' | 'deepseek' | 'openrouter';
  fallback_provider: string; // e.g. "anthropic" or "none"

  // Local Inference Configuration (Ollama)
  ollama_base_url: string; // Default: "http://127.0.0.1:11434"
  ollama_default_model: string; // Default: "llama3.1:8b-instruct-q4_K_M"
  ollama_keep_alive_minutes: number; // Default: 5 (auto-unload after inactivity)

  // Cloud Model Defaults
  anthropic_default_model: string; // Default: "claude-3-5-sonnet-20241022"
  openai_default_model: string; // Default: "gpt-4o"
  deepseek_default_model: string; // Default: "deepseek-chat"

  // Inference Hyperparameters
  temperature: number; // 0.0 - 2.0 (Default: 0.7)
  top_p: number; // 0.0 - 1.0 (Default: 0.9)
  context_window_tokens: number; // 1024 - 128000 (Default: 8192)
  max_output_tokens: number; // 256 - 16384 (Default: 4096)
  timeout_seconds: number; // 5 - 300 (Default: 60)

  // Resource & Safety Guards
  vram_budget_gb: number; // 1.0 - 24.0 (Default: 5.0)
  single_active_model: boolean; // Default: true
  enable_streaming: boolean; // Default: true
  enable_cloud_fallback: boolean; // Default: true
  allow_remote_fallbacks: boolean; // Default: false (local-only privacy toggle)
}
```

---

## 4. Security & Credential Isolation

In accordance with AUTONOM's **Zero Plaintext Credentials** security policy:

1. **Decoupled Key Storage**:
   - The `app_settings` table in SQLite stores configuration options and preferences only.
   - Cloud API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`) are **never stored in SQLite**.
2. **Windows DPAPI Vault Storage**:
   - Keys entered through the UI are sent directly to `POST /api/v1/auth/credentials` or encrypted via Tauri native IPC with user-scoped Windows DPAPI.
   - The settings screen displays masked indicators (`••••••••sk-ant-live...`) and vault health status (`VAULT_CONNECTED`).
3. **Audit Logging**:
   - Any modification to API key linkage, base URLs, or fallback options generates an immutable audit record in `audit_events` with timestamp and actor metadata.

---

## 5. User Interface Controls (`/settings/ai`)

The frontend implementation in [AIProviderSettingsPage.tsx](file:///e:/proooo/AUTO%20JOB/apps/desktop/src/features/settings/pages/AIProviderSettingsPage.tsx) provides:

- **Provider Cards**: Visual selectors for local daemon (Ollama) and cloud APIs with real-time connectivity status.
- **Hardware Profile Card**: Live visualization of the RTX 4050 6GB profile, displaying allocated inference VRAM vs. Windows OS reserved memory.
- **Parameter Sliders & Inputs**: Accessible numeric controls for `temperature`, `top_p`, and context bounds with immediate validation.
- **Zero-Fake-Data Status Indicators**:
  - Unconfigured providers display clear "Not Configured" badges.
  - The local daemon card queries the actual endpoint (`http://127.0.0.1:11434/api/tags`) and reports real connection state or "Offline".
  - If a model is unavailable, the UI presents actionable troubleshooting steps rather than simulated responses.

---

## 6. Stage 11 Integration Requirements (Model Gateway)

Stage 11 will consume the configuration plane established in Stage 10 via the following integration contracts:

1. **Config Consumption**:
   - `services/api/app/services/ai_gateway.py` will read `AISettings` on startup and cache the configuration.
   - Changes emitted via `PATCH /api/v1/settings/ai` will trigger a configuration reload event in the gateway.
2. **Fallback Ladder Execution**:
   - When a primary provider (e.g. Local Ollama) exceeds timeout (`timeout_seconds`) or exhausts VRAM, the gateway verifies `allow_remote_fallbacks`.
   - If permitted, it fails over to `fallback_provider` using DPAPI-unwrapped credentials.
3. **Token Stream Routing**:
   - Streaming responses (`enable_streaming: true`) will use Server-Sent Events (SSE) from FastAPI to TanStack Query/Zustand client hooks.
