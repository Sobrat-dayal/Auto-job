# AUTONOM — Agent Model Profiles & Hardware Optimization

## 1. Executive Summary

Every agent in AUTONOM specifies an `AgentModelProfile` that defines how the Unified AI Model Gateway (`AIGateway`) routes, manages, and provisions inference resources for that agent.

Because AUTONOM is designed to run efficiently on Windows 11 client laptops (specifically calibrated for an **NVIDIA GeForce RTX 4050 Laptop GPU with 6GB VRAM** and 16GB system RAM), the model profile architecture enforces strict memory safety rules.

---

## 2. Model Profile Specification

```python
class AgentModelProfile(BaseModel):
    preferred_local_model: str = "qwen2.5:7b"
    preferred_cloud_model: str = "gemini-1.5-flash"
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_output_tokens: int = Field(2048, ge=128, le=8192)
    reasoning_effort: str = "standard"  # low, standard, high
    fallback_model: Optional[str] = None
```

### Profile Attributes

| Field | Purpose | Typical Values |
|---|---|---|
| `preferred_local_model` | GGUF / Ollama model identifier to load locally | `qwen2.5:7b`, `mistral:7b`, `deepseek-r1:7b` |
| `preferred_cloud_model` | Cloud provider model for heavy reasoning or offloading | `gemini-1.5-flash`, `gemini-1.5-pro`, `gpt-4o-mini` |
| `temperature` | Sampling randomness (0.0 = deterministic, 0.7 = creative) | 0.0 (planner/code), 0.2 (tailoring), 0.7 (creative) |
| `max_output_tokens` | Strict ceiling on output generation | 1,024 to 4,096 tokens |
| `reasoning_effort` | Hint for extended reasoning and chain-of-thought | `low` (fast tasks), `standard`, `high` (DAG/supervision) |

---

## 3. Hardware Guardrail: The RTX 4050 6GB Laptop GPU Policy

### The Single-Active-Model Invariant
A quantized 7B model (Q4_K_M) consumes approximately 4.2 GB of VRAM. Attempting to load two 7B models simultaneously into a 6GB VRAM buffer results in instant CUDA out-of-memory crashes or severe Windows OS paging into system RAM.

To guarantee stability:
1. **Single-Active-Model Semaphore**:
   The AI Gateway uses `asyncio.Semaphore(1)` around all local model inference and loading calls.
2. **No Eager Mass-Loading**:
   Weights for the 24 agents are **never** loaded into VRAM concurrently. Agents are stateful definitions with ephemeral model sessions.
3. **Graceful Offloading / LRU Unload**:
   When switching between different local models, the previous model is evicted from VRAM via Ollama's `keep_alive=0` parameter or memory reclamation routines.
4. **Deterministic Local Fallbacks**:
   All capability handlers in `services/api/app/orchestration/capabilities/` include deterministic analytical fallback algorithms (regular expressions, heuristic parsers, AST analyzers). If the local model server is offline or busy, the task completes without throwing unhandled exceptions.

---

## 4. Agent Domain Profiles

| Domain | Preferred Local | Preferred Cloud | Temp | Reason Effort | Max Tokens |
|---|---|---|---|---|---|
| **Supervisor & Planner** | `qwen2.5:7b` | `gemini-1.5-pro` | 0.0 | High | 4,096 |
| **Verification & Recovery**| `qwen2.5:7b` | `gemini-1.5-pro` | 0.1 | High | 2,048 |
| **Recruitment (Match/Tailor)**| `qwen2.5:7b`| `gemini-1.5-flash`| 0.2 | High | 3,072 |
| **Recruitment (Discovery/Comms)**| `qwen2.5:7b`| `gemini-1.5-flash`| 0.3 | Standard | 2,048 |
| **Coding & Review** | `qwen2.5:7b` | `gemini-1.5-pro` | 0.1 | High | 4,096 |
| **Research & Analysis** | `qwen2.5:7b` | `gemini-1.5-flash`| 0.2 | Standard | 3,072 |
| **Productivity (Doc/Sheet)**| `qwen2.5:7b`| `gemini-1.5-flash`| 0.2 | Standard | 2,048 |
| **Creative Design** | `qwen2.5:7b` | `gemini-1.5-flash`| 0.7 | Low | 2,048 |
| **Computer Operations** | `qwen2.5:7b` | `gemini-1.5-pro` | 0.1 | High | 2,048 |
| **Automation** | `qwen2.5:7b` | `gemini-1.5-flash`| 0.1 | Standard | 2,048 |

---

## 5. Token Budget Allocation

To prevent runaway token accumulation during multi-step DAG workflows:

```
Workflow Context Window: 32,768 tokens (local Qwen-2.5)
+-------------------------------------------------------------+
| System Prompt & Manifest:             ~1,500 tokens (5%)    |
| Profile / Verified Facts:             ~4,000 tokens (12%)   |
| Job Description / Input Data:         ~4,000 tokens (12%)   |
| Step-by-Step DAG Scratchpad / History:~15,000 tokens (46%)  |
| Safety Reserve:                       ~4,000 tokens (12%)   |
| Output Generation Window:             ~4,096 tokens (13%)   |
+-------------------------------------------------------------+
```
