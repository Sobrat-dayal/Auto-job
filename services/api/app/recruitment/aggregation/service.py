"""Master Job Aggregation Service Facade (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AggregationSettingsModel,
    CanonicalEmployerModel,
    CanonicalJobConflictModel,
    CanonicalJobModel,
    CanonicalJobSourceLinkModel,
    EmployerAliasModel,
    EmployerVerifiedDomainModel,
    JobDuplicateCandidateModel,
)
from app.recruitment.aggregation.canonical.conflicts import field_conflict_manager
from app.recruitment.aggregation.canonical.registry import (
    CanonicalJobRegistry,
    canonical_job_registry,
)
from app.recruitment.aggregation.contracts import (
    AggregationDiagnosticsReport,
    AggregationOverviewStats,
    AggregationSettingsConfig,
    AggregationTaskRecord,
    CanonicalEmployerRecord,
    CanonicalJobRecord,
    CanonicalJobSourceLinkRecord,
    DuplicateAction,
    DuplicateCandidateRecord,
    EmployerCorrectionRequest,
    MergeExecuteResponse,
    MergePreviewResponse,
    SplitExecuteResponse,
    SplitPreviewResponse,
)
from app.recruitment.aggregation.employers.identity import (
    EmployerIdentityResolver,
    employer_identity_resolver,
)
from app.recruitment.aggregation.employers.registry import (
    EmployerRegistry,
    employer_registry,
)
from app.recruitment.aggregation.identity_operations.merge import (
    MergeExecutionEngine,
    merge_execution_engine,
)
from app.recruitment.aggregation.identity_operations.merge_preview import (
    MergePreviewEngine,
    merge_preview_engine,
)
from app.recruitment.aggregation.identity_operations.split import (
    SplitExecutionEngine,
    split_execution_engine,
)
from app.recruitment.aggregation.identity_operations.split_preview import (
    SplitPreviewEngine,
    split_preview_engine,
)
from app.recruitment.aggregation.integrations.discovery import (
    DiscoveryIntegrationBridge,
    discovery_integration_bridge,
)
from app.recruitment.aggregation.processing.incremental import (
    BatchAggregationProcessor,
    batch_aggregation_processor,
)
from app.recruitment.aggregation.processing.ingestion import (
    ObservationIngestionPipeline,
    observation_ingestion_pipeline,
)
from app.recruitment.aggregation.review.queue import (
    DuplicateReviewQueueManager,
    duplicate_review_queue_manager,
)


class JobAggregationService:
    """Master facade for multi-source job aggregation, duplicate detection, and canonical registry."""

    def __init__(
        self,
        jobs: Optional[CanonicalJobRegistry] = None,
        employers: Optional[EmployerRegistry] = None,
        employer_resolver: Optional[EmployerIdentityResolver] = None,
        ingestion: Optional[ObservationIngestionPipeline] = None,
        batch_processor: Optional[BatchAggregationProcessor] = None,
        merge_preview: Optional[MergePreviewEngine] = None,
        merge_engine: Optional[MergeExecutionEngine] = None,
        split_preview: Optional[SplitPreviewEngine] = None,
        split_engine: Optional[SplitExecutionEngine] = None,
        review_queue: Optional[DuplicateReviewQueueManager] = None,
        discovery_bridge: Optional[DiscoveryIntegrationBridge] = None,
    ) -> None:
        self.jobs = jobs or canonical_job_registry
        self.employers = employers or employer_registry
        self.employer_resolver = employer_resolver or employer_identity_resolver
        self.ingestion = ingestion or observation_ingestion_pipeline
        self.batch_processor = batch_processor or batch_aggregation_processor
        self.merge_preview = merge_preview or merge_preview_engine
        self.merge_engine = merge_engine or merge_execution_engine
        self.split_preview = split_preview or split_preview_engine
        self.split_engine = split_engine or split_execution_engine
        self.review_queue = review_queue or duplicate_review_queue_manager
        self.discovery_bridge = discovery_bridge or discovery_bridge

    # -------------------------------------------------------------------------
    # Overview & Stats
    # -------------------------------------------------------------------------
    async def get_overview_stats(self, session: AsyncSession) -> AggregationOverviewStats:
        total_obs = (await session.execute(select(func.count(CanonicalJobSourceLinkModel.id)))).scalar() or 0
        total_jobs = (await session.execute(select(func.count(CanonicalJobModel.id)))).scalar() or 0
        multi_source = (
            await session.execute(
                select(func.count(CanonicalJobModel.id)).where(CanonicalJobModel.source_count > 1)
            )
        ).scalar() or 0
        pending_reviews = (
            await session.execute(
                select(func.count(JobDuplicateCandidateModel.id)).where(
                    JobDuplicateCandidateModel.status.in_(["proposed", "in_review", "possible_duplicate"])
                )
            )
        ).scalar() or 0
        unresolved_emps = (
            await session.execute(
                select(func.count(CanonicalEmployerModel.id)).where(
                    CanonicalEmployerModel.identity_status.in_(["ambiguous", "conflicted", "unknown"])
                )
            )
        ).scalar() or 0
        conflicts = (
            await session.execute(
                select(func.count(CanonicalJobConflictModel.id)).where(
                    CanonicalJobConflictModel.status == "unresolved"
                )
            )
        ).scalar() or 0

        return AggregationOverviewStats(
            total_source_observations=total_obs,
            total_canonical_jobs=total_jobs,
            multi_source_canonical_jobs=multi_source,
            pending_duplicate_reviews=pending_reviews,
            confirmed_duplicate_merges=0,
            unresolved_employer_identities=unresolved_emps,
            active_field_conflicts=conflicts,
            running_tasks=0,
            last_sync_timestamp=datetime.now(UTC).isoformat(),
        )

    # -------------------------------------------------------------------------
    # Canonical Jobs
    # -------------------------------------------------------------------------
    async def list_jobs(
        self,
        session: AsyncSession,
        query: Optional[str] = None,
        status: Optional[str] = None,
        employer_id: Optional[str] = None,
        work_arrangement: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CanonicalJobRecord]:
        jobs = await self.jobs.list_jobs(
            session=session,
            query=query,
            status=status,
            employer_id=employer_id,
            work_arrangement=work_arrangement,
            limit=limit,
            offset=offset,
        )
        return [self.jobs.to_contract(j) for j in jobs]

    async def get_job(self, session: AsyncSession, job_id: str) -> Optional[CanonicalJobRecord]:
        job = await self.jobs.get_by_id(session, job_id)
        return self.jobs.to_contract(job) if job else None

    # -------------------------------------------------------------------------
    # Ingestion & Discovery
    # -------------------------------------------------------------------------
    async def process_observation(
        self,
        session: AsyncSession,
        observation: dict[str, Any],
        auto_merge: bool = True,
    ) -> CanonicalJobRecord:
        obs_id = observation.get("id") or observation.get("observation_id") or "obs_unknown"
        job, _ = await self.ingestion.ingest_observation(
            session=session,
            observation_id=obs_id,
            source_id=observation.get("source_id", "src_default"),
            provider=observation.get("provider", "greenhouse"),
            native_posting_id=observation.get("native_posting_id", obs_id),
            title=observation.get("title", "Untitled Job"),
            employer_name=observation.get("employer_name", observation.get("employer", "Unknown Employer")),
            source_url=observation.get("source_url", ""),
            application_url=observation.get("application_url"),
            location_raw=observation.get("location_raw") or observation.get("location"),
            workplace_type=observation.get("workplace_type"),
            employment_type=observation.get("employment_type"),
            salary_raw=observation.get("salary_raw") or observation.get("salary_range"),
            description_text=observation.get("description_text") or observation.get("description"),
            posted_at=observation.get("posted_at"),
            listing_id=observation.get("listing_id"),
            auto_merge_enabled=auto_merge,
        )
        loaded = await self.jobs.get_by_id(session, job.id)
        return self.jobs.to_contract(loaded or job)

    async def process_batch(
        self,
        session: AsyncSession,
        observations: list[dict[str, Any]],
        auto_merge: bool = True,
    ) -> AggregationTaskRecord:
        return await self.batch_processor.process_batch(
            session=session,
            observations=observations,
            auto_merge_enabled=auto_merge,
        )

    async def sync_from_discovery(
        self,
        session: AsyncSession,
        limit: int = 100,
    ) -> AggregationTaskRecord:
        return await discovery_integration_bridge.sync_from_job_listings(session=session, limit=limit)

    # -------------------------------------------------------------------------
    # Duplicate Reviews
    # -------------------------------------------------------------------------
    async def list_duplicate_reviews(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DuplicateCandidateRecord]:
        return await self.review_queue.list_pending_reviews(session, limit, offset)

    async def submit_duplicate_review(
        self,
        session: AsyncSession,
        candidate_id: str,
        decision: DuplicateAction,
        reason: str = "User reviewed decision",
        decided_by: str = "user_manual",
    ) -> bool:
        return await self.review_queue.submit_review_decision(
            session=session,
            candidate_id=candidate_id,
            decision=decision,
            reason=reason,
            decided_by=decided_by,
        )

    # -------------------------------------------------------------------------
    # Merge and Split
    # -------------------------------------------------------------------------
    async def preview_merge(
        self,
        session: AsyncSession,
        surviving_id: str,
        superseded_id: str,
    ) -> MergePreviewResponse:
        return await self.merge_preview.preview_merge(session, surviving_id, superseded_id)

    async def execute_merge(
        self,
        session: AsyncSession,
        surviving_id: str,
        superseded_id: str,
        actor: str = "user_manual",
        reason: str = "Authorized duplicate merge",
        field_overrides: Optional[dict[str, Any]] = None,
    ) -> MergeExecuteResponse:
        return await self.merge_engine.execute_merge(
            session=session,
            surviving_job_id=surviving_id,
            superseded_job_id=superseded_id,
            actor=actor,
            reason=reason,
            field_overrides=field_overrides,
        )

    async def preview_split(
        self,
        session: AsyncSession,
        job_id: str,
    ) -> SplitPreviewResponse:
        return await self.split_preview.preview_split(session, job_id)

    async def execute_split(
        self,
        session: AsyncSession,
        job_id: str,
        link_ids: list[str],
        actor: str = "user_manual",
        reason: str = "Reversing incorrect merge",
    ) -> SplitExecuteResponse:
        return await self.split_engine.execute_split(
            session=session,
            source_job_id=job_id,
            source_link_ids_to_detach=link_ids,
            actor=actor,
            reason=reason,
        )

    # -------------------------------------------------------------------------
    # Employers
    # -------------------------------------------------------------------------
    async def list_employers(
        self,
        session: AsyncSession,
        query: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CanonicalEmployerRecord]:
        emps = await self.employers.list_employers(session, query, status, limit, offset)
        records = []
        for e in emps:
            aliases = [a.alias for a in getattr(e, "aliases", [])]
            domains = [d.domain for d in getattr(e, "verified_domains", [])]
            boards = [{"provider": b.provider, "token": b.board_token} for b in getattr(e, "provider_boards", [])]
            records.append(
                CanonicalEmployerRecord(
                    id=e.id,
                    name=e.name,
                    legal_name=e.legal_name,
                    organization_type=e.organization_type,
                    identity_status=e.identity_status,
                    official_careers_url=e.official_careers_url,
                    primary_domain=e.primary_domain,
                    confidence_score=e.confidence_score,
                    aliases=aliases,
                    verified_domains=domains,
                    provider_boards=boards,
                    created_at=e.created_at.isoformat() if hasattr(e.created_at, "isoformat") else str(e.created_at),
                    updated_at=e.updated_at.isoformat() if hasattr(e.updated_at, "isoformat") else str(e.updated_at),
                )
            )
        return records

    async def get_employer(self, session: AsyncSession, employer_id: str) -> Optional[CanonicalEmployerRecord]:
        e = await self.employers.get_by_id(session, employer_id)
        if not e:
            return None
        aliases = [a.alias for a in (e.__dict__.get("aliases") or [])]
        domains = [d.domain for d in (e.__dict__.get("verified_domains") or [])]
        boards = [{"provider": b.provider, "token": b.board_token} for b in (e.__dict__.get("provider_boards") or [])]
        return CanonicalEmployerRecord(
            id=e.id,
            name=e.name,
            legal_name=e.legal_name,
            organization_type=e.organization_type,
            identity_status=e.identity_status,
            official_careers_url=e.official_careers_url,
            primary_domain=e.primary_domain,
            confidence_score=e.confidence_score,
            aliases=aliases,
            verified_domains=domains,
            provider_boards=boards,
            created_at=e.created_at.isoformat() if hasattr(e.created_at, "isoformat") else str(e.created_at),
            updated_at=e.updated_at.isoformat() if hasattr(e.updated_at, "isoformat") else str(e.updated_at),
        )

    async def resolve_employer(
        self,
        session: AsyncSession,
        raw_name: str,
        source_url: Optional[str] = None,
        provider: Optional[str] = None,
        description: Optional[str] = None,
    ) -> CanonicalEmployerRecord:
        emp, _ = await self.employer_resolver.resolve_employer(
            session=session,
            raw_name=raw_name,
            source_url=source_url,
            provider=provider,
            description=description,
        )
        return (await self.get_employer(session, emp.id)) or CanonicalEmployerRecord(id=emp.id, name=emp.name)

    async def correct_employer(
        self,
        session: AsyncSession,
        employer_id: str,
        req: EmployerCorrectionRequest,
    ) -> Optional[CanonicalEmployerRecord]:
        emp = await self.employers.get_by_id(session, employer_id)
        if not emp:
            return None

        if req.name:
            emp.name = req.name.strip()
        if req.legal_name:
            emp.legal_name = req.legal_name.strip()
        if req.organization_type:
            emp.organization_type = req.organization_type.value
        if req.official_careers_url:
            emp.official_careers_url = req.official_careers_url.strip()

        if req.add_alias:
            alias = EmployerAliasModel(
                employer_id=emp.id,
                alias=req.add_alias.strip(),
                normalized_alias=req.add_alias.lower().strip(),
                category="trading_name",
                source_evidence="user_manual_correction",
                is_verified=True,
                created_at=datetime.now(UTC),
            )
            session.add(alias)

        if req.add_domain:
            dom = EmployerVerifiedDomainModel(
                employer_id=emp.id,
                domain=req.add_domain.lower().strip(),
                is_primary=False,
                verification_method="user_manual_correction",
                created_at=datetime.now(UTC),
            )
            session.add(dom)

        emp.updated_at = datetime.now(UTC)
        await session.flush()
        return await self.get_employer(session, emp.id)

    # -------------------------------------------------------------------------
    # Conflicts
    # -------------------------------------------------------------------------
    async def resolve_conflict(
        self,
        session: AsyncSession,
        conflict_id: str,
        chosen_value: Any,
        resolution_note: str = "Resolved by user",
        resolved_by: str = "user_manual",
    ) -> bool:
        res = await field_conflict_manager.resolve_conflict(
            session=session,
            conflict_id=conflict_id,
            chosen_value=chosen_value,
            resolution_note=resolution_note,
            resolved_by=resolved_by,
        )
        return res is not None

    # -------------------------------------------------------------------------
    # Diagnostics & Settings
    # -------------------------------------------------------------------------
    async def get_diagnostics(self, session: AsyncSession) -> AggregationDiagnosticsReport:
        jobs_cnt = (await session.execute(select(func.count(CanonicalJobModel.id)))).scalar() or 0
        emps_cnt = (await session.execute(select(func.count(CanonicalEmployerModel.id)))).scalar() or 0
        conf_cnt = (
            await session.execute(
                select(func.count(CanonicalJobConflictModel.id)).where(CanonicalJobConflictModel.status == "unresolved")
            )
        ).scalar() or 0
        cands_cnt = (
            await session.execute(
                select(func.count(JobDuplicateCandidateModel.id)).where(
                    JobDuplicateCandidateModel.status.in_(["proposed", "possible_duplicate"])
                )
            )
        ).scalar() or 0

        return AggregationDiagnosticsReport(
            status="healthy",
            database_connected=True,
            canonical_jobs_count=jobs_cnt,
            canonical_employers_count=emps_cnt,
            active_conflicts_count=conf_cnt,
            unresolved_candidates_count=cands_cnt,
        )

    async def get_settings(self, session: AsyncSession) -> AggregationSettingsConfig:
        stmt = select(AggregationSettingsModel).where(AggregationSettingsModel.id == "default")
        res = await session.execute(stmt)
        s = res.scalar_one_or_none()
        if not s:
            return AggregationSettingsConfig()
        return AggregationSettingsConfig(
            auto_merge_enabled=s.auto_merge_enabled,
            min_similarity_for_candidate=s.min_similarity_for_candidate,
            min_similarity_for_auto_merge=s.min_similarity_for_auto_merge,
            require_same_requisition=s.require_same_requisition,
            enable_ai_assisted_review=s.enable_ai_assisted_review,
            batch_size=s.batch_size,
            worker_concurrency=s.worker_concurrency,
            updated_at=s.updated_at.isoformat(),
        )

    async def update_settings(
        self,
        session: AsyncSession,
        settings: AggregationSettingsConfig,
    ) -> AggregationSettingsConfig:
        stmt = select(AggregationSettingsModel).where(AggregationSettingsModel.id == "default")
        res = await session.execute(stmt)
        s = res.scalar_one_or_none()
        if not s:
            s = AggregationSettingsModel(id="default")
            session.add(s)

        s.auto_merge_enabled = settings.auto_merge_enabled
        s.min_similarity_for_candidate = settings.min_similarity_for_candidate
        s.min_similarity_for_auto_merge = settings.min_similarity_for_auto_merge
        s.require_same_requisition = settings.require_same_requisition
        s.enable_ai_assisted_review = settings.enable_ai_assisted_review
        s.batch_size = settings.batch_size
        s.worker_concurrency = settings.worker_concurrency
        s.updated_at = datetime.now(UTC)

        await session.flush()
        return settings


job_aggregation_service = JobAggregationService()
