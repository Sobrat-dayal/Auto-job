# AUTONOM — Storage Operations, Diagnostics & Troubleshooting Runbook

## 1. Quick Diagnostic Checklist

When investigating database or storage issues in AUTONOM:

1. **Check Storage Status via UI**:
   - Open AUTONOM Desktop App -> Click **Storage & Database** in the sidebar.
   - Inspect database size, WAL size, backup counts, free disk space, and integrity status.
2. **Run Integrity Check via PowerShell**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\db-verify.ps1
   ```
3. **Inspect Storage Status via CLI**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\db-status.ps1
   ```

---

## 2. Operational Scripts Reference

The `scripts/` directory provides native PowerShell scripts wrapping the backend CLI:

| Script                   | Purpose                                                     | Underlying Command                                     |
| :----------------------- | :---------------------------------------------------------- | :----------------------------------------------------- |
| `scripts/db-init.ps1`    | Initialize database schema and tables directly              | `python -m app.db.cli init`                            |
| `scripts/db-migrate.ps1` | Apply pending Alembic revisions up to `head`                | `python -m app.db.cli migrate`                         |
| `scripts/db-status.ps1`  | Query disk usage, WAL size, backups, and schema version     | `python -m app.db.cli status`                          |
| `scripts/db-verify.ps1`  | Run `PRAGMA integrity_check` and `PRAGMA foreign_key_check` | `python -m app.db.cli verify`                          |
| `scripts/db-backup.ps1`  | Create consistent online snapshot with SHA-256 manifest     | `python -m app.db.cli backup [--reason <text>]`        |
| `scripts/db-restore.ps1` | Restore database with safety snapshot and verification      | `python -m app.db.cli restore [<backup_id>] [--force]` |

---

## 3. Troubleshooting Common Issues

### Issue 1: `database is locked` Error

- **Root Cause**: An external process (e.g. SQLite GUI viewer or antivirus file scanner) opened `autonom.db` with an exclusive lock, or a long-running uncommitted write transaction occurred.
- **Resolution**:
  1. AUTONOM default busy timeout is configured to 10 seconds (`busy_timeout = 10000`), mitigating short lock contentions.
  2. Verify no third-party SQLite browser is holding an open lock on `%LOCALAPPDATA%\AUTONOM\database\autonom.db`.
  3. Ensure WAL mode is active (`PRAGMA journal_mode = WAL;`) by running `scripts\db-status.ps1`.

### Issue 2: WAL File Growing Abnormally Large (`autonom.db-wal` > 50MB)

- **Root Cause**: Checkpointing has been postponed due to continuous long-running read queries.
- **Resolution**:
  1. Restart the AUTONOM backend process (shutdown triggers a full passive checkpoint `PRAGMA wal_checkpoint(PASSIVE)`).
  2. Run `scripts\db-backup.ps1`. The backup operation synchronizes and checkpoints the database.

### Issue 3: Master Key / DPAPI Decryption Error

- **Symptoms**: `CryptUnprotectData failed: The parameter is incorrect` or `The key is not valid for use in specified state`.
- **Root Cause**: The `.vault.key` file was copied from a different Windows user profile or machine, or the Windows user password was reset without DPAPI recovery.
- **Resolution**:
  1. The vault master key is tied strictly to the Windows user context that generated it.
  2. If the user account was migrated, restore credentials using an authorized backup or re-enter integration API keys through the Settings UI.

### Issue 4: Corrupt Backup File Rejection

- **Symptoms**: `Cannot restore corrupt backup file` or `Checksum mismatch`.
- **Root Cause**: The backup file was modified or corrupted on disk.
- **Resolution**:
  1. AUTONOM's pre-restore validation protects the live database by refusing to restore corrupted snapshots.
  2. Choose the next most recent verified backup from `scripts\db-restore.ps1`.
