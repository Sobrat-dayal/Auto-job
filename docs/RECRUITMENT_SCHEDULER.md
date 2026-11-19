# Recruitment Scheduler & Recurrence Engine (Stage 30)

## 1. Scheduling Rules & Recurrence Types
The AUTONOM recruitment scheduler calculates upcoming execution timestamps deterministically using Python's `zoneinfo` and `tzdata`.

### Recurrence Types
1. **`interval`**: Executes every $M$ minutes (minimum enforced: $M \ge 5$).
2. **`hourly`**: Executes at the top of every hour (`:00`).
3. **`daily`**: Executes once per day at a configured local time (e.g. `09:00`).
4. **`weekdays`**: Executes Monday through Friday at configured time; skips Saturday and Sunday.
5. **`weekly` / `selected_days`**: Executes on selected day indices (0=Monday, 6=Sunday).

## 2. Quiet Hours Evaluation
Quiet hours support cross-midnight intervals (e.g., `22:00` to `08:00`) evaluated against the configured IANA timezone:
- **`mute_notifications`**: Monitoring runs continue silently; generated notifications are staged in the outbox as `deferred_by_quiet_hours`.
- **`pause_source_monitoring`**: Network calls to external boards and career pages are completely suspended until quiet hours elapse.

## 3. Missed Run Policies
When the host computer sleeps or restarts:
- **`skip`**: Drops missed past executions and aligns to the next future scheduled occurrence.
- **`run_latest_due`**: Executes exactly one catch-up run for the latest missed slot upon wake/reboot.
- **`run_once_after_restart`**: Similar to `run_latest_due`, triggers immediate catch-up.
- **`require_review`**: Flags the watch for user confirmation if downtime exceeded 7 days.
