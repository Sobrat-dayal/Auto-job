"""Repository for job sources, job listings, and job matches."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobListing, JobSource
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobListing]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_or_create_source(
        self,
        platform_name: str,
        source_url: str,
        source_type: str = "web",
    ) -> JobSource:
        result = await self.session.execute(select(JobSource).where(JobSource.source_url == source_url))
        source = result.scalar_one_or_none()
        if source:
            return source

        source = JobSource(
            platform_name=platform_name,
            source_url=source_url,
            source_type=source_type,
            enabled=True,
        )
        self.session.add(source)
        await self.session.flush()
        return source

    async def create_listing(
        self,
        source_id: str,
        external_id: str,
        company: str,
        title: str,
        application_url: str,
        location: str | None = None,
        employment_type: str | None = None,
        work_arrangement: str | None = None,
        salary_range: str | None = None,
        description: str | None = None,
        requirements: str | None = None,
    ) -> JobListing:
        # Check duplicate
        query = select(JobListing).where(
            JobListing.source_id == source_id,
            JobListing.external_id == external_id,
        )
        existing = (await self.session.execute(query)).scalar_one_or_none()
        if existing:
            return existing

        listing = JobListing(
            source_id=source_id,
            external_id=external_id,
            company=company,
            title=title,
            application_url=application_url,
            location=location,
            employment_type=employment_type,
            work_arrangement=work_arrangement,
            salary_range=salary_range,
            description=description,
            requirements=requirements,
            status="active",
        )
        self.session.add(listing)
        await self.session.flush()
        return listing

    async def list_listings(
        self,
        status: str | None = None,
        company: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobListing]:
        query = select(JobListing).order_by(JobListing.discovered_at.desc())
        if status:
            query = query.where(JobListing.status == status)
        if company:
            query = query.where(JobListing.company.ilike(f"%{company}%"))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
