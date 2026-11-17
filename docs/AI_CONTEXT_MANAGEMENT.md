# AUTONOM — AI Context Budgeting & Token Management (Stage 11)

## 1. Token Counting Architecture

AUTONOM implements precise token counting using OpenAI's official `tiktoken` library with the `cl100k_base` BPE tokenizer (`services/api/app/ai/context.py`).

If `tiktoken` is unavailable or encounters unsupported encodings, a heuristic fallback (character count divided by 4 with word boundary weighting) is applied with explicit attribution (`source="estimated"`).

```python
# Context Budget Manager
manager = ContextBudgetManager(model_id="gpt-4o", context_window=128000, safety_margin=512)
total_tokens = manager.count_messages_tokens(messages, system_prompt=system_prompt)
```

---

## 2. Context Window Ceilings & Safety Margins

Every model has an enforced context ceiling with an automatic safety margin reserved for formatting overhead, tool definitions, and system roles:

| Model ID | Total Context Window | Safety Margin | Max Usable Input Tokens | Max Output Tokens |
| :--- | :---: | :---: | :---: | :---: |
| `llama3.2:3b` | 8,192 | 512 | 7,680 | 4,096 |
| `llama3:8b` | 8,192 | 512 | 7,680 | 4,096 |
| `qwen2.5-coder:7b` | 32,768 | 1,024 | 31,744 | 8,192 |
| `gpt-4o-mini` | 128,000 | 2,048 | 125,952 | 16,384 |
| `gpt-4o` | 128,000 | 2,048 | 125,952 | 4,096 |

---

## 3. History Auto-Pruning Heuristics

When multi-turn conversations or agent scratchpads threaten to exceed a model's context ceiling, `ContextBudgetManager.truncate_messages_to_budget()` applies a prioritized preservation strategy:

1. **System Prompt & Current User Prompt**: Always preserved with highest priority.
2. **Recent Conversation Turns**: Preserved in reverse chronological order (newest turns kept first).
3. **Older Intermediate Turns**: Gracefully evicted from context with an explicit truncation notice injected into the context stream.
4. **Hard Limit Enforcement**: If even the initial prompt exceeds the total context ceiling after pruning, execution halts immediately with `ContextLimitExceededError`.
