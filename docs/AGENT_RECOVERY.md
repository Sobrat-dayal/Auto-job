# Recovery Agent & Fault Remediation (Stage 12)

## 1. Overview

The **Recovery Agent** (`recovery`) intercepts exceptions and verification failures, classifies them into normalized failure categories, and decides appropriate remediation actions to preserve workflow continuity without human intervention whenever possible.

---

## 2. 13 Normalized Failure Categories

1. `PROVIDER_UNAVAILABLE`: Model provider offline or connection refused.
2. `MODEL_UNAVAILABLE`: Requested model name not found on provider.
3. `TIMEOUT`: Execution exceeded step timeout deadline.
4. `RATE_LIMIT`: Cloud provider HTTP 429 quota exhaustion.
5. `INVALID_OUTPUT`: Output failed structural parsing or JSON syntax.
6. `FAILED_VERIFICATION`: Output rejected by Verification Agent.
7. `MISSING_CAPABILITY`: Requested capability not found in registry.
8. `RESOURCE_EXHAUSTED`: GPU VRAM / Host RAM memory exhaustion.
9. `AUTHORIZATION_REQUIRED`: Privileged action requires human approval.
10. `DEPENDENCY_FAILURE`: Upstream dependency failed, blocking this node.
11. `BACKEND_INTERRUPTION`: Backend stopped mid-execution.
12. `CANCELLED_BY_USER`: Explicit user cancellation.
13. `UNKNOWN_EXTERNAL_OUTCOME`: Unhandled edge case.

---

## 3. Remediation Decision Matrix

| Failure Category | Idempotent? | Retry Attempt < Max? | Recovery Action |
|---|---|---|---|
| `TIMEOUT` | Yes | Yes | `retry` (exponential backoff) |
| `RATE_LIMIT` | Yes | Yes | `retry` |
| `PROVIDER_UNAVAILABLE` | Yes | Yes | `alternate_model` (switch to cloud/local fallback) |
| `MODEL_UNAVAILABLE` | Yes | Yes | `alternate_model` |
| `FAILED_VERIFICATION` | Yes | Attempt < 2 | `retry` |
| `FAILED_VERIFICATION` | Any | Retries exhausted | `replan` (revise DAG) |
| `AUTHORIZATION_REQUIRED` | Any | Any | `wait_authorization` |
| `CANCELLED_BY_USER` | Any | Any | `fail` (terminal cancellation) |
| Unrecoverable | Any | Any | `fail` |

---

## 4. Bounded Dynamic Replanning

To prevent infinite loops, replanning is bounded:
- At most **2 dynamic replans** per workflow (`replan_count <= max_replans`).
- Completed steps and valid checkpoints are preserved; only failed or blocked subgraphs are replanned.
