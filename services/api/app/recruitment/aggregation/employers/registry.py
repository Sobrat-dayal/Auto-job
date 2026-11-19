"""Canonical Employer Registry and Database Repository (Stage 27)."""

from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import (
    CanonicalEmployerModel,
    EmployerAliasModel,
    EmployerIdentityDecisionModel,
    EmployerProviderBoardModel,
    EmployerVerifiedDomainModel,
)
from app.recruitment.aggregation.contracts import (
    CanonicalEmployerRecord,
    EmployerIdentityStatus,
    OrganizationType,
)
from app.recruitment.aggregation.employers.aliases import normalize_employer_name


class EmployerRegistry:
    """Repository and CRUD manager for canonical employers."""

    async def get_by_id(self, session: AsyncSession, employer_id: str) -> Optional[CanonicalEmployerModel]:
        stmt = (
            select(CanonicalEmployerModel)
            .options(
                joinedload(CanonicalEmployerModel.aliases),
                joinedload(CanonicalEmployerModel.verified_domains),
                joinedload(CanonicalEmployerModel.provider_boards),
            )
            .where(CanonicalEmployerModel.id == employer_id)
        )
        res = await session.execute(stmt)
        return res.unique().scalar_one_or_none()

    async def find_by_normalized_name(self, session: AsyncSession, name: str) -> Optional[CanonicalEmployerModel]:
        norm = normalize_employer_name(name)
        stmt = select(CanonicalEmployerModel).where(CanonicalEmployerModel.name.ilike(f"%{norm}%"))
        res = await session.execute(stmt)
        employers = res.scalars().all()
        for emp in employers:
            if normalize_employer_name(emp.name) == norm:
                return emp
        return None

    async def find_by_alias(self, session: AsyncSession, alias_text: str) -> Optional[CanonicalEmployerModel]:
        norm = normalize_employer_name(alias_text)
        stmt = (
            select(CanonicalEmployerModel)
            .join(EmployerAliasModel, EmployerAliasModel.employer_id == CanonicalEmployerModel.id)
            .where(EmployerAliasModel.normalized_alias == norm)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_domain(self, session: AsyncSession, domain: str) -> Optional[CanonicalEmployerModel]:
        clean_dom = domain.lower().strip()
        stmt = (
            select(CanonicalEmployerModel)
            .join(EmployerVerifiedDomainModel, EmployerVerifiedDomainModel.employer_id == CanonicalEmployerModel.id)
            .where(EmployerVerifiedDomainModel.domain == clean_dom)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_board(self, session: AsyncSession, provider: str, board_token: str) -> Optional[CanonicalEmployerModel]:
        stmt = (
            select(CanonicalEmployerModel)
            .join(EmployerProviderBoardModel, EmployerProviderBoardModel.employer_id == CanonicalEmployerModel.id)
            .where(
                EmployerProviderBoardModel.provider == provider.lower(),
                EmployerProviderBoardModel.board_token == board_token.lower(),
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_employer(
        self,
        session: AsyncSession,
        name: str,
        legal_name: Optional[str] = None,
        organization_type: OrganizationType = OrganizationType.DIRECT_EMPLOYER,
        identity_status: EmployerIdentityStatus = EmployerIdentityStatus.PROBABLE,
        official_careers_url: Optional[str] = None,
        primary_domain: Optional[str] = None,
        confidence_score: float = 0.8,
    ) -> CanonicalEmployerModel:
        emp = CanonicalEmployerModel(
            name=name.strip(),
            legal_name=legal_name.strip() if legal_name else None,
            organization_type=organization_type.value,
            identity_status=identity_status.value,
            official_careers_url=official_careers_url.strip() if official_careers_url else None,
            primary_domain=primary_domain.strip().lower() if primary_domain else None,
            confidence_score=confidence_score,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(emp)
        await session.flush()

        # Add initial self alias
        alias = EmployerAliasModel(
            employer_id=emp.id,
            alias=name.strip(),
            normalized_alias=normalize_employer_name(name),
            category="trading_name",
            source_evidence="initial_creation",
            is_verified=True,
            created_at=datetime.now(UTC),
        )
        session.add(alias)

        if primary_domain:
            dom = EmployerVerifiedDomainModel(
                employer_id=emp.id,
                domain=primary_domain.strip().lower(),
                is_primary=True,
                verification_method="careers_url" if official_careers_url else "manual",
                created_at=datetime.now(UTC),
            )
            session.add(dom)

        await session.flush()
        return emp

    async def list_employers(
        self,
        session: AsyncSession,
        query: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CanonicalEmployerModel]:
        stmt = (
            select(CanonicalEmployerModel)
            .options(
                joinedload(CanonicalEmployerModel.aliases),
                joinedload(CanonicalEmployerModel.verified_domains),
                joinedload(CanonicalEmployerModel.provider_boards),
            )
        )
        if status:
            stmt = stmt.where(CanonicalEmployerModel.identity_status == status)
        if query:
            stmt = stmt.where(CanonicalEmployerModel.name.ilike(f"%{query.strip()}%"))
        stmt = stmt.order_by(CanonicalEmployerModel.name.asc()).limit(limit).offset(offset)
        res = await session.execute(stmt)
        return list(res.unique().scalars().all())


employer_registry = EmployerRegistry()
