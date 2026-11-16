#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    autonom_desktop_lib::run();
}

#[cfg(test)]
mod tests {
    use autonom_desktop_lib::commands::*;

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
}
