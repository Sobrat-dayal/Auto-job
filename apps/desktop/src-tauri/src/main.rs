#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    autonom_desktop_lib::run();
}

#[cfg(test)]
mod tests {
    use autonom_desktop_lib::commands::*;
    use autonom_desktop_lib::processes::*;
    use autonom_desktop_lib::state::*;
    use std::path::PathBuf;

    #[test]
    fn test_get_app_info_internal() {
        let info = get_app_info_internal();
        assert_eq!(info.name, "AUTONOM");
        assert_eq!(info.version, "0.1.0");
        assert!(!info.tauri_version.is_empty());
        assert!(!info.os.is_empty());
        assert!(!info.arch.is_empty());
    }

    #[test]
    fn test_app_info_serialization() {
        let info = get_app_info_internal();
        let json = serde_json::to_string(&info).expect("Failed to serialize AppInfo");
        assert!(json.contains("\"name\":\"AUTONOM\""));
        assert!(json.contains("\"version\":\"0.1.0\""));

        let deserialized: AppInfo =
            serde_json::from_str(&json).expect("Failed to deserialize AppInfo");
        assert_eq!(info, deserialized);
    }

    #[test]
    fn test_supervisor_initial_state() {
        let supervisor = BackendSupervisor::new(8765, "test-token".to_string());
        let status = supervisor.get_status();
        assert_eq!(status.state, BackendState::Stopped);
        assert_eq!(status.port, 8765);
        assert_eq!(status.restart_count, 0);
        assert_eq!(status.max_restarts, 5);
        assert!(!status.database_ready);
    }

    #[test]
    fn test_desktop_settings_defaults() {
        let settings = DesktopSettings::default();
        assert!(settings.close_to_tray);
        assert!(!settings.start_at_login);
        assert!(settings.notifications_enabled);
        assert_eq!(settings.window.width, 1440);
        assert_eq!(settings.window.height, 900);
    }

    #[test]
    fn test_resolve_backend_target() {
        let target = resolve_backend_target(None);
        assert!(
            target.is_ok(),
            "Expected development Python venv to resolve"
        );
        if let Ok(BackendMode::DevelopmentVenv {
            python_exe,
            working_dir,
        }) = target
        {
            assert!(python_exe.exists(), "Python executable must exist on disk");
            assert!(working_dir.exists(), "Working directory must exist on disk");
        }
    }

    #[test]
    fn test_build_backend_command() {
        let mode = BackendMode::DevelopmentVenv {
            python_exe: PathBuf::from("python.exe"),
            working_dir: PathBuf::from("."),
        };
        let cmd = build_backend_command(&mode, 8765, "secret-token");
        assert_eq!(cmd.get_program(), "python.exe");
    }
}
