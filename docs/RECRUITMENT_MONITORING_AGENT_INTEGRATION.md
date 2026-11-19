# Recruitment Monitoring Agent Integration (Stage 30)

## 1. Registered Agent Capabilities
Stage 30 registers 14 typed capabilities under the `recruitment.monitoring.*` namespace:

| Capability ID | Description |
|---|---|
| `recruitment.monitoring.status` | Inspects overview KPIs and scheduler state |
| `recruitment.monitoring.watch.create` | Creates a new recurring job watch |
| `recruitment.monitoring.watch.list` | Lists active and configured job watches |
| `recruitment.monitoring.watch.pause` | Pauses recurring executions for a watch |
| `recruitment.monitoring.watch.resume` | Resumes a paused job watch |
| `recruitment.monitoring.watch.preview` | Previews upcoming occurrences and request budgets |
| `recruitment.monitoring.run.trigger` | Triggers an immediate manual discovery run |
| `recruitment.monitoring.run.list` | Lists historical monitoring runs and telemetry |
| `recruitment.monitoring.queue.list` | Lists opportunities from the prioritized queue |
| `recruitment.monitoring.queue.action` | Applies user action (save, prioritize, defer, exclude) |
| `recruitment.monitoring.changes.list` | Inspects material vacancy changes and closures |
| `recruitment.monitoring.alerts.list` | Lists notifications and unread alerts |
| `recruitment.monitoring.alerts.ack` | Acknowledges or dismisses alerts |
| `recruitment.monitoring.diagnostics` | Generates system diagnostics and worker lease report |
