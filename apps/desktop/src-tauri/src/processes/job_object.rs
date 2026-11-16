//! Windows Job Object containment for child processes.
//! Ensures that when AUTONOM desktop exits or is killed, Windows kernel terminates all managed child processes.

use std::os::windows::io::AsRawHandle;
use std::process::Child;
use windows_sys::Win32::Foundation::{CloseHandle, HANDLE};
use windows_sys::Win32::System::JobObjects::{
    AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
    SetInformationJobObject, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
};

pub struct JobObject {
    handle: HANDLE,
}

// Job handles are safe to send across threads
unsafe impl Send for JobObject {}
unsafe impl Sync for JobObject {}

impl JobObject {
    /// Creates a new Windows Job Object configured to kill child processes when closed.
    pub fn create() -> Result<Self, String> {
        unsafe {
            let handle = CreateJobObjectW(std::ptr::null(), std::ptr::null());
            if handle.is_null() {
                return Err("Failed to create Win32 Job Object".to_string());
            }

            let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;

            let success = SetInformationJobObject(
                handle,
                JobObjectExtendedLimitInformation,
                &info as *const _ as *const std::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            );

            if success == 0 {
                CloseHandle(handle);
                return Err("Failed to set JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE".to_string());
            }

            Ok(Self { handle })
        }
    }

    /// Assigns a running child process to the job object.
    pub fn assign_child(&self, child: &Child) -> Result<(), String> {
        let process_handle = child.as_raw_handle() as HANDLE;
        unsafe {
            let success = AssignProcessToJobObject(self.handle, process_handle);
            if success == 0 {
                return Err(format!(
                    "Failed to assign process {} to Job Object",
                    child.id()
                ));
            }
        }
        Ok(())
    }
}

impl Drop for JobObject {
    fn drop(&mut self) {
        if !self.handle.is_null() {
            unsafe {
                CloseHandle(self.handle);
            }
        }
    }
}
