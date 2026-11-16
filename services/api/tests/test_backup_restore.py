"""Unit tests for online database backup, integrity verification, and safe restoration."""

import json
from pathlib import Path

import pytest
from sqlalchemy import text

from app.core.config import settings
from app.db.backup import (
    create_database_backup,
    list_backups,
    restore_database_backup,
)
from app.db.engine import create_engine_and_session
from app.db.maintenance import verify_database_integrity
from app.db.migrations import init_database_schema


@pytest.mark.asyncio
async def test_backup_and_restore_cycle(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "appdata"
    monkeypatch.setattr(settings, "data_dir", data_dir)
    settings.ensure_directories()

    # 1. Initialize DB with test table and row
    engine, session_factory = create_engine_and_session()
    await init_database_schema(engine)

    async with session_factory() as session:
        await session.execute(
            text(
                "INSERT INTO app_settings (key, value_json, schema_version, updated_at, scope) VALUES (:k, :v, 1, CURRENT_TIMESTAMP, 'system')"
            ),
            {"k": "backup_test_key", "v": json.dumps({"value": 42})},
        )
        await session.commit()
    await engine.dispose()

    # 2. Create online backup
    manifest = await create_database_backup()
    assert manifest["integrity_check_passed"] is True
    assert Path(settings.backups_dir / manifest["filename"]).exists()

    backups = list_backups()
    assert len(backups) == 1
    assert backups[0]["backup_id"] == manifest["backup_id"]

    # 3. Modify live database
    engine2, session_factory2 = create_engine_and_session()
    async with session_factory2() as session:
        await session.execute(
            text("UPDATE app_settings SET value_json = :v WHERE key = 'backup_test_key'"),
            {"v": json.dumps({"value": 999})},
        )
        await session.commit()
    await engine2.dispose()

    # Verify live DB has updated value 999
    engine3, session_factory3 = create_engine_and_session()
    async with session_factory3() as session:
        res = await session.execute(text("SELECT value_json FROM app_settings WHERE key = 'backup_test_key'"))
        assert json.loads(res.scalar())["value"] == 999
    await engine3.dispose()

    # 4. Restore from backup
    backup_file = settings.backups_dir / manifest["filename"]
    restore_res = await restore_database_backup(backup_file)
    assert restore_res["restored"] is True
    assert restore_res["integrity_verified"] is True

    # 5. Verify restored database has original value 42
    engine4, session_factory4 = create_engine_and_session()
    async with session_factory4() as session:
        res = await session.execute(text("SELECT value_json FROM app_settings WHERE key = 'backup_test_key'"))
        assert json.loads(res.scalar())["value"] == 42

    # Integrity verification
    integ = await verify_database_integrity(engine4)
    assert integ["integrity_check_passed"] is True
    assert integ["foreign_keys_passed"] is True
    await engine4.dispose()


@pytest.mark.asyncio
async def test_corrupt_backup_rejected(tmp_path: Path):
    corrupt_file = tmp_path / "corrupt.db"
    corrupt_file.write_bytes(b"NOT_A_VALID_SQLITE_DATABASE_GARBAGE")

    target_db = tmp_path / "target.db"
    target_db.write_bytes(b"ORIGINAL_DATA")

    with pytest.raises(ValueError) as exc:
        await restore_database_backup(corrupt_file, target_db_path=target_db)

    assert "Cannot restore corrupt backup file" in str(exc.value)
    # Ensure original database was untouched
    assert target_db.read_bytes() == b"ORIGINAL_DATA"
