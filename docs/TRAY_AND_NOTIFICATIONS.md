# AUTONOM System Tray & Native Windows Notifications

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Executive Summary

As a background autonomous assistant, AUTONOM must operate unobtrusively while keeping the user informed of critical events. Stage 05 implements native Windows 11 shell integration through a **System Tray icon** with interactive context menus, left-click quick access, close-to-tray background execution, and native **Windows Action Center toast notifications**.

---

## 2. System Tray Architecture (`apps/desktop/src-tauri/src/tray/`)

The system tray is initialized on the Tauri application builder and binds to the Windows notification area.

### 2.1 Context Menu Structure

The tray context menu (`tray/menu.rs`) exposes:

1. **Open AUTONOM**: Restores and focuses the main window.
2. **Hide / Show Window**: Toggles window visibility.
3. _--- Separator ---_
4. **Backend Status: Ready**: Dynamic read-only indicator reflecting the sidecar supervisor state.
5. **Active Tasks: 0**: Real-time counter of currently executing agent tasks.
6. _--- Separator ---_
7. **Restart Backend**: Directly triggers supervisor restart without requiring the main UI.
8. **Settings**: Opens the settings dialog or focuses the application preferences.
9. _--- Separator ---_
10. **Exit AUTONOM**: Performs full graceful shutdown of the desktop shell and the backend sidecar.

### 2.2 User Interactions

- **Left Click**: Toggles the window between shown (and focused) and hidden in the tray.
- **Right Click**: Displays the context menu.
- **Double Click**: Restores and brings the main window to the foreground.

---

## 3. Windows Native Notifications (`apps/desktop/src-tauri/src/notifications/`)

AUTONOM uses `tauri-plugin-notification` to deliver rich notifications via the Windows 11 WinRT notification infrastructure.

### 3.1 Notification Categories

- **Task**: Dispatched upon task start, progress milestones, or completion.
- **Agent**: Dispatched when an agent requires user authorization, reaches a decision point, or completes a workflow.
- **System**: Dispatched on backend restarts, supervisor errors, or database snapshot completions.
- **Security**: Dispatched on credential access, permission escalation requests, or boundary events.

### 3.2 Notification Preferences & Quiet Mode

Users can configure notification delivery in `desktop_settings.json`:

- `notifications_enabled`: Master switch for all notifications.
- `notify_on_task_completion`: Dispatches toast when long-running background tasks finish.
- `notify_on_backend_events`: Alerts user if the backend encounters an unrecoverable failure.

---

## 4. Testing Notification Dispatch

Notifications can be verified in both developer mode and production via the native command:

```typescript
import { testDesktopNotification } from '@/services/tauri';

// Triggers native toast in Windows Action Center
await testDesktopNotification(
  'AUTONOM Desktop Shell',
  'Windows 11 notification center test successful!'
);
```

Or via the **Desktop Shell** diagnostics panel in the user interface.
