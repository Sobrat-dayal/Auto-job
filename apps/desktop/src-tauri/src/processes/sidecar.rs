//! Backend sidecar executable resolution and process command builder.
//! Supports both packaged standalone binary execution and development-mode virtualenv fallback.

use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Clone, PartialEq)]
pub enum BackendMode {
    PackagedSidecar(PathBuf),
    DevelopmentVenv {
        python_exe: PathBuf,
        working_dir: PathBuf,
    },
}

/// Resolves the backend executable and working directory.
pub fn resolve_backend_target(app_dir: Option<&Path>) -> Result<BackendMode, String> {
    // 1. Check for packaged sidecar executable in Tauri bin or resources
    let target_triples = ["x86_64-pc-windows-msvc", "x86_64-pc-windows-gnu"];
    for triple in &target_triples {
        let binary_name = format!("autonom-api-{}.exe", triple);

        // Check alongside executable
        if let Ok(current_exe) = std::env::current_exe() {
            if let Some(exe_dir) = current_exe.parent() {
                let candidate = exe_dir.join(&binary_name);
                if candidate.exists() {
                    return Ok(BackendMode::PackagedSidecar(candidate));
                }
                let bin_candidate = exe_dir.join("bin").join(&binary_name);
                if bin_candidate.exists() {
                    return Ok(BackendMode::PackagedSidecar(bin_candidate));
                }
            }
        }

        // Check in app directory
        if let Some(base) = app_dir {
            let candidate = base.join("bin").join(&binary_name);
            if candidate.exists() {
                return Ok(BackendMode::PackagedSidecar(candidate));
            }
        }
    }

    // 2. Development mode fallback: locate services/api/.venv/Scripts/python.exe
    let mut search_dirs = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        search_dirs.push(cwd.clone());
        if let Some(parent) = cwd.parent() {
            search_dirs.push(parent.to_path_buf());
            if let Some(grandparent) = parent.parent() {
                search_dirs.push(grandparent.to_path_buf());
            }
        }
    }

    // Also check standard workspace root path
    search_dirs.push(PathBuf::from("E:\\proooo\\AUTO JOB"));

    for dir in search_dirs {
        let venv_python = dir
            .join("services")
            .join("api")
            .join(".venv")
            .join("Scripts")
            .join("python.exe");
        if venv_python.exists() {
            let api_dir = dir.join("services").join("api");
            return Ok(BackendMode::DevelopmentVenv {
                python_exe: venv_python,
                working_dir: api_dir,
            });
        }
    }

    Err(
        "Could not locate packaged backend sidecar or development Python virtual environment."
            .to_string(),
    )
}

/// Constructs the process Command for launching the backend.
pub fn build_backend_command(mode: &BackendMode, port: u16, api_key: &str) -> Command {
    match mode {
        BackendMode::PackagedSidecar(exe_path) => {
            let mut cmd = Command::new(exe_path);
            cmd.arg("--port").arg(port.to_string());
            cmd.arg("--host").arg("127.0.0.1");
            cmd.env("AUTONOM_API_KEY", api_key);
            cmd.env("PYTHONUNBUFFERED", "1");
            if let Some(parent) = exe_path.parent() {
                cmd.current_dir(parent);
            }
            cmd
        }
        BackendMode::DevelopmentVenv {
            python_exe,
            working_dir,
        } => {
            let mut cmd = Command::new(python_exe);
            cmd.arg("-m");
            cmd.arg("uvicorn");
            cmd.arg("app.main:app");
            cmd.arg("--host");
            cmd.arg("127.0.0.1");
            cmd.arg("--port");
            cmd.arg(port.to_string());
            cmd.arg("--log-level");
            cmd.arg("info");
            cmd.current_dir(working_dir);
            cmd.env("AUTONOM_API_KEY", api_key);
            cmd.env("PYTHONUNBUFFERED", "1");
            cmd
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_backend_target_dev() {
        let target = resolve_backend_target(None);
        assert!(
            target.is_ok(),
            "Expected development venv to resolve: {:?}",
            target
        );
        if let Ok(BackendMode::DevelopmentVenv { python_exe, .. }) = target {
            assert!(python_exe.exists(), "Resolved python_exe must exist");
        }
    }

    #[test]
    fn test_build_backend_command_dev() {
        let mode = BackendMode::DevelopmentVenv {
            python_exe: PathBuf::from("python.exe"),
            working_dir: PathBuf::from("."),
        };
        let cmd = build_backend_command(&mode, 8765, "test-key");
        assert_eq!(cmd.get_program(), "python.exe");
    }
}
