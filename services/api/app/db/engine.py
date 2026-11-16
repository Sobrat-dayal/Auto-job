"""SQLAlchemy 2.x asynchronous database engine, connection event listener, and session factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_engine_and_session(
    database_url: str | None = None,
    echo: bool = False,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Creates a configured AsyncEngine with SQLite PRAGMAs and an async session factory."""
    settings.ensure_directories()
    url = database_url or settings.database_url

    engine = create_async_engine(
        url,
        echo=echo,
        connect_args={
            "timeout": max(5.0, settings.database_busy_timeout_ms / 1000.0),
            "check_same_thread": False,
        },
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        """Enforces foreign keys, WAL mode, normal synchronous, and busy timeout on every connection."""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute(f"PRAGMA busy_timeout = {settings.database_busy_timeout_ms};")
        finally:
            cursor.close()

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return engine, session_factory


# Default application engine and sessionmaker
engine, async_session_factory = create_engine_and_session()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields an AsyncSession with automatic commit on success and rollback on exception."""
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def verify_database_connection(test_engine: AsyncEngine | None = None) -> dict[str, Any]:
    """Executes a diagnostic query to verify SQLite connection and PRAGMA settings."""
    target_engine = test_engine or engine
    async with target_engine.connect() as conn:
        fk_result = await conn.execute(text("PRAGMA foreign_keys;"))
        fk_enabled = bool(fk_result.scalar())

        journal_result = await conn.execute(text("PRAGMA journal_mode;"))
        journal_mode = str(journal_result.scalar()).upper()

        sync_result = await conn.execute(text("PRAGMA synchronous;"))
        sync_mode = sync_result.scalar()

    return {
        "connected": True,
        "foreign_keys_enabled": fk_enabled,
        "journal_mode": journal_mode,
        "synchronous_level": sync_mode,
    }
