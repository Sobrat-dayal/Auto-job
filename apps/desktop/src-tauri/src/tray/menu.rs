//! System Tray Menu Builder for AUTONOM.

use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::{AppHandle, Wry};

pub struct TrayMenuItems {
    pub open_item: MenuItem<Wry>,
    pub toggle_item: MenuItem<Wry>,
    pub status_item: MenuItem<Wry>,
    pub emergency_stop_item: MenuItem<Wry>,
    pub pause_item: MenuItem<Wry>,
    pub approvals_item: MenuItem<Wry>,
    pub restart_item: MenuItem<Wry>,
    pub activity_item: MenuItem<Wry>,
    pub settings_item: MenuItem<Wry>,
    pub exit_item: MenuItem<Wry>,
}

pub fn create_tray_menu(app: &AppHandle) -> Result<(Menu<Wry>, TrayMenuItems), tauri::Error> {
    let open_item = MenuItem::with_id(app, "open", "Open AUTONOM", true, None::<&str>)?;
    let toggle_item = MenuItem::with_id(app, "toggle", "Hide / Show Window", true, None::<&str>)?;
    let status_item =
        MenuItem::with_id(app, "status", "Backend: Starting...", false, None::<&str>)?;
    let emergency_stop_item =
        MenuItem::with_id(app, "emergency_stop", "EMERGENCY STOP (Halt Swarm)", true, None::<&str>)?;
    let pause_item =
        MenuItem::with_id(app, "pause_automation", "Pause / Resume Automation", true, None::<&str>)?;
    let approvals_item =
        MenuItem::with_id(app, "approvals", "Pending Approvals Queue", true, None::<&str>)?;
    let restart_item = MenuItem::with_id(app, "restart", "Restart Backend", true, None::<&str>)?;
    let activity_item =
        MenuItem::with_id(app, "activity", "Diagnostics & Tasks", true, None::<&str>)?;
    let settings_item =
        MenuItem::with_id(app, "settings", "Storage & Database", true, None::<&str>)?;
    let exit_item = MenuItem::with_id(app, "exit", "Exit AUTONOM", true, None::<&str>)?;

    let menu = Menu::with_items(
        app,
        &[
            &open_item,
            &toggle_item,
            &approvals_item,
            &PredefinedMenuItem::separator(app)?,
            &emergency_stop_item,
            &pause_item,
            &PredefinedMenuItem::separator(app)?,
            &status_item,
            &activity_item,
            &settings_item,
            &PredefinedMenuItem::separator(app)?,
            &restart_item,
            &exit_item,
        ],
    )?;

    let items = TrayMenuItems {
        open_item,
        toggle_item,
        status_item,
        emergency_stop_item,
        pause_item,
        approvals_item,
        restart_item,
        activity_item,
        settings_item,
        exit_item,
    };

    Ok((menu, items))
}
