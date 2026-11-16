"""Tests for SQLite database initialization, WAL mode, and schema integrity."""

import pytest
from autonom_backend.db.database import db_manager


@pytest.mark.asyncio
async def test_database_initialization():
    await db_manager.initialize()
    health = await db_manager.check_health()
    assert health["connected"] is True
    assert health["mode"].lower() == "wal"


@pytest.mark.asyncio
async def test_tables_and_seed_agents():
    await db_manager.initialize()
    async with db_manager.get_connection() as db:
        # Check tables exist
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('agents', 'tasks', 'jobs', 'applications', 'approvals', 'audit_logs', 'credentials');"
        )
        rows = await cursor.fetchall()
        table_names = {r["name"] for r in rows}
        expected_tables = {"agents", "tasks", "jobs", "applications", "approvals", "audit_logs", "credentials"}
        assert expected_tables.issubset(table_names)

        # Check default agents are seeded
        cursor_agents = await db.execute("SELECT id, name, role FROM agents ORDER BY id;")
        agents = await cursor_agents.fetchall()
        assert len(agents) >= 4
        agent_ids = [a["id"] for a in agents]
        assert "coordinator-01" in agent_ids
        assert "scout-01" in agent_ids
        assert "tailor-01" in agent_ids
        assert "submitter-01" in agent_ids
