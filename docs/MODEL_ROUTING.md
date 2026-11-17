# AUTONOM — Intelligent Model Routing (Stage 11)

## 1. Overview & Strategy Engine

AUTONOM's **Intelligent Model Router** (`services/api/app/ai/router.py`) maps diverse multi-agent workloads to the optimal inference model. Rather than hard-coding model names, specialist agents provide a `task_category` and constraints, allowing the router to evaluate:
- The user's active `RoutingStrategy`.
- Category-specific preference overrides.
- Privacy boundaries (`is_local_only=True`).
- Active VRAM state and currently loaded models (to minimize switching latency).
- Prompt size vs. model context ceilings.

---

## 2. 16 Task Specialization Categories

| Category | Default Local Model | Default Cloud Model | Privacy Default | Typical Workload |
| :--- | :--- | :--- | :---: | :--- |
| `general_conversation` | `llama3:8b` | `gpt-4o-mini` | Standard | Interactive user chat |
| `short_reasoning` | `llama3:8b` | `gpt-4o-mini` | Standard | Quick decision gates |
| `complex_reasoning` | `llama3:8b` | `gpt-4o` | Standard | Deep strategy & planning |
| `coding` | `qwen2.5-coder:7b` | `gpt-4o` | Standard | Script generation & refactoring |
| `code_review` | `qwen2.5-coder:7b` | `gpt-4o` | Standard | Security & quality auditing |
| `research_synthesis` | `llama3:8b` | `gpt-4o` | Standard | Multi-source literature synthesis |
| `document_writing` | `llama3:8b` | `gpt-4o` | Standard | Cover letters & long-form text |
| `job_description_analysis` | `llama3:8b` | `gpt-4o-mini` | Standard | Requirement extraction & ATS scoring |
| `resume_analysis` | `llama3:8b` | `gpt-4o` | **Strict Local** | PII resume parsing & skills audit |
| `screening_answer_drafting`| `llama3:8b` | `gpt-4o` | Standard | Application question formulation |
| `summarization` | `llama3.2:3b` | `gpt-4o-mini` | Standard | Log & document condensations |
| `structured_extraction` | `llama3:8b` | `gpt-4o-mini` | Standard | Strict JSON schema data parsing |
| `classification` | `llama3.2:3b` | `gpt-4o-mini` | Standard | Intent routing & message triage |
| `planning` | `llama3:8b` | `gpt-4o` | Standard | Multi-agent DAG task decomposition |
| `vision_interpretation` | N/A | `gpt-4o` | Standard | UI screenshot OCR & visual inspection |
| `computer_control_grounding`| N/A | `gpt-4o` | Standard | Action coordinate identification |

---

## 3. 7 Routing Strategies

1. `local_first` (Default): Evaluates whether a capable local model is installed. If so, routes locally with zero external network transmission. Falls back to cloud only when authorized and local models are absent or memory-saturated.
2. `cloud_first`: Prioritizes cloud endpoints for maximum benchmark quality.
3. `lowest_cost`: Evaluates token pricing catalogs and selects the cheapest capable provider (local is always evaluated as $0.00).
4. `lowest_latency`: Selects local models actively resident in VRAM or fast cloud mini-models.
5. `capability_first`: Filters candidates strictly by required capabilities (e.g. `structured_output`, `vision`).
6. `privacy_restricted`: Absolute local boundary. Under no circumstances will prompt tokens be forwarded to cloud APIs. If no local model is available, fails with `ProviderUnavailableError`.
7. `manual`: Directly adheres to user-specified `provider_preference` and `model_preference`.

---

## 4. Explainable Routing Decisions

Every routing decision produces an explainable `RoutingDecision` payload:

```json
{
  "selected_provider_id": "ollama",
  "selected_model_id": "llama3:8b",
  "strategy_used": "local_first",
  "rule_applied": "Active VRAM Model Re-use",
  "explanation": "Category job_description_analysis preferred model ollama:llama3:8b is already resident in RTX 4050 VRAM. Selected to eliminate model load latency.",
  "candidates_considered": ["ollama:llama3:8b", "openai:gpt-4o-mini"],
  "fallbacks_available": ["openai:gpt-4o-mini"],
  "is_local": true
}
```
This payload is persisted in SQLite with the inference log and is inspectable in the AI Usage audit table.
