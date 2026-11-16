//! Application info, desktop status, and filesystem commands.

use crate::notifications::{send_desktop_notification, NotificationCategory};
use crate::state::{AppState, DesktopSettings};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::{AppHandle, State};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AppInfo {
    pub name: String,
    pub version: String,
    pub tauri_version: String,
    pub os: String,
    pub arch: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DesktopStatus {
    pub app_info: AppInfo,
    pub active_tasks_count: usize,
    pub settings: DesktopSettings,
}

pub fn get_app_info_internal() -> AppInfo {
    AppInfo {
        name: "AUTONOM".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        tauri_version: tauri::VERSION.to_string(),
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
    }
}

#[tauri::command]
pub fn get_app_info() -> AppInfo {
    get_app_info_internal()
}

#[tauri::command]
pub fn get_desktop_status(state: State<'_, AppState>) -> DesktopStatus {
    DesktopStatus {
        app_info: get_app_info_internal(),
        active_tasks_count: state.get_active_tasks(),
        settings: state.get_settings(),
    }
}

#[tauri::command]
pub fn open_artifact_location(relative_or_absolute: String) -> Result<bool, String> {
    let local_appdata = std::env::var("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("C:\\Users\\Default\\AppData\\Local"));
    let allowed_root = local_appdata.join("AUTONOM");

    let target_path = if PathBuf::from(&relative_or_absolute).is_absolute() {
        PathBuf::from(&relative_or_absolute)
    } else {
        allowed_root.join(&relative_or_absolute)
    };

    // Traversal check: Target path must start with allowed_root
    if !target_path.starts_with(&allowed_root) && !target_path.starts_with("E:\\proooo\\AUTO JOB") {
        return Err("Access denied: path is outside allowed application directories.".to_string());
    }

    if !target_path.exists() {
        return Err(format!("Path does not exist: {:?}", target_path));
    }

    // Windows explorer /select
    let mut cmd = std::process::Command::new("explorer.exe");
    if target_path.is_file() {
        cmd.arg("/select,").arg(target_path.as_os_str());
    } else {
        cmd.arg(target_path.as_os_str());
    }

    cmd.spawn()
        .map(|_| true)
        .map_err(|e| format!("Failed to open Windows File Explorer: {}", e))
}

#[tauri::command]
pub fn test_notification(app: AppHandle, state: State<'_, AppState>) -> Result<bool, String> {
    send_desktop_notification(
        &app,
        &state,
        NotificationCategory::SystemAlert,
        "AUTONOM Desktop Notification",
        "Native Windows toast notification system is active and verified.",
    );
    Ok(true)
}
