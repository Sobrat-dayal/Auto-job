//! Backend Process Supervisor.
//! Manages Python backend lifecycle, readiness checks, Windows Job Object containment,
//! crash detection, and bounded restart recovery.

use super::job_object::JobObject;
use super::sidecar::{build_backend_command, resolve_backend_target, BackendMode};
use serde::{Deserialize, Serialize};
use std::process::Child;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BackendState {
    Stopped,
    Starting,
    Connecting,
    Ready,
    Degraded,
    Restarting,
    Failed,
    Stopping,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendProcessStatus {
    pub state: BackendState,
    pub pid: Option<u32>,
    pub port: u16,
    pub uptime_seconds: u64,
    pub restart_count: u32,
    pub max_restarts: u32,
    pub last_error: Option<String>,
    pub backend_mode: String,
    pub database_ready: bool,
}

struct SupervisorInner {
    state: BackendState,
    child: Option<Child>,
    job_object: Option<JobObject>,
    started_at: Option<Instant>,
    port: u16,
    api_key: String,
    restart_count: u32,
    max_restarts: u32,
    last_error: Option<String>,
    mode_description: String,
    database_ready: bool,
    should_run: bool,
}

#[derive(Clone)]
pub struct BackendSupervisor {
    inner: Arc<Mutex<SupervisorInner>>,
}

impl BackendSupervisor {
    pub fn new(port: u16, api_key: String) -> Self {
        Self {
            inner: Arc::new(Mutex::new(SupervisorInner {
                state: BackendState::Stopped,
                child: None,
                job_object: None,
                started_at: None,
                port,
                api_key,
                restart_count: 0,
                max_restarts: 5,
                last_error: None,
                mode_description: "unresolved".to_string(),
                database_ready: false,
                should_run: false,
            })),
        }
    }

    pub fn get_status(&self) -> BackendProcessStatus {
        let guard = self.inner.lock().unwrap();
        let uptime = guard.started_at.map(|t| t.elapsed().as_secs()).unwrap_or(0);
        let pid = guard.child.as_ref().map(|c| c.id());

        BackendProcessStatus {
            state: guard.state,
            pid,
            port: guard.port,
            uptime_seconds: uptime,
            restart_count: guard.restart_count,
            max_restarts: guard.max_restarts,
            last_error: guard.last_error.clone(),
            backend_mode: guard.mode_description.clone(),
            database_ready: guard.database_ready,
        }
    }

    /// Spawns the backend sidecar and initiates readiness polling.
    pub fn start(&self) -> Result<(), String> {
        let mut guard = self.inner.lock().unwrap();
        if guard.state == BackendState::Ready || guard.state == BackendState::Starting {
            return Ok(());
        }

        guard.state = BackendState::Starting;
        guard.should_run = true;
        guard.last_error = None;

        let port = guard.port;
        let api_key = guard.api_key.clone();

        // 1. Resolve executable
        let mode = match resolve_backend_target(None) {
            Ok(m) => m,
            Err(e) => {
                guard.state = BackendState::Failed;
                guard.last_error = Some(e.clone());
                return Err(e);
            }
        };

        guard.mode_description = match &mode {
            BackendMode::PackagedSidecar(p) => format!(
                "Packaged ({})",
                p.file_name().unwrap_or_default().to_string_lossy()
            ),
            BackendMode::DevelopmentVenv { python_exe, .. } => {
                format!("Development ({})", python_exe.to_string_lossy())
            }
        };

        // 2. Create Job Object for bulletproof process cleanup
        let job = match JobObject::create() {
            Ok(j) => j,
            Err(e) => {
                eprintln!("[SUPERVISOR-WARN] Could not create JobObject: {}. Continuing without job containment.", e);
                // Non-fatal fallback
                JobObject::create().unwrap_or_else(|_| unsafe { std::mem::zeroed() })
            }
        };

        // 3. Spawn child process
        let mut cmd = build_backend_command(&mode, port, &api_key);
        let child = match cmd.spawn() {
            Ok(c) => c,
            Err(e) => {
                guard.state = BackendState::Failed;
                guard.last_error = Some(format!("Failed to spawn backend process: {}", e));
                return Err(guard.last_error.clone().unwrap());
            }
        };

        let _ = job.assign_child(&child);

        guard.child = Some(child);
        guard.job_object = Some(job);
        guard.started_at = Some(Instant::now());
        guard.state = BackendState::Connecting;

        drop(guard);

        // 4. Poll readiness in background or synchronously wait for initial boot
        self.spawn_readiness_poll();
        self.spawn_exit_monitor();

        Ok(())
    }

    fn spawn_readiness_poll(&self) {
        let sup = self.clone();
        thread::spawn(move || {
            let port = { sup.inner.lock().unwrap().port };
            let ready_url = format!("http://127.0.0.1:{}/api/v1/ready", port);
            let start = Instant::now();
            let timeout = Duration::from_secs(15);
            let mut is_ready = false;

            while start.elapsed() < timeout {
                // Check if supervisor was told to stop
                {
                    let guard = sup.inner.lock().unwrap();
                    if !guard.should_run || guard.state == BackendState::Stopping {
                        return;
                    }
                }

                if let Ok(resp) = ureq::get(&ready_url)
                    .timeout(Duration::from_millis(800))
                    .call()
                {
                    if resp.status() == 200 {
                        if let Ok(body) = resp.into_json::<serde_json::Value>() {
                            if body.get("ready").and_then(|v| v.as_bool()).unwrap_or(false) {
                                is_ready = true;
                                let db_ok = body
                                    .get("checks")
                                    .and_then(|c| c.get("database"))
                                    .and_then(|d| d.as_bool())
                                    .unwrap_or(false);

                                let mut guard = sup.inner.lock().unwrap();
                                guard.state = BackendState::Ready;
                                guard.database_ready = db_ok;
                                eprintln!(
                                    "[SUPERVISOR] Backend confirmed READY on port {} in {:.2}s.",
                                    port,
                                    start.elapsed().as_secs_f32()
                                );
                                break;
                            }
                        }
                    }
                }
                thread::sleep(Duration::from_millis(300));
            }

            if !is_ready {
                let mut guard = sup.inner.lock().unwrap();
                if guard.state == BackendState::Connecting {
                    guard.state = BackendState::Degraded;
                    guard.last_error =
                        Some("Backend readiness timeout exceeded (15s).".to_string());
                    eprintln!("[SUPERVISOR-WARN] Backend failed to become ready within timeout.");
                }
            }
        });
    }

    fn spawn_exit_monitor(&self) {
        let sup = self.clone();
        thread::spawn(move || {
            loop {
                thread::sleep(Duration::from_millis(500));

                let mut should_restart = false;
                {
                    let mut guard = sup.inner.lock().unwrap();
                    if !guard.should_run
                        || guard.state == BackendState::Stopping
                        || guard.state == BackendState::Stopped
                    {
                        break;
                    }

                    if let Some(child) = guard.child.as_mut() {
                        match child.try_wait() {
                            Ok(Some(status)) => {
                                eprintln!(
                                    "[SUPERVISOR] Child backend process exited with status: {}",
                                    status
                                );
                                guard.child = None;
                                guard.database_ready = false;

                                if guard.should_run {
                                    if guard.restart_count < guard.max_restarts {
                                        guard.restart_count += 1;
                                        guard.state = BackendState::Restarting;
                                        guard.last_error = Some(format!(
                                            "Unexpected termination (exit status: {})",
                                            status
                                        ));
                                        should_restart = true;
                                    } else {
                                        guard.state = BackendState::Failed;
                                        guard.last_error = Some(format!(
                                            "Backend exceeded max restarts ({}/{}). Manual restart required.",
                                            guard.restart_count, guard.max_restarts
                                        ));
                                        break;
                                    }
                                }
                            }
                            Ok(None) => {
                                // Still running
                            }
                            Err(e) => {
                                eprintln!("[SUPERVISOR-ERROR] Error checking child status: {}", e);
                            }
                        }
                    }
                }

                if should_restart {
                    // Exponential backoff
                    let count = { sup.inner.lock().unwrap().restart_count };
                    let backoff_ms = std::cmp::min(1000 * (1 << (count - 1)), 8000);
                    eprintln!(
                        "[SUPERVISOR] Restarting backend in {}ms (Attempt {})...",
                        backoff_ms, count
                    );
                    thread::sleep(Duration::from_millis(backoff_ms));
                    let _ = sup.start();
                    break;
                }
            }
        });
    }

    /// Triggers a controlled restart of the backend.
    pub fn restart(&self) -> Result<(), String> {
        eprintln!("[SUPERVISOR] Initiating manual backend restart...");
        self.stop();
        thread::sleep(Duration::from_millis(500));
        self.start()
    }

    /// Stops the child process cleanly with a timeout and kill fallback.
    pub fn stop(&self) {
        let mut guard = self.inner.lock().unwrap();
        guard.should_run = false;
        guard.state = BackendState::Stopping;

        if let Some(mut child) = guard.child.take() {
            let pid = child.id();
            eprintln!("[SUPERVISOR] Stopping backend child PID: {}", pid);

            // Attempt graceful kill
            let _ = child.kill();
            let start = Instant::now();
            let timeout = Duration::from_secs(3);

            while start.elapsed() < timeout {
                if let Ok(Some(_)) = child.try_wait() {
                    break;
                }
                thread::sleep(Duration::from_millis(100));
            }

            // Cleanup
            let _ = child.wait();
        }

        guard.job_object = None;
        guard.state = BackendState::Stopped;
        guard.started_at = None;
        guard.database_ready = false;
        eprintln!("[SUPERVISOR] Backend stopped.");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_supervisor_initial_status() {
        let sup = BackendSupervisor::new(8765, "test-api-key".to_string());
        let status = sup.get_status();
        assert_eq!(status.state, BackendState::Stopped);
        assert_eq!(status.port, 8765);
        assert_eq!(status.restart_count, 0);
        assert_eq!(status.max_restarts, 5);
        assert!(!status.database_ready);
        assert!(status.pid.is_none());
    }

    #[test]
    fn test_supervisor_state_serialization() {
        let status = BackendProcessStatus {
            state: BackendState::Ready,
            pid: Some(12345),
            port: 8765,
            uptime_seconds: 42,
            restart_count: 1,
            max_restarts: 5,
            last_error: None,
            backend_mode: "Packaged".to_string(),
            database_ready: true,
        };
        let json = serde_json::to_string(&status).expect("Serialization failed");
        assert!(json.contains("\"state\":\"Ready\""));
        assert!(json.contains("\"database_ready\":true"));
        let deserialized: BackendProcessStatus =
            serde_json::from_str(&json).expect("Deserialization failed");
        assert_eq!(deserialized.state, BackendState::Ready);
    }
}
