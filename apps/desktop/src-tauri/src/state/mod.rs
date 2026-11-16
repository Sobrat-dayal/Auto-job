//! AUTONOM Desktop Application State & Settings Persistence
//! Handles desktop preferences, window layout restoration, and supervisor state tracking.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct SavedWindowState {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
    pub maximized: bool,
    pub selected_module: String,
}

impl Default for SavedWindowState {
    fn default() -> Self {
        Self {
            x: 100,
            y: 100,
            width: 1440,
            height: 900,
            maximized: false,
            selected_module: "command-center".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DesktopSettings {
    pub close_to_tray: bool,
    pub start_at_login: bool,
    pub notifications_enabled: bool,
    pub notify_on_task_completion: bool,
    pub notify_on_backend_events: bool,
    pub window: SavedWindowState,
}

impl Default for DesktopSettings {
    fn default() -> Self {
        Self {
            close_to_tray: true,
            start_at_login: false,
            notifications_enabled: true,
            notify_on_task_completion: true,
            notify_on_backend_events: true,
            window: SavedWindowState::default(),
        }
    }
}

pub fn get_settings_file_path() -> PathBuf {
    let local_appdata = std::env::var("LOCALAPPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("C:\\Users\\Default\\AppData\\Local"));
    let config_dir = local_appdata.join("AUTONOM").join("config");
    let _ = fs::create_dir_all(&config_dir);
    config_dir.join("desktop_settings.json")
}

pub fn load_desktop_settings() -> DesktopSettings {
    let path = get_settings_file_path();
    if path.exists() {
        if let Ok(content) = fs::read_to_string(&path) {
            if let Ok(settings) = serde_json::from_str::<DesktopSettings>(&content) {
                return settings;
            }
        }
    }
    let defaults = DesktopSettings::default();
    save_desktop_settings(&defaults);
    defaults
}

pub fn save_desktop_settings(settings: &DesktopSettings) {
    let path = get_settings_file_path();
    if let Ok(json) = serde_json::to_string_pretty(settings) {
        let _ = fs::write(path, json);
    }
}

#[derive(Clone)]
pub struct AppState {
    pub settings: Arc<Mutex<DesktopSettings>>,
    pub active_tasks_count: Arc<AtomicUsize>,
}

impl AppState {
    pub fn new() -> Self {
        let loaded = load_desktop_settings();
        Self {
            settings: Arc::new(Mutex::new(loaded)),
            active_tasks_count: Arc::new(AtomicUsize::new(0)),
        }
    }

    pub fn get_settings(&self) -> DesktopSettings {
        self.settings.lock().unwrap().clone()
    }

    pub fn update_settings<F>(&self, update_fn: F) -> DesktopSettings
    where
        F: FnOnce(&mut DesktopSettings),
    {
        let mut guard = self.settings.lock().unwrap();
        update_fn(&mut guard);
        let cloned = guard.clone();
        save_desktop_settings(&cloned);
        cloned
    }

    pub fn set_active_tasks(&self, count: usize) {
        self.active_tasks_count.store(count, Ordering::Relaxed);
    }

    pub fn get_active_tasks(&self) -> usize {
        self.active_tasks_count.load(Ordering::Relaxed)
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_desktop_settings_default() {
        let settings = DesktopSettings::default();
        assert!(settings.close_to_tray);
        assert!(!settings.start_at_login);
        assert!(settings.notifications_enabled);
        assert_eq!(settings.window.width, 1440);
        assert_eq!(settings.window.height, 900);
        assert_eq!(settings.window.selected_module, "command-center");
    }

    #[test]
    fn test_desktop_settings_serialization() {
        let settings = DesktopSettings::default();
        let json = serde_json::to_string(&settings).expect("Serialization failed");
        assert!(json.contains("\"close_to_tray\":true"));
        let deserialized: DesktopSettings =
            serde_json::from_str(&json).expect("Deserialization failed");
        assert_eq!(settings, deserialized);
    }
}
