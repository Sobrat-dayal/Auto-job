# Monitoring Resource Budgets & Rate Limit Management (Stage 30)

## 1. Budget Controller Architecture
The `BudgetController` prevents API exhaustion, rate-limit bans, and high resource utilization across background monitoring operations.

### Constraints Enforced
1. **Global Concurrency Limit**:
   - Caps simultaneously executing monitoring runs (default: 3 concurrent runs).
   - Subsequent watch runs queue in `pending` state until an active worker releases its lease.
2. **Daily Request Quota**:
   - Tracks total HTTP requests issued across all providers in a 24-hour UTC window (default: 500 requests/day).
   - Resets automatically at 00:00 UTC.
3. **Provider Rate Limit Cooldowns**:
   - When an upstream source returns HTTP 429 or `Retry-After`, the provider is placed on a timed cooldown (`is_in_cooldown(provider) == True`).
   - Watches targeting that source defer execution until the cooldown timer expires.
4. **Minimum Interval Guard**:
   - All recurring watch schedules enforce a strict lower bound of $\ge 5$ minutes to eliminate aggressive polling.
