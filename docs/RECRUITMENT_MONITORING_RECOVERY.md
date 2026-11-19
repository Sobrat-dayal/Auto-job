# Recruitment Monitoring Failure Recovery & Self-Healing (Stage 30)

## 1. Failure Scenarios & Recovery Strategies

| Scenario | Symptom | Self-Healing Strategy |
|---|---|---|
| **Process Crash Mid-Run** | Worker lease remains held in SQLite | Leases have a strict 120s TTL. On startup or expiration, `clear_expired_leases` reclaims or purges orphaned leases. |
| **System Sleep / Hibernation** | Clock advances significantly during pause | `WindowsLifecycleManager.reconcile_after_wake` inspects elapsed downtime, clears expired leases, and triggers `evaluate_missed_run`. |
| **Provider HTTP 429** | Upstream rate-limit reached | Records provider cooldown, marks watch `rate_limited`, and defers future polling until retry timestamp. |
| **Consecutive Watch Failures** | $N \ge 3$ consecutive errors | Marks watch `suspended` and alerts user to review credentials or URL. |
| **Database Disconnection** | SQLite lock contention | Handled via configured 10s `busy_timeout` and WAL mode retry loops. |
| **Emergency Stop Triggered** | Global stop activated | Master coordinator immediately checks `EmergencyStopController` before every run, aborting in-flight tasks safely. |
