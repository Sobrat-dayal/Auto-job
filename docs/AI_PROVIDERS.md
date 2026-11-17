# AUTONOM — AI Provider Integrations (Stage 11)

## 1. Supported Providers

AUTONOM implements genuine adapters for three distinct categories of model runtimes:

1. **Ollama (Local Offline Loopback)**:
   - Primary host runtime for zero-cloud, 100% offline, privacy-guaranteed execution.
   - Endpoint: `http://127.0.0.1:11434` (standard local loopback).
   - Authentication: None required on loopback.
   - Supported Operations:
     - Tag Discovery: `GET /api/tags`
     - Model Information: `POST /api/show`
     - Text Generation & Chat: `POST /api/chat`
     - Real-Time Streaming: Chunked NDJSON stream parser.
     - Dynamic VRAM Allocation: Unload via `keep_alive=0`, load via `keep_alive=300s`.

2. **OpenAI Official Cloud API**:
   - Secondary cloud runtime for high-capacity multi-step reasoning, multimodal processing, and large context windows.
   - Endpoint: `https://api.openai.com/v1`
   - Authentication: Windows DPAPI encrypted API key resolved securely from the local keystore (`services/api/app/security/vault.py`).
   - Supported Operations:
     - Standard Chat: `POST /v1/chat/completions`
     - Real-Time Streaming: Server-Sent Events line parser with `data: [DONE]` terminal signal.
     - Structured JSON: `response_format={"type": "json_object"}`.

3. **OpenAI-Compatible Custom Endpoints**:
   - Configurable adapter for self-hosted instances (vLLM, LM Studio, LocalAI, DeepSeek, Together AI).
   - Dynamically configurable endpoint URL and custom authentication headers.

---

## 2. Model Discovery & Verification

The Gateway automatically discovers available models on startup and upon invocation of `POST /api/v1/ai/models/refresh`:

```python
# Discovered metadata structure
class ModelInfo(BaseModel):
    id: str  # "provider_id:model_id"
    provider_id: str
    model_id: str
    display_name: str
    provider_type: Literal["local", "cloud"]
    is_available: bool
    context_window: int
    max_output_tokens: int
    capabilities: list[str]
    pricing: ModelPricing
    reported_size_bytes: int | None
    quantization: str | None
    last_discovered_at: datetime
```

### Zero-Fake-Data Compliance
If Ollama is running but no local models have been pulled by the user (`ollama list` returns empty), the Gateway honestly reports:
```json
{
  "provider_id": "ollama",
  "is_healthy": true,
  "status": "available",
  "models": []
}
```
No synthetic or mock models are fabricated. The UI provides direct, non-blocking guidance for installing lightweight quantized models suitable for the 6GB VRAM budget (e.g. `llama3.2:3b`, `llama3:8b`, `qwen2.5-coder:7b`).
