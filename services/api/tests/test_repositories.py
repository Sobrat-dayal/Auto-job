"""Unit tests for Stage 04 repository layer operations and encryption."""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import create_engine_and_session
from app.db.migrations import init_database_schema
from app.repositories import (
    ApplicationRepository,
    CredentialRepository,
    JobRepository,
    ProfileRepository,
    SettingsRepository,
    TaskEventRepository,
    TaskRepository,
)
from app.schemas.tasks import TaskState


@pytest.fixture
async def db_session(tmp_path: Path):
    db_file = tmp_path / "test_repo.db"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    engine, session_factory = create_engine_and_session(database_url=db_url)
    await init_database_schema(engine)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_settings_repository(db_session: AsyncSession):
    repo = SettingsRepository(db_session)
    await repo.set_setting("theme", {"mode": "dark", "accent": "blue"})
    await db_session.commit()

    val = await repo.get_setting("theme")
    assert val == {"mode": "dark", "accent": "blue"}


@pytest.mark.asyncio
async def test_profile_repository_encrypted_contact(db_session: AsyncSession):
    repo = ProfileRepository(db_session)
    profile = await repo.create_profile(
        profile_name="Senior Engineer",
        summary="Experienced distributed systems developer",
        contact_info={"email": "dev@autonom.local", "phone": "+1-555-0199"},
    )
    await db_session.commit()

    assert profile.contact_info_encrypted is not None
    assert "dev@autonom.local" not in profile.contact_info_encrypted

    fetched = await repo.get_profile(profile.id)
    assert fetched is not None
    assert fetched["contact_info"]["email"] == "dev@autonom.local"
    assert fetched["contact_info"]["phone"] == "+1-555-0199"


@pytest.mark.asyncio
async def test_job_and_application_repository(db_session: AsyncSession):
    job_repo = JobRepository(db_session)
    app_repo = ApplicationRepository(db_session)

    source = await job_repo.get_or_create_source("greenhouse", "https://boards.greenhouse.io/autonom")
    listing = await job_repo.create_listing(
        source_id=source.id,
        external_id="gh-12345",
        company="AUTONOM Corp",
        title="AI Engineer",
        application_url="https://boards.greenhouse.io/autonom/jobs/12345",
    )
    await db_session.commit()

    # Verify duplicate creation returns existing listing
    dup_listing = await job_repo.create_listing(
        source_id=source.id,
        external_id="gh-12345",
        company="AUTONOM Corp",
        title="AI Engineer",
        application_url="https://boards.greenhouse.io/autonom/jobs/12345",
    )
    assert dup_listing.id == listing.id

    # Create application and record attempt
    profile_repo = ProfileRepository(db_session)
    profile = await profile_repo.create_profile("Candidate Profile")
    await db_session.commit()

    app = await app_repo.create_application(listing.id, profile.id)
    attempt = await app_repo.record_attempt(app.id, "submitted", "attempt-key-999")
    await db_session.commit()

    assert attempt.idempotency_key == "attempt-key-999"


@pytest.mark.asyncio
async def test_task_repository_and_reconciliation(db_session: AsyncSession):
    task_repo = TaskRepository(db_session)
    event_repo = TaskEventRepository(db_session)

    task = await task_repo.create_task(
        task_id="task-persistent-01",
        task_type="compute.echo",
        payload={"text": "hello"},
    )
    assert task.status == TaskState.QUEUED.value

    await task_repo.update_task_state(task.id, TaskState.RUNNING.value, progress=25.0)
    await event_repo.record_event(task.id, "task.progress", state_transition="Queued->Running")
    await db_session.commit()

    # Test startup reconciliation on interrupted task
    interrupted = await task_repo.reconcile_interrupted_tasks()
    await db_session.commit()

    assert len(interrupted) == 1
    assert interrupted[0].id == "task-persistent-01"
    assert interrupted[0].status == TaskState.FAILED.value
    assert "INTERRUPTED" in interrupted[0].progress_message


@pytest.mark.asyncio
async def test_credential_repository(db_session: AsyncSession):
    cred_repo = CredentialRepository(db_session)
    await cred_repo.store_credential(
        provider="anthropic",
        credential_type="api_key",
        secret_value="sk-ant-api03-secret-value-12345",
    )
    await db_session.commit()

    # Secret retrieval
    secret = await cred_repo.get_secret("anthropic")
    assert secret == "sk-ant-api03-secret-value-12345"

    # Status listing must not expose secret
    statuses = await cred_repo.list_credential_status()
    assert len(statuses) == 1
    assert statuses[0]["provider"] == "anthropic"
    assert "secret" not in statuses[0]
    assert "encrypted_blob" not in statuses[0]
