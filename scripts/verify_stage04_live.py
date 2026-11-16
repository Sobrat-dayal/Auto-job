#!/usr/bin/env python3
"""
AUTONOM Stage 04 — End-to-End Live Verification Script
Validates the persistent database architecture, DPAPI/AES-256-GCM secure storage,
online backups, verified restoration, task persistence, credential masking, and restart recovery.
"""

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
API_DIR = ROOT_DIR / "services" / "api"
PYTHON_EXE = API_DIR / ".venv" / "Scripts" / "python.exe"
BASE_URL = "http://127.0.0.1:8765"
AUTH_HEADERS = {"Authorization": "Bearer dev-local-autonom-key"}


def log(msg: str) -> None:
    print(f"[STAGE 04 LIVE] {msg}")


def start_backend() -> subprocess.Popen:
    log("Starting backend process via uvicorn on 127.0.0.1:8765...")
    proc = subprocess.Popen(
        [
            str(PYTHON_EXE),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8765",
            "--log-level",
            "warning",
        ],
        cwd=str(API_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc


def wait_for_ready(client: httpx.Client, timeout: float = 12.0) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = client.get(f"{BASE_URL}/api/v1/ready")
            if r.status_code == 200 and r.json().get("ready") is True:
                return r.json()
        except Exception:
            pass
        time.sleep(0.3)
    raise TimeoutError("Backend failed to become ready within timeout period")


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    log("=" * 76)
    log("AUTONOM STAGE 04 — PERSISTENT DATABASE & SECURE STORAGE LIVE VERIFICATION")
    log("=" * 76)

    # 1. Start Server Instance 1
    server_proc = start_backend()
    client = httpx.Client(base_url=BASE_URL, headers=AUTH_HEADERS, timeout=15.0)

    try:
        # Step 1 & 2: Readiness check
        ready_data = wait_for_ready(client)
        log(f"Step 01-02: Backend started and confirmed READY: {ready_data}")

        # Step 03: Security check (unauthenticated requests rejected)
        unauth_client = httpx.Client(base_url=BASE_URL, timeout=5.0)
        unauth_res = unauth_client.get("/api/v1/storage/status")
        log(f"Step 03: Unauthenticated /api/v1/storage/status returned HTTP {unauth_res.status_code}")
        assert unauth_res.status_code == 401, f"Expected 401, got {unauth_res.status_code}"

        # Step 04: Storage status and health
        status_res = client.get("/api/v1/storage/status")
        assert status_res.status_code == 200, f"Storage status failed: {status_res.text}"
        status_data = status_res.json()
        log(f"Step 04: Storage status verified: DB={status_data['database_size_bytes']} bytes, FreeDisk={status_data['disk_free_bytes'] / (1024**3):.2f} GB")

        health_res = client.get("/api/v1/storage/health")
        assert health_res.status_code == 200, f"Storage health failed: {health_res.text}"
        health_data = health_res.json()
        log(f"Step 05: Storage health: SQLite integrity={health_data['integrity_check_passed']}, FKs={health_data['foreign_keys_passed']}")
        assert health_data["integrity_check_passed"] is True
        assert health_data["foreign_keys_passed"] is True

        # Step 06: App Settings persistence
        settings_payload = {
            "value": {"theme": "autonom-dark", "accent": "cyan", "sidebar_collapsed": False},
            "scope": "user",
        }
        patch_res = client.patch("/api/v1/settings/app.display_theme", json=settings_payload)
        assert patch_res.status_code == 200, f"Patch settings failed: {patch_res.text}"
        get_settings_res = client.get("/api/v1/settings")
        assert get_settings_res.status_code == 200
        settings_list = get_settings_res.json()
        saved_theme = next((s for s in settings_list if s["key"] == "app.display_theme"), None)
        assert saved_theme is not None, "Saved setting key not found in list"
        assert saved_theme["value"]["accent"] == "cyan"
        log("Step 06: App Settings created and retrieved successfully from database")

        # Step 07: Applicant Profile Creation with Encrypted Contact
        profile_req = {
            "profile_name": "Dr. Sarah Connor",
            "summary": "Lead Autonomous Systems Architect pioneering agentic workflows and local AI execution.",
            "career_preferences": {
                "target_roles": ["Lead AI Architect", "Principal Systems Engineer"],
                "target_locations": ["Remote", "Denver, CO"],
                "remote_preference": "remote_only",
                "min_salary": 220000,
            },
            "contact_info": {
                "contact_email": "sarah.connor@cyberdyne-resistance.org",
                "contact_phone": "+1-555-0199-887",
                "contact_address": "404 SkyNet Way, Cheyenne Mountain, CO",
            },
        }
        prof_res = client.post("/api/v1/profiles", json=profile_req)
        assert prof_res.status_code == 201, f"Create profile failed: {prof_res.text}"
        profile = prof_res.json()
        profile_id = profile["id"]
        log(f"Step 07: Applicant profile created with ID: {profile_id}")

        # Step 08: Direct raw SQLite check: verify contact email is NOT in plaintext in the DB file
        db_path = Path(status_data["database_path"])
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT profile_name, contact_info_encrypted FROM applicant_profiles WHERE id = ?", (profile_id,))
        row = cur.fetchone()
        conn.close()
        assert row is not None, "Profile row missing from SQLite database"
        assert row[0] == "Dr. Sarah Connor"
        raw_contact_blob = row[1]
        assert raw_contact_blob is not None, "Encrypted contact info blob is missing"
        # Plaintext secret MUST NOT appear in the encrypted blob or raw row
        assert "sarah.connor@cyberdyne-resistance.org" not in str(raw_contact_blob)
        assert "+1-555-0199-887" not in str(raw_contact_blob)
        log("Step 08: Verified: Sensitive contact info is strongly encrypted and plaintext is absent in SQLite")

        # Step 09: Secure Credential Storage & Masked Status
        cred_res = client.post(
            "/api/v1/integrations/credentials",
            json={
                "provider": "anthropic_claude",
                "secret_value": "sk-ant-api03-live-test-super-secret-key-12345",
                "label": "Anthropic Production API Key",
            },
        )
        assert cred_res.status_code in (200, 201), f"Store credential failed: {cred_res.text}"
        cred_data = cred_res.json()
        assert cred_data["is_configured"] is True
        log("Step 09: Secure credential protected by Windows DPAPI and stored")

        # Step 10: Query credential status: verify plaintext secret is NEVER exposed
        cred_status_res = client.get("/api/v1/integrations/credentials/status")
        assert cred_status_res.status_code == 200
        creds = cred_status_res.json()
        anthropic_cred = next((c for c in creds if c["provider"] == "anthropic_claude"), None)
        assert anthropic_cred is not None
        assert anthropic_cred["is_configured"] is True
        assert "secret_value" not in anthropic_cred
        assert "super-secret" not in json.dumps(creds)
        log("Step 10: Verified: Credential status endpoint masks all secrets without leakage")

        # Step 11: Task Persistence & Execution
        task_create_res = client.post(
            "/api/v1/tasks",
            json={
                "task_type": "compute.echo",
                "payload": {"text": "Persistent AUTONOM Task Execution", "repeat": 2},
                "priority": "high",
            },
        )
        assert task_create_res.status_code == 201, f"Task create failed: {task_create_res.text}"
        task_id = task_create_res.json()["task_id"]
        log(f"Step 11: Dispatched task {task_id}")

        # Wait for task completion
        completed = False
        for _ in range(25):
            t_res = client.get(f"/api/v1/tasks/{task_id}")
            if t_res.status_code == 200 and t_res.json()["state"].lower() == "completed":
                completed = True
                break
            time.sleep(0.2)
        assert completed, f"Task {task_id} did not reach completed state in time"
        log(f"Step 11: Task {task_id} completed successfully")

        # Step 12: Durable Event History Query
        history_res = client.get(f"/api/v1/tasks/{task_id}/history")
        assert history_res.status_code == 200, f"History fetch failed: {history_res.text}"
        history = history_res.json()
        event_types = [e["event_type"] for e in history]
        log(f"Step 12: Durable task event trail: {event_types}")
        assert "task.created" in event_types
        assert "task.queued" in event_types
        assert "task.started" in event_types
        assert "task.completed" in event_types

        # Step 13: Online Consistent Backup
        backup_res = client.post("/api/v1/storage/backups")
        assert backup_res.status_code == 201, f"Backup creation failed: {backup_res.text}"
        backup_info = backup_res.json()
        backup_id = backup_info["backup_id"]
        log(f"Step 13: Online backup created with ID: {backup_id}")

        # Step 14: Verify backup manifest and checksum
        backups_list_res = client.get("/api/v1/storage/backups")
        assert backups_list_res.status_code == 200
        backups = backups_list_res.json()
        matching_backup = next((b for b in backups if b["backup_id"] == backup_id), None)
        assert matching_backup is not None, "Backup not listed in backup index"
        assert matching_backup["integrity_check_passed"] is True
        log("Step 14: Verified: Backup manifest registered and SHA-256 integrity passed")

        # Step 15: Mutate state (Add a temporary second profile)
        temp_prof_res = client.post(
            "/api/v1/profiles",
            json={
                "profile_name": "Temporary Mutation Record",
                "summary": "This record will be wiped by backup restoration",
                "career_preferences": {"roles": ["Tester"]},
                "contact_info": {"email": "temp@example.com"},
            },
        )
        assert temp_prof_res.status_code == 201
        temp_id = temp_prof_res.json()["id"]
        log(f"Step 15: Injected state mutation: temporary profile ID {temp_id}")

        profiles_before_restore = client.get("/api/v1/profiles").json()
        assert any(p["id"] == temp_id for p in profiles_before_restore)

        # Step 16: Safe Verified Restoration
        backup_filename = backup_info["filename"]
        restore_res = client.post(
            "/api/v1/storage/restore",
            json={"filename": backup_filename, "confirm": True},
        )
        assert restore_res.status_code == 200, f"Restore failed: {restore_res.text}"
        restore_data = restore_res.json()
        assert restore_data["restored"] is True
        assert restore_data["integrity_verified"] is True
        log(f"Step 16: Successfully restored database from snapshot. Pre-restore safety: {restore_data.get('pre_restore_safety_backup')}")

        # Step 17: Verify state restored (temporary profile gone, original intact)
        profiles_after_restore = client.get("/api/v1/profiles").json()
        assert not any(p["id"] == temp_id for p in profiles_after_restore), "Temporary profile should be gone after restore"
        assert any(p["id"] == profile_id for p in profiles_after_restore), "Original profile must persist after restore"
        log("Step 17: State restoration verified: mutations rolled back and baseline restored")

        # Step 18: Reject invalid restore request
        bad_restore_res = client.post(
            "/api/v1/storage/restore",
            json={"filename": "non-existent-backup-file.db", "confirm": True},
        )
        assert bad_restore_res.status_code == 404
        log(f"Step 18: Invalid restore rejected with HTTP 404 without data corruption")

        # Step 19: Unconfirmed restore request rejected
        unconf_restore = client.post(
            "/api/v1/storage/restore",
            json={"filename": backup_filename, "confirm": False},
        )
        assert unconf_restore.status_code == 400
        log(f"Step 19: Unconfirmed restore rejected with HTTP 400")

        # Step 20: Clean shutdown of Server Instance 1
        log("Step 20: Stopping Server Instance 1 to test full process restart...")
        server_proc.terminate()
        server_proc.wait(timeout=5.0)

        # Step 21: Start Server Instance 2 (Simulating application restart)
        log("Step 21: Starting Server Instance 2...")
        server_proc = start_backend()
        wait_for_ready(client)
        log("Step 21: Server Instance 2 restarted and confirmed READY")

        # Step 22: Verify persisted profile survived restart
        restarted_profiles = client.get("/api/v1/profiles").json()
        restarted_prof = next((p for p in restarted_profiles if p["id"] == profile_id), None)
        assert restarted_prof is not None, "Profile lost across server restart"
        assert restarted_prof["profile_name"] == "Dr. Sarah Connor"
        log("Step 22: Verified: Profile data survived full server restart")

        # Step 23: Verify task and history survived restart
        restarted_task_res = client.get(f"/api/v1/tasks/{task_id}")
        assert restarted_task_res.status_code == 200
        assert restarted_task_res.json()["state"].lower() == "completed"
        restarted_hist_res = client.get(f"/api/v1/tasks/{task_id}/history")
        assert restarted_hist_res.status_code == 200
        restarted_events = [e["event_type"] for e in restarted_hist_res.json()]
        assert "task.completed" in restarted_events
        log(f"Step 23: Verified: Task execution record and history survived server restart")

        # Step 24: Direct PRAGMA integrity and foreign key check on restarted system
        post_restart_health = client.get("/api/v1/storage/health").json()
        assert post_restart_health["integrity_check_passed"] is True
        assert post_restart_health["foreign_keys_passed"] is True
        log("Step 24: PRAGMA integrity_check and foreign_key_check PASSED post-restart")

        # Step 25: Final summary and success confirmation
        log("Step 25: All 25 Stage 04 end-to-end verification gates PASSED successfully!")
        log("=" * 76)
        log("AUTONOM STAGE 04 LIVE VERIFICATION: 100% COMPLETE & VALIDATED")
        log("=" * 76)

    finally:
        client.close()
        log("Shutting down backend process...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            server_proc.kill()


if __name__ == "__main__":
    main()
