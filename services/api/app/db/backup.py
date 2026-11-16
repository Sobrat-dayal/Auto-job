"""Online database backup and safe verified restoration."""

import hashlib
import json
import logging
import shutil
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger("autonom.backup")


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def check_sqlite_file_integrity(db_file: Path) -> tuple[bool, str]:
    """Runs PRAGMA integrity_check directly on an isolated SQLite file."""
    try:
        conn = sqlite3.connect(f"file:{db_file.as_posix()}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        status = res[0] if res else "empty"
        return status == "ok", str(status)
    except Exception as exc:
        return False, str(exc)


async def create_database_backup(destination_dir: Path | None = None, reason: str = "manual") -> dict[str, Any]:
    """Creates a consistent online snapshot of the live SQLite database and generates a verified manifest."""
    settings.ensure_directories()
    dest_dir = destination_dir or settings.backups_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    backup_id = f"backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    backup_file = dest_dir / f"{backup_id}.db"
    manifest_file = dest_dir / f"{backup_id}.manifest.json"

    source_db = settings.database_path
    if not source_db.exists():
        raise FileNotFoundError(f"Source database not found at {source_db}")

    # Perform online SQLite backup
    src_conn = sqlite3.connect(source_db.as_posix())
    dst_conn = sqlite3.connect(backup_file.as_posix())
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()

    # Verify backup integrity
    integrity_ok, integrity_msg = check_sqlite_file_integrity(backup_file)
    checksum = compute_sha256(backup_file)
    file_size = backup_file.stat().st_size
    now_iso = datetime.now(UTC).isoformat()

    manifest = {
        "backup_id": backup_id,
        "filename": backup_file.name,
        "backup_file": str(backup_file),
        "created_at": now_iso,
        "timestamp_utc": now_iso,
        "reason": reason,
        "app_version": settings.app_version,
        "file_size_bytes": file_size,
        "size_bytes": file_size,
        "sha256_checksum": checksum,
        "sha256": checksum,
        "integrity_check_passed": integrity_ok,
        "integrity_message": integrity_msg,
    }

    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info(
        f"Created database backup {backup_id} (size: {file_size} bytes, reason: {reason}, integrity: {integrity_ok})"
    )

    # Prune old backups exceeding retention count
    prune_old_backups(dest_dir, retain_count=settings.backup_retention_count)

    return manifest


def prune_old_backups(backups_dir: Path, retain_count: int = 10) -> int:
    """Removes older backup files exceeding the configured retention count."""
    manifest_files = sorted(
        backups_dir.glob("*.manifest.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    if len(manifest_files) > retain_count:
        for excess in manifest_files[retain_count:]:
            db_file = excess.with_suffix("").with_suffix(".db")
            if db_file.exists():
                db_file.unlink()
            excess.unlink()
            removed += 1
            logger.info(f"Pruned old backup: {excess.name}")
    return removed


def list_backups(backups_dir: Path | None = None) -> list[dict[str, Any]]:
    """Returns a list of all available backups with their manifests, sorted newest first."""
    target_dir = backups_dir or settings.backups_dir
    if not target_dir.exists():
        return []

    manifest_files = sorted(
        target_dir.glob("*.manifest.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    backups = []
    for mf in manifest_files:
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            backups.append(data)
        except Exception:
            pass
    return backups


async def restore_database_backup(backup_file_path: Path | str, target_db_path: Path | None = None) -> dict[str, Any]:
    """Restores database from a verified backup, taking a safety snapshot of the live database first."""
    if isinstance(backup_file_path, str):
        p = Path(backup_file_path)
        if not p.exists():
            if (settings.backups_dir / backup_file_path).exists():
                p = settings.backups_dir / backup_file_path
            elif (settings.backups_dir / f"{backup_file_path}.db").exists():
                p = settings.backups_dir / f"{backup_file_path}.db"
        backup_file_path = p

    if not backup_file_path.exists():
        raise FileNotFoundError(f"Backup file not found at {backup_file_path}")

    # 1. Pre-restore integrity check on backup file
    integrity_ok, integrity_msg = check_sqlite_file_integrity(backup_file_path)
    if not integrity_ok:
        raise ValueError(f"Cannot restore corrupt backup file: {integrity_msg}")

    # 2. Check checksum against manifest if manifest exists
    manifest_path = backup_file_path.with_suffix(".manifest.json")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_sha = manifest.get("sha256_checksum")
        actual_sha = compute_sha256(backup_file_path)
        if expected_sha and expected_sha != actual_sha:
            raise ValueError(f"Checksum mismatch: expected {expected_sha}, got {actual_sha}")

    target_db = target_db_path or settings.database_path

    # 3. Take safety pre-restore backup if target DB currently exists
    safety_backup = None
    if target_db.exists():
        safety_id = f"pre_restore_safety_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        safety_path = target_db.parent / f"{safety_id}.bak"
        shutil.copy2(target_db, safety_path)
        safety_backup = str(safety_path)
        logger.info(f"Created pre-restore safety snapshot at {safety_path}")

    # 4. Perform restoration using SQLite backup API
    src_conn = sqlite3.connect(backup_file_path.as_posix())
    dst_conn = sqlite3.connect(target_db.as_posix())
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()

    # 5. Post-restore integrity verification
    post_ok, post_msg = check_sqlite_file_integrity(target_db)
    if not post_ok:
        # Rollback to safety backup if restoration produced an invalid file
        if safety_backup and Path(safety_backup).exists():
            shutil.copy2(safety_backup, target_db)
        raise RuntimeError(f"Post-restore integrity check failed: {post_msg}. Rolled back.")

    logger.info(f"Successfully restored database from {backup_file_path.name}")
    return {
        "restored": True,
        "success": True,
        "backup_source": backup_file_path.name,
        "target_database": target_db.name,
        "pre_restore_safety_backup": safety_backup,
        "safety_snapshot": safety_backup,
        "integrity_verified": post_ok,
        "timestamp": datetime.now(UTC).isoformat(),
    }
