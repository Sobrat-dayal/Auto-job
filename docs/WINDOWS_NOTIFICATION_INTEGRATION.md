# Windows Notification Integration & Outbox Dispatcher (Stage 30)

## 1. Durable Notification Outbox
All desktop notifications are queued in the durable `recruitment_notification_outbox` table before delivery. This guarantees zero message loss during system restart, application minimization, or network interruptions.

## 2. Notification Delivery Pipeline
1. **Outbox Polling**: Worker checks for entries with status `ready` or `deferred_by_quiet_hours`.
2. **Quiet Hours Check**: If quiet hours are currently active in the user's timezone, status is marked `deferred_by_quiet_hours`.
3. **Privacy Sanitization**: When privacy mode is active, sensitive strings (employer names, salaries) are redacted.
4. **Desktop Dispatch**: Emits native Windows desktop toast notifications or in-app snackbars.
5. **Mark as Delivered / Read**: Updates outbox record status to `delivered_where_confirmed` or `read`.
