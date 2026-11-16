# AUTONOM — Database Migrations Guide

## 1. Migration Architecture & Philosophy

AUTONOM utilizes **Alembic** alongside SQLAlchemy for deterministic, version-controlled schema evolution. In an enterprise-grade desktop application operating on local SQLite databases across thousands of user workstations, migrations must adhere to strict principles:

1. **Non-Destructive Schema Evolution**: Migrations must never drop user data. Columns or tables being phased out are deprecated, marked nullable, and migrated through staged transitions.
2. **Forward-Only Production Policy**: While downgrade scripts are authored for development, production desktop releases only execute forward migrations (`alembic upgrade head`) during application startup.
3. **SQLite DDL Safety (`batch_op`)**: SQLite has limited native support for `ALTER TABLE` operations. All column additions, deletions, or type modifications must use Alembic's `batch_alter_table` mode to safely recreate tables behind the scenes while preserving table contents.
4. **Programmatic Execution**: Migrations can be executed both via the standard Alembic CLI and programmatically during backend initialization (`app/db/migrations.py`).

---

## 2. Directory Structure

```
services/api/
├── alembic.ini                  # Alembic runtime configuration
└── alembic/
    ├── env.py                   # Async SQLAlchemy migration execution context
    ├── script.py.mako           # Template for newly generated migration scripts
    └── versions/
        └── 001_initial_schema.py # Initial baseline revision (17 tables & indexes)
```

---

## 3. Configuration & `env.py`

`services/api/alembic/env.py` dynamically resolves the database URL from AUTONOM application settings (`app.core.config.settings.database_url`) and imports `Base.metadata` from `app.db.models`:

```python
# Extract metadata for autogenerate support
target_metadata = Base.metadata

def run_migrations_online() -> None:
    # Connects via synchronous SQLite driver for reliable DDL lock management during migration
    ...
```

---

## 4. Operational Commands & Scripts

### Applying Migrations via PowerShell

To apply all pending migrations up to the latest revision (`head`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-migrate.ps1
```

Or directly via the Python CLI:

```powershell
services\api\.venv\Scripts\python -m app.db.cli migrate
```

### Checking Migration & Schema Version

To inspect the current revision recorded in SQLite's `alembic_version` table:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\db-status.ps1
```

### Generating a New Migration Revision

When new SQLAlchemy models or columns are added:

```powershell
cd services\api
..\api\.venv\Scripts\alembic revision --autogenerate -m "add_search_indexes_to_jobs"
```

---

## 5. Migration Best Practices for AUTONOM

1. **Explicit Index Naming**: Always declare explicit constraint and index names (e.g. `ix_tasks_status`, `uq_job_listings_source_ext_id`) so SQLite batch alterations can cleanly recreate them.
2. **Default Values for Non-Nullable Columns**: Adding a `nullable=False` column to an existing table requires an explicit server default value in the migration.
3. **Pre-Migration Safety Snapshot**: In production, automated migrations trigger an online backup (`create_database_backup(reason="pre-migration")`) before executing DDL alterations. If a migration fails, the pre-migration snapshot can be restored immediately without data loss.
