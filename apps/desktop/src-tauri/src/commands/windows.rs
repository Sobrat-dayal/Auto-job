//! Window state, preferences, and multi-monitor validation commands.

use crate::state::{AppState, DesktopSettings, SavedWindowState};
use tauri::{AppHandle, Manager, State};

#[tauri::command]
pub fn get_window_preferences(state: State<'_, AppState>) -> DesktopSettings {
    state.get_settings()
}

#[derive(serde::Deserialize)]
pub struct UpdatePreferencesPayload {
    pub close_to_tray: Option<bool>,
    pub start_at_login: Option<bool>,
    pub notifications_enabled: Option<bool>,
    pub notify_on_task_completion: Option<bool>,
    pub notify_on_backend_events: Option<bool>,
    pub window: Option<SavedWindowState>,
}

#[tauri::command]
pub fn set_window_preferences(
    payload: UpdatePreferencesPayload,
    state: State<'_, AppState>,
) -> Result<DesktopSettings, String> {
    let updated = state.update_settings(|settings| {
        if let Some(v) = payload.close_to_tray {
            settings.close_to_tray = v;
        }
        if let Some(v) = payload.start_at_login {
            settings.start_at_login = v;
        }
        if let Some(v) = payload.notifications_enabled {
            settings.notifications_enabled = v;
        }
        if let Some(v) = payload.notify_on_task_completion {
            settings.notify_on_task_completion = v;
        }
        if let Some(v) = payload.notify_on_backend_events {
            settings.notify_on_backend_events = v;
        }
        if let Some(mut w) = payload.window {
            // Coordinate sanity bounds
            if w.width < 1050 {
                w.width = 1050;
            }
            if w.height < 650 {
                w.height = 650;
            }
            settings.window = w;
        }
    });

    Ok(updated)
}

#[tauri::command]
pub fn save_current_window_state(app: AppHandle, state: State<'_, AppState>) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        if let (Ok(pos), Ok(size), Ok(maximized)) = (
            window.outer_position(),
            window.inner_size(),
            window.is_maximized(),
        ) {
            state.update_settings(|s| {
                s.window.x = pos.x;
                s.window.y = pos.y;
                s.window.width = size.width;
                s.window.height = size.height;
                s.window.maximized = maximized;
            });
        }
    }
    Ok(())
}
