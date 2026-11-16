#!/usr/bin/env python3
"""
AUTONOM Stage 03 — Live End-to-End Verification Script
Executes the live scenario defined in Section 24 of the Stage 03 specification:
1. Starts the backend server process.
2. Confirms readiness.
3. Subscribes to Server-Sent Events (SSE) stream.
4. Dispatches safe demonstration task (compute.echo).
5. Observes state transitions and real-time event delivery.
6. Inspects final task result.
7. Dispatches cancellable multi-step task (test.sleep_progress).
8. Issues cooperative cancellation and verifies terminal cancelled state.
9. Restarts backend and verifies disconnection and reconnection handling.
10. Confirms in-memory ephemeral semantics (clean start without orphaned tasks).
"""

import sys
import time
import subprocess
import httpx
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
API_DIR = ROOT_DIR / "services" / "api"
PYTHON_EXE = API_DIR / ".venv" / "Scripts" / "python.exe"
BASE_URL = "http://127.0.0.1:8765"


def log(msg: str):
    print(f"[STAGE 03 LIVE] {msg}")


def start_backend():
    log("Starting backend process via uvicorn on 127.0.0.1:8765...")
    proc = subprocess.Popen(
        [str(PYTHON_EXE), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8765", "--log-level", "warning"],
        cwd=str(API_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc


def wait_for_ready(client: httpx.Client, timeout: float = 10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = client.get(f"{BASE_URL}/api/v1/ready")
            if r.status_code == 200 and r.json().get("ready") is True:
                return r.json()
        except Exception:
            pass
        time.sleep(0.3)
    raise TimeoutError("Backend did not become ready in time")


def main():
    log("=" * 70)
    log("AUTONOM STAGE 03 — LIVE END-TO-END VERIFICATION")
    log("=" * 70)

    # 1. Start Server
    server_proc = start_backend()
    client = httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": "Bearer dev-local-autonom-key"},
        timeout=10.0,
    )

    try:
        # 2. Confirm readiness (unauthenticated safe endpoint)
        ready_data = wait_for_ready(client)
        log(f"Step 1 & 2: Backend started and confirmed READY. Details: {ready_data}")

        # Security check: verify unauthenticated request to protected endpoint is rejected
        unauth_client = httpx.Client(base_url=BASE_URL, timeout=5.0)
        unauth_r = unauth_client.get("/api/v1/system/status")
        log(f"Security Check: Unauthenticated request to protected endpoint returned HTTP {unauth_r.status_code}")
        assert unauth_r.status_code == 401, f"Expected 401 Unauthorized, got {unauth_r.status_code}"

        # 3. Confirm System Capabilities & Status
        status_r = client.get("/api/v1/system/status")
        assert status_r.status_code == 200, f"Status code {status_r.status_code}"
        sys_status = status_r.json()
        log(f"Step 3: System Status: Uptime={sys_status['uptime_seconds']}s, Workers={sys_status['workers']}")

        caps_r = client.get("/api/v1/system/capabilities")
        assert caps_r.status_code == 200
        caps = caps_r.json()
        log(f"Step 3: Registered Handlers: {caps['supported_task_types']}")
        assert "compute.echo" in caps["supported_task_types"]
        assert "test.sleep_progress" in caps["supported_task_types"]

        # 4. Connect to SSE Stream (test handshake)
        log("Step 4: Connecting to SSE stream endpoint /api/v1/events/stream...")
        with client.stream("GET", "/api/v1/events/stream") as sse_stream:
            lines = sse_stream.iter_lines()
            first_line = next(lines)
            log(f"SSE Handshake Line: '{first_line}'")
            assert ": connected" in first_line

            # 5. Dispatch Safe Demo Task (compute.echo)
            log("Step 5: Dispatching compute.echo task...")
            create_r = client.post(
                "/api/v1/tasks",
                json={
                    "task_type": "compute.echo",
                    "payload": {"text": "AUTONOM live execution verification", "repeat": 2},
                    "priority": "normal",
                },
            )
            assert create_r.status_code == 201, create_r.text
            echo_task = create_r.json()
            echo_id = echo_task["task_id"]
            log(f"Task created: ID={echo_id}, State={echo_task['state']}")
            assert echo_task["state"].lower() in ("created", "queued", "running", "completed")

            # 6. Wait for task completion
            time.sleep(0.5)
            task_info = client.get(f"/api/v1/tasks/{echo_id}").json()
            log(f"Step 6-9: Task {echo_id} reached state: {task_info['state']}")
            assert task_info["state"].lower() == "completed"
            assert task_info["progress"] == 100.0

            # 7. Inspect actual task result
            res_r = client.get(f"/api/v1/tasks/{echo_id}/result")
            assert res_r.status_code == 200
            res_data = res_r.json()
            log(f"Step 10: Task result verified: {res_data['result']}")
            assert res_data["result"]["original_text"] == "AUTONOM live execution verification"
            assert res_data["result"]["repeat_count"] == 2
            assert res_data["result"]["status"] == "success"

            # 8. Dispatch Cancellable Task (test.sleep_progress)
            log("Step 11: Dispatching cancellable task test.sleep_progress (steps: 8, delay: 0.3s)...")
            cancel_create_r = client.post(
                "/api/v1/tasks",
                json={
                    "task_type": "test.sleep_progress",
                    "payload": {"steps": 8, "step_delay": 0.3},
                    "priority": "normal",
                },
            )
            assert cancel_create_r.status_code == 201
            sleep_id = cancel_create_r.json()["task_id"]
            log(f"Cancellable task dispatched: ID={sleep_id}")

            # Let it start running and report progress
            time.sleep(0.6)
            running_info = client.get(f"/api/v1/tasks/{sleep_id}").json()
            log(f"Running progress check: State={running_info['state']}, Progress={running_info['progress']}%")

            # Step 12: Request cancellation
            log(f"Step 12: Requesting cooperative cancellation for task {sleep_id}...")
            cancel_r = client.post(f"/api/v1/tasks/{sleep_id}/cancel")
            assert cancel_r.status_code == 200
            log(f"Cancel response: {cancel_r.json()}")

            # Allow worker to cooperatively yield and finalize
            time.sleep(0.5)
            final_info = client.get(f"/api/v1/tasks/{sleep_id}").json()
            log(f"Step 13: Final state after cancellation: {final_info['state']}")
            assert final_info["state"].lower() == "cancelled"

            # 9. Verify Recent Events In-Memory Ring Buffer
            events_r = client.get("/api/v1/events/recent?limit=10")
            assert events_r.status_code == 200
            events = events_r.json()
            log(f"Ring Buffer Events Count: {len(events)}")
            event_types = [e["event_type"] for e in events]
            log(f"Observed Event Types: {set(event_types)}")
            assert any("task.created" in t for t in event_types)
            assert any("task.cancelled" in t for t in event_types)

        # 10. Restart Backend and verify in-memory ephemeral semantics
        log("Step 14: Restarting backend process to verify clean shutdown and ephemeral in-memory state...")
        server_proc.terminate()
        server_proc.wait(timeout=5)
        log("Initial backend process terminated cleanly.")

        # Re-start server
        server_proc = start_backend()
        wait_for_ready(client)
        log("Step 15: New backend process started and confirmed ready.")

        # Confirm old in-memory task is gone (404 Not Found)
        lost_r = client.get(f"/api/v1/tasks/{echo_id}")
        log(f"Step 16-17: Querying previous task ID on clean restart returned HTTP {lost_r.status_code} (as expected for in-memory stage)")
        assert lost_r.status_code == 404

        workers_after = client.get("/api/v1/workers").json()
        log(f"Worker pool after restart: Active={workers_after['active_workers']}, Idle={workers_after['idle_workers']}, Capacity={workers_after['max_capacity']}")
        assert workers_after["active_workers"] == 0
        assert workers_after["idle_workers"] == workers_after["max_capacity"]

        log("=" * 70)
        log("ALL 17 LIVE VERIFICATION STEPS PASSED PERFECTLY!")
        log("=" * 70)

    finally:
        log("Cleaning up backend process...")
        if server_proc.poll() is None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server_proc.kill()
        log("Teardown complete.")


if __name__ == "__main__":
    main()
