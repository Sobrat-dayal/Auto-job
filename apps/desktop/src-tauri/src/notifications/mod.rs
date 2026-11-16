//! Native Windows Toast Notification Subsystem.
//! Respects user notification preferences, categories, and quiet mode.

use crate::state::AppState;
use tauri::AppHandle;
use tauri_plugin_notification::NotificationExt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NotificationCategory {
    BackendEvent,
    TaskCompletion,
    TaskFailure,
    SystemAlert,
}

pub fn send_desktop_notification(
    app: &AppHandle,
    state: &AppState,
    category: NotificationCategory,
    title: &str,
    body: &str,
) {
    let settings = state.get_settings();
    if !settings.notifications_enabled {
        return;
    }

    match category {
        NotificationCategory::BackendEvent => {
            if !settings.notify_on_backend_events {
                return;
            }
        }
        NotificationCategory::TaskCompletion => {
            if !settings.notify_on_task_completion {
                return;
            }
        }
        NotificationCategory::TaskFailure | NotificationCategory::SystemAlert => {
            // Always sent if notifications are globally enabled
        }
    }

    // Fire native toast notification
    let _ = app.notification().builder().title(title).body(body).show();
}
