# AUTONOM — Database Backup, Restoration & Disaster Recovery

## 1. Overview & Resilience Model

AUTONOM implements zero-downtime, consistent online database backups and safe, verified restorations directly within the desktop application. Because AUTONOM is a local-first system, protecting against workstation crashes, filesystem corruption, and accidental user actions is paramount.

### Core Capabilities

1. **Online Snapshot Generation**: Uses the native SQLite Online Backup API (`sqlite3.backup`) to create atomic, point-in-time snapshots while the database is actively servicing read and write queries.
2. **Cryptographic Manifest Verification**: Every backup snapshot is paired with an independent `.manifest.json` file recording timestamp, file size, reason, application version, and a SHA-256 checksum.
3. **Pre-Restore Safety Snapshot**: Before any backup is restored to the live database, an automated safety snapshot (`pre_restore_safety_*.bak`) is captured of the existing database.
4. **Isolated Integrity Verification**: Backups are verified with `PRAGMA integrity_check` in isolation before restoration begins.
5. **Post-Restore Verification & Atomic Rollback**: Following restoration, the live database is verified with `PRAGMA integrity_check`. If corruption is detected, the operation automatically rolls back to the pre-restore safety snapshot.
6. **Automatic Backup Retention Management**: Backups are automatically pruned, retaining the 10 most recent snapshots to prevent storage bloat.

---

## 2. Backup Manifest Specification

Every backup produces two paired files in `%LOCALAPPDATA%\AUTONOM\backups\`:

- `backup_{TIMESTAMP}_{UUID}.db`: The raw SQLite snapshot.
- `backup_{TIMESTAMP}_{UUID}.manifest.json`: Metadata manifest.

### Example Manifest (`.manifest.json`)

```json
{
  "backup_id": "backup_20261116_150341_9c4b20",
  "filename": "backup_20261116_150341_9c4b20.db",
  "backup_file": "C:\\Users\\...\\AppData\\Local\\AUTONOM\\backups\\backup_20261116_150341_9c4b20.db",
  "created_at": "2026-11-16T15:03:41.872659+00:00",
  "timestamp_utc": "2026-11-16T15:03:41.872659+00:00",
  "reason": "manual-cli",
  "app_version": "0.1.0",
  "file_size_bytes": 356352,
  "size_bytes": 356352,
  "sha256_checksum": "5c7b6424241dc5b0cfe1f9ba398eaebe8ce7f610933e606afad42a1b426ac36c",
  "sha256": "5c7b6424241dc5b0cfe1f9ba398eaebe8ce7f610933e606afad42a1b426ac36c",
  "integrity_check_passed": true,
  "integrity_message": "ok"
}
```

---

## 3. Verified Restoration Workflow

```
+-------------------------------------------------------------------+
|               User Requests Restore (UI or CLI)                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   Step 1: Pre-Restore Integrity                   |
|       - Verify backup file exists in %LOCALAPPDATA%\backups\      |
|       - Run PRAGMA integrity_check on backup file in isolation    |
|       - Verify SHA-256 checksum against .manifest.json            |
+-------------------------------------------------------------------+
                                  | Passed
                                  v
+-------------------------------------------------------------------+
|               Step 2: Capture Safety Pre-Restore Snapshot         |
|   - Copy live autonom.db -> pre_restore_safety_{TIMESTAMP}.bak   |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                Step 3: Online Restoration Execution               |
|            - Stream backup pages into live autonom.db             |
|                 using native SQLite backup API                    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                  Step 4: Post-Restore Verification                |
|       - Run PRAGMA integrity_check on live restored database      |
+-------------------------------------------------------------------+
            |                                         |
     Passed |                                  Failed |
            v                                         v
+------------------------+              +---------------------------+
| SUCCESS: Return Status |              | AUTOMATIC ROLLBACK        |
|  and Safety Reference  |              | Restore pre_restore_*.bak |
+------------------------+              | Raise RuntimeError        |
                                        +---------------------------+
```

---

## 4. Operational Playbooks

### Triggering a Manual Backup via CLI

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-backup.ps1 -Reason "pre-major-import"
```

### Listing Available Backups

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-restore.ps1
```

### Restoring from a Backup

Interactive confirmation prompt:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-restore.ps1 -BackupId "backup_20261116_150341_9c4b20"
```

Automated force restore:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-restore.ps1 -BackupId "backup_20261116_150341_9c4b20" -Force
```

### Performing Disaster Recovery from Safety Snapshot

If an unexpected operating system failure interrupted a restore operation:

```powershell
# Safety backups are stored directly in the database folder:
Copy-Item "%LOCALAPPDATA%\AUTONOM\database\pre_restore_safety_*.bak" "%LOCALAPPDATA%\AUTONOM\database\autonom.db" -Force
powershell -ExecutionPolicy Bypass -File scripts\db-verify.ps1
```
