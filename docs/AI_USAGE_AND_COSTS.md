# AUTONOM — AI Usage Accounting & Cost Tracking (Stage 11)

## 1. Token Pricing Catalog

AUTONOM maintains an up-to-date pricing table (`services/api/app/ai/budgets.py`) measured in USD per 1 Million Tokens:

| Provider | Model | Input Cost / 1M | Output Cost / 1M | Cost Model |
| :--- | :--- | :---: | :---: | :--- |
| **Ollama** | All Local Models | **$0.0000** | **$0.0000** | 100% Free / Local Hardware |
| **OpenAI** | `gpt-4o` | $2.5000 | $10.0000 | Cloud Pay-Per-Token |
| **OpenAI** | `gpt-4o-mini` | $0.1500 | $0.6000 | Ultra-Low Cost Cloud |
| **OpenAI** | `o1-mini` | $3.0000 | $12.0000 | High Reasoning Cloud |
| **Anthropic** | `claude-3-5-sonnet` | $3.0000 | $15.0000 | High Capability Cloud |
| **DeepSeek** | `deepseek-chat` | $0.1400 | $0.2800 | DeepSeek Official API |

---

## 2. Accurate Cost Calculation

For every inference response, costs are computed deterministically down to six decimal places:

$$\text{Cost} = \left( \frac{\text{Prompt Tokens}}{1,000,000} \times \text{Input Price} \right) + \left( \frac{\text{Completion Tokens}}{1,000,000} \times \text{Output Price} \right)$$

For local Ollama inference, cost is explicitly attributed as `$0.000000`.

---

## 3. Persistent Inference Audit Logging

Every inference request is stored permanently in SQLite (`ai_requests` table) via `AIRepository.record_request()`:

- `request_id`: Unique UUID identifier.
- `task_id` / `correlation_id`: Link to autonomous task execution DAGs.
- `task_category`: Specialization category.
- `provider_id` & `model_id`: Provider and model resolved.
- `prompt_tokens`, `completion_tokens`, `total_tokens`: Reported by runtime or calculated by `tiktoken`.
- `estimated_cost_usd`: Exact financial attribution.
- `latency_ms` & `time_to_first_token_ms`: Performance metrics.
- `status`: `completed`, `failed`, or `cancelled`.
- `routing_rule_applied`: Reason why this model was chosen.
- `created_at`: High-precision timestamp.

---

## 4. Usage Aggregation & Reporting

The endpoint `GET /api/v1/ai/usage?days=30` aggregates metrics across any time window:
- Total inferences, success rate percentage, and error count.
- Local vs. cloud execution ratio (e.g. `83% Local / 17% Cloud`).
- Total prompt and completion token volume.
- Cumulative estimated financial spend.
- Average response latency.
- Per-provider and per-model consumption breakdowns.
