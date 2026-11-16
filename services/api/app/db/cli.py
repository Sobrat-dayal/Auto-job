"""Command line interface for AUTONOM database operations: init, migrate, status, backup, verify, restore."""

import argparse
import asyncio
import sys

from alembic import command
from app.core.config import settings
from app.db.backup import create_database_backup, list_backups, restore_database_backup
from app.db.engine import engine
from app.db.maintenance import get_storage_status, verify_database_integrity
from app.db.migrations import get_alembic_config, get_current_schema_version, init_database_schema


async def cmd_init(args: argparse.Namespace) -> int:
    print(f"[AUTONOM-DB] Initializing database schema at {settings.database_path}...")
    await init_database_schema(engine)
    version = await get_current_schema_version(engine)
    print(f"[AUTONOM-DB] SUCCESS: Database initialized. Schema version: {version}")
    return 0


async def cmd_migrate(args: argparse.Namespace) -> int:
    print("[AUTONOM-DB] Running Alembic database migrations...")
    cfg = get_alembic_config()
    try:
        command.upgrade(cfg, "head")
        version = await get_current_schema_version(engine)
        print(f"[AUTONOM-DB] SUCCESS: Migrations applied. Current revision: {version}")
        return 0
    except Exception as exc:
        print(f"[AUTONOM-DB] ERROR: Migration failed: {exc}", file=sys.stderr)
        return 1


async def cmd_status(args: argparse.Namespace) -> int:
    print("[AUTONOM-DB] Fetching storage and database status...")
    status = await get_storage_status()
    version = await get_current_schema_version(engine)
    print(f"  Database Path:        {status['database_path']}")
    print(
        f"  Database Size:        {status['database_size_bytes']} bytes ({status['database_size_bytes'] / (1024 * 1024):.2f} MB)"
    )
    print(f"  WAL Size:             {status['wal_size_bytes']} bytes")
    print(f"  Artifacts Size:       {status['artifacts_size_bytes']} bytes")
    print(f"  Backups Total Size:   {status['backups_size_bytes']} bytes ({status['total_backups_count']} backups)")
    print(f"  Disk Free Space:      {status['disk_free_bytes'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"  Schema Revision:      {version}")
    return 0


async def cmd_verify(args: argparse.Namespace) -> int:
    print("[AUTONOM-DB] Running database integrity and foreign key checks...")
    result = await verify_database_integrity(engine)
    if result["integrity_check_passed"] and result["foreign_keys_passed"]:
        print("[AUTONOM-DB] SUCCESS: Integrity check PASSED. Foreign keys PASSED.")
        return 0
    else:
        print("[AUTONOM-DB] FAILURE: Integrity issues detected!", file=sys.stderr)
        if not result["integrity_check_passed"]:
            print(f"  Integrity details: {result['integrity_details']}", file=sys.stderr)
        if not result["foreign_keys_passed"]:
            print(f"  Foreign key violations: {result['foreign_key_violations']}", file=sys.stderr)
        return 1


async def cmd_backup(args: argparse.Namespace) -> int:
    reason = args.reason or "manual-cli"
    print(f"[AUTONOM-DB] Creating online backup (reason: {reason})...")
    manifest = await create_database_backup(reason=reason)
    print("[AUTONOM-DB] SUCCESS: Backup created successfully.")
    print(f"  Backup ID:     {manifest['backup_id']}")
    print(f"  File:          {manifest['backup_file']}")
    print(f"  Size:          {manifest['size_bytes']} bytes")
    print(f"  SHA-256:       {manifest['sha256']}")
    print(f"  Timestamp:     {manifest['timestamp_utc']}")
    return 0


async def cmd_restore(args: argparse.Namespace) -> int:
    backup_id = args.backup_id
    if not backup_id:
        print("[AUTONOM-DB] ERROR: backup_id is required. Available backups:", file=sys.stderr)
        for b in list_backups():
            ts = b.get("timestamp_utc") or b.get("created_at") or "unknown"
            print(f"  - {b['backup_id']} ({ts}) - {b.get('reason', '')}")
        return 1

    if not args.force:
        print(f"[AUTONOM-DB] WARNING: Restoring backup '{backup_id}' will replace the current database!")
        confirm = input("Type 'RESTORE' to proceed: ")
        if confirm.strip() != "RESTORE":
            print("[AUTONOM-DB] Restore cancelled by user.")
            return 1

    print(f"[AUTONOM-DB] Restoring backup '{backup_id}' with safety snapshot and integrity checks...")
    res = await restore_database_backup(backup_id)
    if res.get("success") or res.get("restored"):
        print(f"[AUTONOM-DB] SUCCESS: Restored backup '{backup_id}'.")
        print(f"  Safety Snapshot: {res.get('safety_snapshot') or res.get('pre_restore_safety_backup')}")
        return 0
    else:
        print(f"[AUTONOM-DB] ERROR: Restore failed: {res.get('error')}", file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="AUTONOM Database CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize database schema directly")
    p_init.set_defaults(func=cmd_init)

    # migrate
    p_mig = subparsers.add_parser("migrate", help="Run Alembic migrations to head")
    p_mig.set_defaults(func=cmd_migrate)

    # status
    p_stat = subparsers.add_parser("status", help="Show database & storage status")
    p_stat.set_defaults(func=cmd_status)

    # verify
    p_ver = subparsers.add_parser("verify", help="Run SQLite integrity & foreign key checks")
    p_ver.set_defaults(func=cmd_verify)

    # backup
    p_bak = subparsers.add_parser("backup", help="Create an online verified backup")
    p_bak.add_argument("--reason", default="cli-manual", help="Reason for backup")
    p_bak.set_defaults(func=cmd_backup)

    # restore
    p_res = subparsers.add_parser("restore", help="Restore database from a backup")
    p_res.add_argument("backup_id", nargs="?", help="ID of backup to restore")
    p_res.add_argument("--force", action="store_true", help="Bypass interactive confirmation")
    p_res.set_defaults(func=cmd_restore)

    parsed = parser.parse_args()
    code = asyncio.run(parsed.func(parsed))
    sys.exit(code)


if __name__ == "__main__":
    main()
