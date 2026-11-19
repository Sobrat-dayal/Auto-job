# Windows 11 Background Monitoring & Lifecycle Management (Stage 30)

## 1. Desktop Lifecycle Integration
AUTONOM is designed for continuous, respectful operation within Windows 11 desktop environments.

### Supported Operating Modes
1. **Interactive Foreground**: Real-time progress indicators, interactive opportunity tables, and direct manual execution.
2. **Minimized / System Tray**: Background monitoring continues quietly; notifications appear via Windows toast notifications (respecting privacy mode).
3. **Power Event Awareness (Sleep / Wake)**:
   - Upon system suspend/sleep, active timers freeze safely.
   - Upon system wake/resume, the `WindowsLifecycleManager` inspects elapsed downtime, purges stale worker leases, and reconciles missed executions according to each watch's policy.
4. **Battery Power Policy**:
   - Optional `pause_on_battery` setting halts non-urgent background network requests when running on battery to conserve host energy.

## 2. Notification Privacy Protection
When `notification_privacy_mode` is enabled, desktop toast notifications conceal sensitive details (such as employer names, job titles, or salary figures) to protect applicant privacy in shared office or screen-sharing environments, surfacing an actionable link back to the local workspace.
