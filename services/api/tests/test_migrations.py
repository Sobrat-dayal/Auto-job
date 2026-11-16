"""Unit tests verifying database creation, foreign keys, and schema inspection."""

from pathlib import Path

import pytest
from sqlalchemy import inspect

from app.db.engine import create_engine_and_session, verify_database_connection
from app.db.migrations import init_database_schema


@pytest.mark.asyncio
async def test_database_creation_and_pragmas(tmp_path: Path):
    db_file = tmp_path / "test_autonom.db"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"

    engine, session_factory = create_engine_and_session(database_url=db_url)
    diag = await verify_database_connection(engine)

    assert diag["connected"] is True
    assert diag["foreign_keys_enabled"] is True
    assert diag["journal_mode"] == "WAL"

    await init_database_schema(engine)

    # Inspect created tables
    def inspect_tables(sync_conn):
        insp = inspect(sync_conn)
        return insp.get_table_names()

    async with engine.connect() as conn:
        tables = await conn.run_sync(inspect_tables)

    expected_tables = {
        "app_settings",
        "applicant_profiles",
        "verified_skills",
        "profile_evidence",
        "resume_versions",
        "job_sources",
        "job_listings",
        "job_matches",
        "applications",
        "application_attempts",
        "tasks",
        "task_events",
        "worker_runs",
        "agent_definitions",
        "artifacts",
        "credential_references",
        "audit_events",
    }

    assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"

    await engine.dispose()
