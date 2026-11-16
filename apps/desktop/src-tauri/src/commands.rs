use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AppInfo {
    pub name: String,
    pub version: String,
    pub tauri_version: String,
    pub os: String,
    pub arch: String,
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
