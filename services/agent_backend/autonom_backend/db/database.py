"""Database connection management and initialization for SQLite with WAL mode."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite

from autonom_backend.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._is_initialized = False

    async def initialize(self) -> None:
        """Initialize database with WAL mode and initial schema tables."""
        logger.info(f"Initializing database at: {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            # Pragmas for reliability and performance
            await db.execute("PRAGMA journal_mode = WAL;")
            await db.execute("PRAGMA synchronous = NORMAL;")
            await db.execute("PRAGMA foreign_keys = ON;")
            await db.commit()

            # Execute schema creation
            from autonom_backend.db.models import SCHEMA_STATEMENTS
            for statement in SCHEMA_STATEMENTS:
                await db.execute(statement)
            await db.commit()

            # Seed default agent identities if not present
            cursor = await db.execute("SELECT COUNT(*) FROM agents;")
            row = await cursor.fetchone()
            count = row[0] if row else 0
            if count == 0:
                from autonom_backend.db.models import DEFAULT_AGENTS
                for agent in DEFAULT_AGENTS:
                    await db.execute(
                        """
                        INSERT INTO agents (id, name, role, status, model, tasks_completed)
                        VALUES (?, ?, ?, ?, ?, 0);
                        """,
                        (agent["id"], agent["name"], agent["role"], agent["status"], agent["model"]),
                    )
                await db.commit()
                logger.info("Seeded initial default agents into database.")

        self._is_initialized = True
        logger.info("Database initialized successfully.")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Context manager for acquiring a database connection."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys = ON;")
            yield db

    async def check_health(self) -> dict:
        """Check database connectivity and journal mode."""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute("PRAGMA journal_mode;")
                row = await cursor.fetchone()
                journal_mode = row[0] if row else "unknown"
                return {
                    "connected": True,
                    "mode": journal_mode,
                    "path": str(self.db_path),
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "connected": False,
                "mode": "error",
                "path": str(self.db_path),
                "error": str(e),
            }


db_manager = DatabaseManager(str(settings.database_path))
