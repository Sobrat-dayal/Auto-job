"""Programmatic database migration runner and schema initialization."""

import logging
from pathlib import Path

from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)


def get_alembic_config() -> Config:
    """Returns an Alembic Config instance pointing to the api directory's alembic.ini."""
    api_dir = Path(__file__).resolve().parent.parent.parent
    ini_path = api_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(api_dir / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    return cfg


async def init_database_schema(engine: AsyncEngine) -> None:
    """Creates all database tables directly using SQLAlchemy metadata (fast path for dev & tests)."""
    settings.ensure_directories()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Create FTS5 virtual table for memory search if supported by SQLite
        try:
            await conn.execute(
                text(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        memory_id UNINDEXED,
                        title,
                        content,
                        summary,
                        owner_scope,
                        scope_id,
                        memory_type,
                        tokenize = 'porter unicode61'
                    );
                    """
                )
            )
        except Exception as exc:
            logger.warning(f"Could not initialize memory_fts virtual table (FTS5 may be disabled): {exc}")
    logger.info("Database schema initialized successfully.")


async def get_current_schema_version(engine: AsyncEngine) -> str:
    """Queries the alembic_version table to retrieve current schema revision."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1;"))
            row = result.scalar()
            return str(row) if row else "unversioned"
    except Exception:
        # Table might not exist yet if created directly with create_all
        return "v0.4.0-initial"
