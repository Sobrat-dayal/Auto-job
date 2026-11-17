//! System tray integration for AUTONOM desktop.

pub mod menu;

use crate::processes::BackendSupervisor;
use crate::state::AppState;
use menu::create_tray_menu;
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Emitter, Manager};

pub fn setup_tray(
    app: &AppHandle,
    supervisor: BackendSupervisor,
    state: AppState,
) -> Result<(), tauri::Error> {
    let (menu, _items) = create_tray_menu(app)?;

    let sup_clone = supervisor.clone();
    let _state_clone = state.clone();

    let _tray = TrayIconBuilder::new()
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(move |app, event| match event.id.as_ref() {
            "open" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                }
            }
            "toggle" => {
                if let Some(window) = app.get_webview_window("main") {
                    if let Ok(visible) = window.is_visible() {
                        if visible {
                            let _ = window.hide();
                        } else {
                            let _ = window.show();
                            let _ = window.unminimize();
                            let _ = window.set_focus();
                        }
                    }
                }
            }
            "emergency_stop" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                    let _ = window.emit("trigger_emergency_stop", ());
                }
            }
            "pause_automation" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.emit("toggle_automation_pause", ());
                }
            }
            "approvals" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                    let _ = window.emit("navigate_module", "approvals");
                }
            }
            "activity" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                    let _ = window.emit("navigate_module", "diagnostics");
                }
            }
            "settings" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                    let _ = window.emit("navigate_module", "storage");
                }
            }
            "restart" => {
                let s = sup_clone.clone();
                std::thread::spawn(move || {
                    let _ = s.restart();
                });
            }
            "exit" => {
                eprintln!("[AUTONOM] User selected Exit from tray menu.");
                sup_clone.stop();
                app.exit(0);
            }
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    if let Ok(visible) = window.is_visible() {
                        if visible {
                            let _ = window.hide();
                        } else {
                            let _ = window.show();
                            let _ = window.unminimize();
                            let _ = window.set_focus();
                        }
                    }
                }
            }
        })
        .build(app)?;

    Ok(())
}
