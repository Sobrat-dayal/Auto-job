"""Discovery Coordinator and Synchronization Engine (Stage 26).

Coordinates multi-source job discovery runs, bounded parallel fetching,
incremental snapshot reconciliation, change detection, and Stage 25 policy pre-filtering.
Enforces the critical invariant: partial snapshots must NEVER mass-close postings!
"""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
import logging
from typing import Any, Optional
from uuid import uuid4

from app.recruitment.discovery.connectors.manual_import import ManualImportConnector
from app.recruitment.discovery.connectors.registry import connector_registry
from app.recruitment.discovery.connectors.url_import import UrlImportConnector
from app.recruitment.discovery.contracts import (
    ConnectorId,
    DiscoveryOverviewStats,
    DiscoverySettingsConfig,
    DiscoveryTaskCreateRequest,
    DiscoveryTaskRecord,
    DiscoveryTaskState,
    ExtractedPosting,
    JobSourceConfig,
    JobSourceObservation,
    JobSourceSnapshot,
    ManualImportRequest,
    PostingAvailability,
    PrefilterOutcome,
    SnapshotCompleteness,
    SourceAccessStatus,
    UrlImportRequest,
)
from app.recruitment.discovery.errors import (
    JobDiscoveryError,
    SourceAccessRestrictedError,
    SourceNotFoundError,
    TaskCancelledError,
)
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient
from app.recruitment.discovery.sources.registry import source_registry

logger = logging.getLogger("autonom.recruitment.discovery.synchronization.coordinator")


class DiscoveryCoordinator:
    """Master orchestrator for discovering, synchronizing, and observing job postings."""

    def __init__(self, http_client: Optional[DiscoveryHttpClient] = None) -> None:
        self.http_client = http_client or DiscoveryHttpClient()
        self.settings = DiscoverySettingsConfig()
        self._observations: dict[str, JobSourceObservation] = {}
        # Index: (source_id, native_posting_id) -> observation_id
        self._source_posting_index: dict[tuple[str, str], str] = {}
        self._snapshots: dict[str, JobSourceSnapshot] = {}
        self._tasks: dict[str, DiscoveryTaskRecord] = {}
        self._active_async_tasks: dict[str, asyncio.Task] = {}

    # -------------------------------------------------------------------------
    # Observation Store Operations
    # -------------------------------------------------------------------------
    def get_observation(self, observation_id: str) -> Optional[JobSourceObservation]:
        return self._observations.get(observation_id)

    def find_observation_by_native_id(self, source_id: str, native_posting_id: str) -> Optional[JobSourceObservation]:
        obs_id = self._source_posting_index.get((source_id, native_posting_id))
        return self._observations.get(obs_id) if obs_id else None

    def list_observations(
        self,
        source_id: Optional[str] = None,
        availability: Optional[PostingAvailability] = None,
        prefilter: Optional[PrefilterOutcome] = None,
        query: Optional[str] = None,
        limit: int = 100,
    ) -> list[JobSourceObservation]:
        items = list(self._observations.values())
        if source_id:
            items = [obs for obs in items if obs.source_id == source_id]
        if availability:
            items = [obs for obs in items if obs.availability == availability]
        if prefilter:
            items = [obs for obs in items if obs.prefilter_status == prefilter]
        if query:
            q = query.lower()
            items = [
                obs for obs in items
                if q in obs.title.lower() or q in obs.employer.lower() or q in obs.description_text.lower()
            ]
        # Sort by last fetched at descending
        items.sort(key=lambda x: x.last_fetched_at, reverse=True)
        return items[:limit]

    # -------------------------------------------------------------------------
    # Stage 25 Policy Pre-filtering Integration
    # -------------------------------------------------------------------------
    def _evaluate_prefilter(
        self,
        posting: ExtractedPosting,
        strategy_id: Optional[str] = None,
    ) -> tuple[PrefilterOutcome, list[str]]:
        """Evaluate posting against active recruitment policy rules."""
        reasons: list[str] = []
        try:
            from app.recruitment.policy.service import recruitment_policy_service
            strategy = (
                recruitment_policy_service.get_strategy(strategy_id)
                if strategy_id
                else recruitment_policy_service.get_active_strategy()
            )
            if not strategy:
                return PrefilterOutcome.PREFILTER_ACCEPTED, ["No active recruitment strategy; default accepted"]

            # 1. Employer blocklist check
            emp_name = posting.employer_name.strip().lower()
            for blocked in strategy.employers.blocked_employers:
                if blocked.employer_name.strip().lower() in emp_name or emp_name in blocked.employer_name.strip().lower():
                    return PrefilterOutcome.PREFILTER_REJECTED, [f"Employer '{posting.employer_name}' is blocked by policy: {blocked.reason}"]

            # 2. Excluded target roles check
            title_lower = posting.title.lower()
            for role in strategy.target_roles:
                if role.is_excluded and role.title.lower() in title_lower:
                    return PrefilterOutcome.PREFILTER_REJECTED, [f"Role matches excluded title '{role.title}'"]

            # 3. Compensation minimum check
            if (
                posting.compensation
                and posting.compensation.max_amount
                and strategy.compensation
                and strategy.compensation.is_hard_minimum
            ):
                if Decimal(str(posting.compensation.max_amount)) < strategy.compensation.min_acceptable_amount:
                    return PrefilterOutcome.PREFILTER_REJECTED, [
                        f"Published maximum compensation ({posting.compensation.max_amount}) is below floor ({strategy.compensation.min_acceptable_amount})"
                    ]

            # 4. Work arrangement check
            if strategy.work_arrangement and strategy.work_arrangement.is_hard_constraint:
                allowed_arrs = [a.value.lower() for a in strategy.work_arrangement.allowed_arrangements]
                if posting.location.workplace_type and posting.location.workplace_type.lower() not in allowed_arrs:
                    return PrefilterOutcome.PREFILTER_REJECTED, [
                        f"Workplace arrangement '{posting.location.workplace_type}' is not permitted by policy"
                    ]

            # 5. Remote country constraint check
            if strategy.geography and strategy.geography.remote_within_country_only:
                if posting.location.country and posting.location.country.lower() not in [c.lower() for c in strategy.geography.allowed_countries]:
                    return PrefilterOutcome.NEEDS_REVIEW, [
                        f"Location country '{posting.location.country}' outside allowed countries"
                    ]

            return PrefilterOutcome.PREFILTER_ACCEPTED, ["Matches active career strategy criteria"]
        except Exception as exc:
            logger.warning("Policy pre-filter evaluation encountered an error: %s", exc)
            return PrefilterOutcome.NEEDS_REVIEW, [f"Policy evaluation error: {str(exc)}"]

    # -------------------------------------------------------------------------
    # Core Synchronization & Invariant Enforcement
    # -------------------------------------------------------------------------
    async def sync_source(
        self,
        source_id: str,
        task_id: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        strategy_id: Optional[str] = None,
    ) -> JobSourceSnapshot:
        """Fetch postings from a single source, reconcile snapshots, and update observations.
        
        CRITICAL INVARIANT: Partial snapshots must NEVER mark missing postings as closed!
        """
        source_config = source_registry.get_source(source_id)
        if not source_config.is_enabled:
            raise SourceAccessRestrictedError(f"Source '{source_config.name}' is currently disabled")

        if source_config.access_status in (
            SourceAccessStatus.REQUIRES_CREDENTIALS,
            SourceAccessStatus.RESTRICTED_BY_TERMS,
            SourceAccessStatus.ACCESS_DENIED,
        ):
            raise SourceAccessRestrictedError(
                f"Source '{source_config.name}' access status is {source_config.access_status.value}"
            )

        connector = connector_registry.get_connector(source_config.connector_id)
        effective_task_id = task_id or f"direct_sync_{uuid4().hex[:8]}"

        snapshot = JobSourceSnapshot(
            source_id=source_id,
            task_id=effective_task_id,
            completeness=SnapshotCompleteness.COMPLETE,
        )

        start_time = datetime.now(UTC)
        extracted_postings: list[ExtractedPosting] = []
        is_partial = False
        error_msg: Optional[str] = None
        rate_limited = False

        try:
            extracted_postings = await connector.fetch_postings(
                config=source_config,
                client=self.http_client,
                params=params,
            )
        except Exception as exc:
            err_str = str(exc)
            logger.error("Error fetching postings from source '%s': %s", source_id, err_str)
            error_msg = err_str
            if "rate limit" in err_str.lower() or "429" in err_str:
                snapshot.completeness = SnapshotCompleteness.RATE_LIMITED
                rate_limited = True
            else:
                snapshot.completeness = SnapshotCompleteness.PARTIAL
            is_partial = True

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        # Update source health
        source_registry.record_health(
            source_id=source_id,
            success=not is_partial,
            latency_ms=latency_ms,
            error=error_msg,
            retrieved_count=len(extracted_postings),
            rate_limited=rate_limited,
        )

        # Process observed postings
        snapshot.total_observed = len(extracted_postings)
        observed_native_ids: set[str] = set()
        now_iso = datetime.now(UTC).isoformat()

        for posting in extracted_postings:
            native_id = posting.native_posting_id
            observed_native_ids.add(native_id)

            existing = self.find_observation_by_native_id(source_id, native_id)
            prefilter_status, prefilter_reasons = self._evaluate_prefilter(posting, strategy_id)

            if existing is None:
                # Brand new posting
                new_obs = JobSourceObservation(
                    source_id=source_id,
                    provider=source_config.connector_id,
                    native_posting_id=native_id,
                    source_url=posting.official_posting_url,
                    title=posting.title,
                    employer=posting.employer_name,
                    location=posting.location,
                    employment_type=posting.employment_type,
                    compensation=posting.compensation,
                    description_text=posting.description_text,
                    application_url=posting.application_url or posting.official_posting_url,
                    department=posting.department,
                    posted_at=posting.posted_date,
                    updated_at=posting.updated_date,
                    discovered_at=now_iso,
                    last_fetched_at=now_iso,
                    availability=PostingAvailability.AVAILABLE,
                    prefilter_status=prefilter_status,
                    prefilter_reasons=prefilter_reasons,
                    snapshot_id=snapshot.id,
                )
                self._observations[new_obs.id] = new_obs
                self._source_posting_index[(source_id, native_id)] = new_obs.id
                snapshot.new_count += 1
            else:
                # Existing posting reconciliation
                is_changed = (
                    existing.title != posting.title
                    or existing.description_text != posting.description_text
                    or existing.compensation != posting.compensation
                )
                existing.last_fetched_at = now_iso
                existing.availability = PostingAvailability.AVAILABLE
                existing.snapshot_id = snapshot.id
                existing.prefilter_status = prefilter_status
                existing.prefilter_reasons = prefilter_reasons

                if is_changed:
                    existing.title = posting.title
                    existing.description_text = posting.description_text
                    existing.compensation = posting.compensation
                    existing.location = posting.location
                    existing.updated_at = now_iso
                    snapshot.updated_count += 1
                else:
                    snapshot.unchanged_count += 1

        # ---------------------------------------------------------------------
        # ENFORCE PARTIAL SNAPSHOT SAFETY INVARIANT:
        # Only mark missing postings closed if the snapshot was completely successful!
        # If the snapshot was partial, interrupted, or rate-limited, leave postings unchanged.
        # ---------------------------------------------------------------------
        if snapshot.completeness == SnapshotCompleteness.COMPLETE:
            # Check previously active postings from this source
            for (s_id, n_id), obs_id in list(self._source_posting_index.items()):
                if s_id == source_id and n_id not in observed_native_ids:
                    obs = self._observations.get(obs_id)
                    if obs and obs.availability == PostingAvailability.AVAILABLE:
                        obs.availability = PostingAvailability.CLOSED
                        obs.updated_at = now_iso
                        snapshot.closed_count += 1
        else:
            logger.info(
                "Source '%s' snapshot completeness is %s; preserving existing active postings without closing",
                source_id,
                snapshot.completeness.value,
            )

        snapshot.completed_at = datetime.now(UTC).isoformat()
        snapshot.error_message = error_msg
        self._snapshots[snapshot.id] = snapshot

        source_config.last_synced_at = now_iso
        return snapshot

    # -------------------------------------------------------------------------
    # Discovery Task Orchestration
    # -------------------------------------------------------------------------
    def create_task(self, req: DiscoveryTaskCreateRequest) -> DiscoveryTaskRecord:
        """Create and queue a multi-source discovery task."""
        task_id = f"task_{uuid4().hex[:10]}"
        selected_sources = req.source_ids or [s.id for s in source_registry.list_sources(enabled_only=True)]

        task = DiscoveryTaskRecord(
            id=task_id,
            strategy_id=req.strategy_id,
            requested_sources=req.source_ids,
            selected_sources=selected_sources,
            status=DiscoveryTaskState.QUEUED,
        )
        self._tasks[task_id] = task
        return task

    async def execute_task(self, task_id: str) -> DiscoveryTaskRecord:
        """Execute discovery task with bounded parallelism across sources."""
        task = self._tasks.get(task_id)
        if not task:
            raise JobDiscoveryError(f"Task with ID '{task_id}' not found")

        task.status = DiscoveryTaskState.RUNNING
        task.started_at = datetime.now(UTC).isoformat()

        semaphore = asyncio.Semaphore(self.settings.max_concurrent_sources)
        total_found = 0
        total_new = 0

        async def _run_source(src_id: str) -> None:
            nonlocal total_found, total_new
            if task.cancellation_requested:
                return

            async with semaphore:
                try:
                    snapshot = await self.sync_source(
                        source_id=src_id,
                        task_id=task.id,
                        strategy_id=task.strategy_id,
                    )
                    task.source_snapshots[src_id] = snapshot.id
                    total_found += snapshot.total_observed
                    total_new += snapshot.new_count
                    if snapshot.completeness != SnapshotCompleteness.COMPLETE:
                        task.errors.append(f"Source {src_id}: completeness {snapshot.completeness.value} ({snapshot.error_message})")
                except Exception as exc:
                    task.errors.append(f"Source {src_id} failed: {str(exc)}")

        # Fan-out bounded execution
        fetch_coroutines = [_run_source(sid) for sid in task.selected_sources]
        await asyncio.gather(*fetch_coroutines, return_exceptions=True)

        task.completed_at = datetime.now(UTC).isoformat()
        task.total_postings_found = total_found
        task.new_postings_count = total_new

        if task.cancellation_requested:
            task.status = DiscoveryTaskState.CANCELLED
        elif task.errors and len(task.errors) == len(task.selected_sources):
            task.status = DiscoveryTaskState.FAILED
        elif task.errors:
            task.status = DiscoveryTaskState.PARTIALLY_COMPLETED
        else:
            task.status = DiscoveryTaskState.COMPLETED

        return task

    def start_task_background(self, task_id: str) -> DiscoveryTaskRecord:
        """Schedule a task to run in the background."""
        task = self._tasks.get(task_id)
        if not task:
            raise JobDiscoveryError(f"Task with ID '{task_id}' not found")
        
        async_task = asyncio.create_task(self.execute_task(task_id))
        self._active_async_tasks[task_id] = async_task
        return task

    def cancel_task(self, task_id: str) -> bool:
        """Request cancellation of an active task."""
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.cancellation_requested = True
        task.status = DiscoveryTaskState.CANCELLED
        if task_id in self._active_async_tasks:
            self._active_async_tasks[task_id].cancel()
        return True

    def get_task(self, task_id: str) -> Optional[DiscoveryTaskRecord]:
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 50) -> list[DiscoveryTaskRecord]:
        items = list(self._tasks.values())
        items.sort(key=lambda x: x.started_at, reverse=True)
        return items[:limit]

    # -------------------------------------------------------------------------
    # Import Handlers
    # -------------------------------------------------------------------------
    async def import_from_url(self, req: UrlImportRequest) -> JobSourceObservation:
        """Extract and observe a posting from a single user-supplied URL."""
        url_conn = connector_registry.get_connector(ConnectorId.URL_IMPORT)
        assert isinstance(url_conn, UrlImportConnector)

        extracted = await url_conn.import_from_url(req, self.http_client)
        now_iso = datetime.now(UTC).isoformat()
        prefilter_status, prefilter_reasons = self._evaluate_prefilter(extracted)

        obs = JobSourceObservation(
            source_id="user_url_import",
            provider=ConnectorId.URL_IMPORT,
            native_posting_id=extracted.native_posting_id,
            source_url=extracted.official_posting_url,
            title=extracted.title,
            employer=extracted.employer_name,
            location=extracted.location,
            employment_type=extracted.employment_type,
            compensation=extracted.compensation,
            description_text=extracted.description_text,
            application_url=extracted.application_url or extracted.official_posting_url,
            posted_at=extracted.posted_date,
            discovered_at=now_iso,
            last_fetched_at=now_iso,
            availability=PostingAvailability.AVAILABLE,
            prefilter_status=prefilter_status,
            prefilter_reasons=prefilter_reasons,
        )
        self._observations[obs.id] = obs
        self._source_posting_index[("user_url_import", obs.native_posting_id)] = obs.id
        return obs

    def import_manual(self, req: ManualImportRequest) -> JobSourceObservation:
        """Store a manually entered job posting."""
        manual_conn = connector_registry.get_connector(ConnectorId.MANUAL_IMPORT)
        assert isinstance(manual_conn, ManualImportConnector)

        extracted = manual_conn.create_from_request(req)
        now_iso = datetime.now(UTC).isoformat()
        prefilter_status, prefilter_reasons = self._evaluate_prefilter(extracted)

        obs = JobSourceObservation(
            source_id="manual_entry",
            provider=ConnectorId.MANUAL_IMPORT,
            native_posting_id=extracted.native_posting_id,
            source_url=extracted.official_posting_url,
            title=extracted.title,
            employer=extracted.employer_name,
            location=extracted.location,
            employment_type=extracted.employment_type,
            compensation=extracted.compensation,
            description_text=extracted.description_text,
            application_url=extracted.application_url,
            posted_at=extracted.posted_date,
            discovered_at=now_iso,
            last_fetched_at=now_iso,
            availability=PostingAvailability.AVAILABLE,
            prefilter_status=prefilter_status,
            prefilter_reasons=prefilter_reasons,
        )
        self._observations[obs.id] = obs
        self._source_posting_index[("manual_entry", obs.native_posting_id)] = obs.id
        return obs

    # -------------------------------------------------------------------------
    # Diagnostics & Stats
    # -------------------------------------------------------------------------
    def get_overview_stats(self) -> DiscoveryOverviewStats:
        all_sources = source_registry.list_sources()
        enabled = [s for s in all_sources if s.is_enabled]
        health_items = source_registry.list_health()

        failed_count = sum(1 for h in health_items if h.consecutive_failures >= 3)
        rate_limited_count = sum(1 for h in health_items if h.current_status == SourceAccessStatus.TEMPORARILY_RATE_LIMITED)
        active_tasks = sum(1 for t in self._tasks.values() if t.status in (DiscoveryTaskState.RUNNING, DiscoveryTaskState.QUEUED))

        active_postings = sum(1 for o in self._observations.values() if o.availability == PostingAvailability.AVAILABLE)

        return DiscoveryOverviewStats(
            total_sources=len(all_sources),
            enabled_sources=len(enabled),
            total_observations=len(self._observations),
            active_postings_count=active_postings,
            recently_discovered_count=len(self._observations),
            failed_sources_count=failed_count,
            rate_limited_sources_count=rate_limited_count,
            active_tasks_count=active_tasks,
        )

    def get_settings(self) -> DiscoverySettingsConfig:
        return self.settings

    def update_settings(self, new_settings: DiscoverySettingsConfig) -> DiscoverySettingsConfig:
        self.settings = new_settings
        return self.settings


# Global coordinator singleton
discovery_coordinator = DiscoveryCoordinator()
