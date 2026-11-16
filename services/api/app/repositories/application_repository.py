"""Repository for job applications and execution attempts."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Application, ApplicationAttempt
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_application(
        self,
        job_id: str,
        profile_id: str,
        resume_version_id: str | None = None,
        notes: str | None = None,
    ) -> Application:
        # Check idempotency: 1 active application per job and profile
        existing = await self.session.execute(
            select(Application).where(
                Application.job_id == job_id,
                Application.profile_id == profile_id,
            )
        )
        app = existing.scalar_one_or_none()
        if app:
            return app

        app = Application(
            job_id=job_id,
            profile_id=profile_id,
            resume_version_id=resume_version_id,
            notes=notes,
            status="draft",
        )
        self.session.add(app)
        await self.session.flush()
        return app

    async def record_attempt(
        self,
        application_id: str,
        execution_status: str,
        idempotency_key: str,
        failure_category: str | None = None,
        error_summary: str | None = None,
        retry_eligible: bool = False,
    ) -> ApplicationAttempt:
        # Check if attempt already exists for idempotency key
        result = await self.session.execute(
            select(ApplicationAttempt).where(ApplicationAttempt.idempotency_key == idempotency_key)
        )
        existing_attempt = result.scalar_one_or_none()
        if existing_attempt:
            return existing_attempt

        attempt = ApplicationAttempt(
            application_id=application_id,
            execution_status=execution_status,
            idempotency_key=idempotency_key,
            failure_category=failure_category,
            error_summary=error_summary,
            retry_eligible=retry_eligible,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def list_applications(
        self,
        status: str | None = None,
        profile_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Application]:
        query = (
            select(Application)
            .options(selectinload(Application.job), selectinload(Application.attempts))
            .order_by(Application.updated_at.desc())
        )
        if status:
            query = query.where(Application.status == status)
        if profile_id:
            query = query.where(Application.profile_id == profile_id)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_application_by_id(self, application_id: str) -> Application | None:
        query = (
            select(Application)
            .options(selectinload(Application.job), selectinload(Application.attempts))
            .where(Application.id == application_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_applications(
        self,
        status: str | None = None,
        profile_id: str | None = None,
    ) -> int:
        query = select(func.count(Application.id))
        if status:
            query = query.where(Application.status == status)
        if profile_id:
            query = query.where(Application.profile_id == profile_id)
        result = await self.session.execute(query)
        return int(result.scalar() or 0)
