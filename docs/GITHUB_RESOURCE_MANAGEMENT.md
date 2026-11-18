# Stage 22: GitHub Resource Management & Quota Economics

## 1. Resource Limits & Sizing Boundaries

To prevent runaway CPU, memory, or network utilization on applicant machines, Stage 22 enforces strict operational ceilings:

| Parameter | Operational Threshold | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Max File Inspection Size** | 500 KB (512,000 bytes) | `SourceFilter.should_inspect_file()` |
| **Max Files Per Repository** | 60 files | `SourceTreeInspector` candidate truncation |
| **Max Memory Per Repo Analysis** | 10 MB in-memory buffer | Ephemeral file release after manifest parsing |
| **Max Concurrent Tree Fetches** | 2 concurrent HTTP requests | Semaphore-bounded worker execution |
| **Analysis Job Timeout** | 60 seconds | `asyncio.wait_for()` timeout wrapping |

---

## 2. API Quota Budgeting

GitHub APIs impose strict per-hour request allocations:
- **Public / Unauthenticated**: 60 requests/hr.
- **Authenticated PAT**: 5,000 requests/hr.

### 2.1 Optimization Techniques
1. **Recursive Git Trees**: One API call (`GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1`) discovers up to 100,000 files in a single network round-trip, avoiding recursive folder queries.
2. **ETag Conditional Headers**: All discovery endpoints utilize `If-None-Match`. Unchanged repositories return `304 Not Modified` and consume zero rate-limit tokens.
3. **Selective Analysis**: The applicant explicitly toggles which repositories to analyze (`is_selected`), preventing unwanted bulk downloads of dormant or archived projects.
4. **Proactive Throttling**: The `RateLimitController` calculates remaining request headroom. When remaining requests fall below 10%, non-essential metadata sync is deferred, reserving capacity for user-initiated actions.
