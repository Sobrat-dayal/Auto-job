"""Database maintenance, integrity verification, storage metrics, and cleanup."""

import logging
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db.backup import list_backups
from app.db.engine import engine

logger = logging.getLogger("autonom.maintenance")


async def verify_database_integrity(target_engine: AsyncEngine | None = None) -> dict[str, Any]:
    """Executes SQLite PRAGMA integrity_check and foreign_key_check."""
    eng = target_engine or engine
    async with eng.connect() as conn:
        # Integrity check
        ic_res = await conn.execute(text("PRAGMA integrity_check;"))
        ic_rows = [str(r[0]) for r in ic_res.fetchall()]
        integrity_ok = len(ic_rows) == 1 and ic_rows[0].lower() == "ok"

        # Foreign key check
        fk_res = await conn.execute(text("PRAGMA foreign_key_check;"))
        fk_violations = [dict(r._mapping) for r in fk_res.fetchall()]
        foreign_keys_ok = len(fk_violations) == 0

    return {
        "integrity_check_passed": integrity_ok,
        "integrity_details": ic_rows,
        "foreign_keys_passed": foreign_keys_ok,
        "foreign_key_violations": fk_violations,
    }


def get_directory_size(path: Path) -> int:
    """Computes total size of files in a directory in bytes."""
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


async def get_storage_status() -> dict[str, Any]:
    """Produces storage utilization metrics including database size, WAL size, and backup counts."""
    db_file = settings.database_path
    wal_file = settings.database_dir / "autonom.db-wal"
    shm_file = settings.database_dir / "autonom.db-shm"

    db_size = db_file.stat().st_size if db_file.exists() else 0
    wal_size = wal_file.stat().st_size if wal_file.exists() else 0
    shm_size = shm_file.stat().st_size if shm_file.exists() else 0

    artifacts_size = get_directory_size(settings.artifacts_dir)
    backups_size = get_directory_size(settings.backups_dir)
    backups = list_backups()

    # Free disk space on storage drive
    free_bytes = 0
    total_bytes = 0
    try:
        usage = shutil.disk_usage(settings.data_dir)
        free_bytes = usage.free
        total_bytes = usage.total
    except Exception:
        pass

    return {
        "database_path": str(db_file),
        "database_exists": db_file.exists(),
        "database_size_bytes": db_size,
        "wal_size_bytes": wal_size,
        "shm_size_bytes": shm_size,
        "artifacts_size_bytes": artifacts_size,
        "backups_size_bytes": backups_size,
        "total_backups_count": len(backups),
        "disk_free_bytes": free_bytes,
        "disk_total_bytes": total_bytes,
        "latest_backup": backups[0] if backups else None,
    }


def cleanup_expired_data(max_cache_age_hours: int = 48) -> dict[str, int]:
    """Cleans temporary cache files without touching permanent user records or active tasks."""
    cleaned_cache_files = 0
    cache_dir = settings.cache_dir
    if cache_dir.exists():
        for f in cache_dir.glob("*"):
            if f.is_file():
                try:
                    f.unlink()
                    cleaned_cache_files += 1
                except Exception:
                    pass

    return {
        "cache_files_removed": cleaned_cache_files,
    }
