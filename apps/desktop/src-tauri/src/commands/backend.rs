//! Backend process supervisor commands.

use crate::processes::{BackendProcessStatus, BackendSupervisor};
use tauri::State;

#[tauri::command]
pub fn get_backend_status(supervisor: State<'_, BackendSupervisor>) -> BackendProcessStatus {
    supervisor.get_status()
}

#[tauri::command]
pub fn restart_backend(
    supervisor: State<'_, BackendSupervisor>,
) -> Result<BackendProcessStatus, String> {
    supervisor.restart()?;
    Ok(supervisor.get_status())
}
