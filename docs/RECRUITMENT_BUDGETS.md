# AUTONOM Recruitment Budgets & Multi-Agent Concurrency

## Stage 25 of 50 — Safety Caps & Quota Management

---

### The Overbooking Problem

When multiple autonomous agents (Scouting Agent, Tailoring Agent, Application Agent) operate concurrently on Windows desktop or via browser automation, race conditions can cause application caps to be exceeded before state updates propagate.

```
Agent A (Attempt 10) ──┐
                       ├──► [ Race Condition ] ──► 11 Applications (Limit 10 Breached!)
Agent B (Attempt 10) ──┘
```

---

### Two-Phase Atomic Reservation Protocol

AUTONOM solves this using an asynchronous two-phase reservation protocol backed by `asyncio.Lock`:

```
               Agent Worker                        ApplicationBudgetController
                    │                                           │
                    │─── 1. reserve_slot(agent_id, job_id) ────►│ Check available slots
                    │                                           │ (count + reservations < limit)
                    │◄── 2. reservation_id (TTL: 300s) ─────────│ Place atomic reservation lock
                    │                                           │
         [ Prepare application ]                                │
                    │                                           │
   ┌────────────────┴────────────────┐                          │
   │ Success                         │ Failure / User abort     │
   ▼                                 ▼                          │
   │─── 3. confirm_slot(res_id) ────►│ Release reservation      │─── 3. release_slot(res_id) ────►
   │                                 │ Increment count          │                                 │ Release reservation
   │◄── 4. confirmed ────────────────│                          │◄── 4. released ─────────────────│ No count increment
```

---

### Quotas & Reset Lifecycles

- **`daily_application_limit`**: Resets at 00:00 UTC daily.
- **`weekly_application_limit`**: Resets on Monday 00:00 UTC.
- **`monthly_application_limit`**: Resets on the 1st of each calendar month.
- **`daily_discovery_limit` / `daily_preparations_limit`**: Safety throttle on web traffic and local LLM tokens.
