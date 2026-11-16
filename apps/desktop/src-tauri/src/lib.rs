pub mod commands;
pub mod notifications;
pub mod processes;
pub mod state;
pub mod tray;

pub use commands::AppInfo;
pub use processes::{BackendProcessStatus, BackendState, BackendSupervisor};
pub use state::{AppState, DesktopSettings};

use tauri::{Manager, PhysicalPosition, PhysicalSize};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app_state = AppState::new();
    let supervisor = BackendSupervisor::new(8765, "dev-local-autonom-key".to_string());

    let sup_clone = supervisor.clone();

    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::default(),
            Some(vec!["--minimized"]),
        ))
        .manage(app_state.clone())
        .manage(supervisor.clone())
        .invoke_handler(tauri::generate_handler![
            commands::get_app_info,
            commands::get_desktop_status,
            commands::get_backend_status,
            commands::restart_backend,
            commands::get_window_preferences,
            commands::set_window_preferences,
            commands::save_current_window_state,
            commands::open_artifact_location,
            commands::test_notification,
        ])
        .setup(move |app| {
            // Setup system tray
            let handle = app.handle();
            let _ = tray::setup_tray(handle, supervisor.clone(), app_state.clone());

            // Restore saved window state
            let settings = app_state.get_settings();
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_size(PhysicalSize::new(settings.window.width, settings.window.height));
                if settings.window.x > 0 && settings.window.y > 0 {
                    let _ = window.set_position(PhysicalPosition::new(settings.window.x, settings.window.y));
                }
                if settings.window.maximized {
                    let _ = window.maximize();
                }
            }

            // Start managed backend sidecar
            if let Err(e) = supervisor.start() {
                eprintln!("[AUTONOM-BOOT] Warning: initial backend start reported: {}", e);
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                let app_state = window.state::<AppState>();
                if app_state.get_settings().close_to_tray {
                    api.prevent_close();
                    let _ = window.hide();
                }
            }
        })
        .build(tauri::generate_context!())
        .expect("error while running AUTONOM desktop application")
        .run(move |_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                eprintln!("[AUTONOM-SHUTDOWN] Application exit requested. Ensuring child backend is terminated.");
                sup_clone.stop();
            }
        });
}
