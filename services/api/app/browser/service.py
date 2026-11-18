"""Central BrowserService coordinating sessions, security, interaction, and multi-agent browsing."""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.artifacts.downloads import BrowserDownloadManager
from app.browser.artifacts.screenshots import BrowserScreenshotManager
from app.browser.artifacts.traces import BrowserTraceManager
from app.browser.contracts import (
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserActionStatus,
    BrowserActionType,
    BrowserBatchActionsRequest,
    BrowserBatchActionsResponse,
    BrowserDownloadResponse,
    BrowserNavigateRequest,
    BrowserNavigateResponse,
    BrowserProfileCreateRequest,
    BrowserProfileResponse,
    BrowserRuntimeStatus,
    BrowserScreenshotRequest,
    BrowserScreenshotResponse,
    BrowserSessionCreateRequest,
    BrowserSessionResponse,
    BrowserSessionStatus,
    BrowserSessionSummary,
    BrowserTabCreateRequest,
    BrowserTabInfo,
    BrowserTabStatus,
    BrowserTaskCreateRequest,
    BrowserTaskResponse,
    BrowserTaskStatus,
    DOMInspectionRequest,
    DOMInspectionResponse,
)
from app.browser.interaction.actions import ActionExecutor
from app.browser.interaction.dom import DOMExtractor
from app.browser.interaction.forms import FormAnalyzer
from app.browser.interaction.verification import ActionVerifier
from app.browser.runtime.manager import BrowserRuntimeManager
from app.browser.runtime.profiles import BrowserProfileService
from app.browser.runtime.sessions import BrowserSessionManager, LiveSession
from app.browser.runtime.tabs import LiveTab
from app.browser.security.authentication import BrowserAuthenticationManager
from app.browser.security.origins import OriginValidator
from app.core.config import settings
from app.db.models import (
    BrowserActionRecord,
    BrowserDownloadRecord,
    BrowserSessionRecord,
    BrowserTabRecord,
    BrowserTaskRecord,
)
from app.security.authorization.emergency import EmergencyStopController

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrowserService:
    """Core Browser Automation Service managing the complete automation pipeline."""

    _instance: "BrowserService | None" = None

    def __init__(
        self,
        runtime_manager: BrowserRuntimeManager | None = None,
        session_manager: BrowserSessionManager | None = None,
        profile_service: BrowserProfileService | None = None,
        origin_validator: OriginValidator | None = None,
        download_manager: BrowserDownloadManager | None = None,
        screenshot_manager: BrowserScreenshotManager | None = None,
        trace_manager: BrowserTraceManager | None = None,
    ) -> None:
        self.runtime_manager = runtime_manager or BrowserRuntimeManager()
        self.session_manager = session_manager or BrowserSessionManager(runtime_manager=self.runtime_manager)
        self.profile_service = profile_service or BrowserProfileService()
        self.origin_validator = origin_validator or OriginValidator(
            allow_loopback=settings.is_loopback or settings.environment in ("development", "test"),
            allow_private_ips=settings.environment in ("development", "test"),
            test_mode=settings.environment == "test",
        )
        self.download_manager = download_manager or BrowserDownloadManager()
        self.screenshot_manager = screenshot_manager or BrowserScreenshotManager()
        self.trace_manager = trace_manager or BrowserTraceManager()
        self.emergency_controller = EmergencyStopController.get_instance()

    @classmethod
    def get_instance(cls) -> "BrowserService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _check_emergency_stop(self) -> None:
        """Verifies Emergency Stop is not triggered."""
        if self.emergency_controller.is_emergency_stop_active:
            raise RuntimeError("Emergency Stop is currently active. Browser operations are blocked.")
        if self.emergency_controller.is_automation_paused:
            raise RuntimeError("Automation is currently paused by administrator policy.")

    def get_runtime_status(self) -> BrowserRuntimeStatus:
        """Returns browser subsystem health and installed engines."""
        active_count = len(self.session_manager.active_sessions)
        return self.runtime_manager.get_runtime_status(active_sessions_count=active_count)

    async def create_session(
        self,
        db_session: AsyncSession,
        req: BrowserSessionCreateRequest,
    ) -> BrowserSessionResponse:
        """Creates and launches a new browser session."""
        self._check_emergency_stop()
        response = await self.session_manager.create_session(db_session, req)

        # Wire up download handler for the live session
        live = self.session_manager.get_live_session(response.id)
        if live:
            for tab in live.tab_manager.tabs.values():
                self._attach_tab_listeners(live, tab, db_session)

        return response

    def _attach_tab_listeners(self, live: LiveSession, tab: LiveTab, db_session: AsyncSession) -> None:
        """Attaches background download and navigation listeners to a live page."""
        async def on_download(download: Any) -> None:
            logger.info(f"Page triggered download {download.suggested_filename} in session {live.session_id}")
            # Create a dedicated background task or handle
            try:
                # We save download via manager
                await self.download_manager.handle_download(
                    db_session=db_session,
                    download=download,
                    session_id=live.session_id,
                    tab_id=tab.tab_id,
                )
            except Exception as e:
                logger.error(f"Error handling background download: {e}")

        tab.page.on("download", lambda d: asyncio.create_task(on_download(d)))

    async def get_session(
        self,
        db_session: AsyncSession,
        session_id: str,
    ) -> BrowserSessionResponse | None:
        """Retrieves session details from memory or database."""
        live = self.session_manager.get_live_session(session_id)
        if live:
            return await live.to_response()

        stmt = select(BrowserSessionRecord).where(BrowserSessionRecord.id == session_id)
        res = await db_session.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            return None

        # Fetch tabs
        tab_stmt = select(BrowserTabRecord).where(BrowserTabRecord.session_id == session_id).order_by(BrowserTabRecord.tab_index.asc())
        tab_res = await db_session.execute(tab_stmt)
        tab_records = tab_res.scalars().all()

        tabs: list[BrowserTabInfo] = [
            BrowserTabInfo(
                id=t.id,
                session_id=t.session_id,
                tab_index=t.tab_index,
                title=t.title,
                url=t.url,
                status=BrowserTabStatus(t.status) if t.status in BrowserTabStatus._value2member_map_ else BrowserTabStatus.CLOSED,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
                closed_at=t.closed_at,
            )
            for t in tab_records
        ]

        return BrowserSessionResponse(
            id=record.id,
            profile_id=record.profile_id,
            browser_type=record.browser_type,
            channel=record.channel,
            status=BrowserSessionStatus(record.status) if record.status in BrowserSessionStatus._value2member_map_ else BrowserSessionStatus.CLOSED,
            is_headless=record.is_headless,
            active_tab_id=record.active_tab_id,
            pid=record.pid,
            viewport_width=record.viewport_width,
            viewport_height=record.viewport_height,
            user_agent=record.user_agent,
            locale=record.locale,
            timezone_id=record.timezone_id,
            created_at=record.created_at,
            last_activity_at=record.last_activity_at,
            closed_at=record.closed_at,
            error_message=record.error_message,
            metadata=record.metadata_json or {},
            tabs=tabs,
        )

    async def list_sessions(self, db_session: AsyncSession) -> list[BrowserSessionSummary]:
        """Lists summaries of browser sessions."""
        return await self.session_manager.list_session_summaries(db_session)

    async def close_session(self, db_session: AsyncSession, session_id: str) -> bool:
        """Closes an active browser session."""
        return await self.session_manager.close_session(db_session, session_id)

    async def create_tab(
        self,
        db_session: AsyncSession,
        session_id: str,
        req: BrowserTabCreateRequest | None = None,
    ) -> BrowserTabInfo:
        """Opens a new tab in the session."""
        self._check_emergency_stop()
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not currently running.")

        url = req.url if req else None
        if url:
            sec_res = self.origin_validator.validate_url(url)
            if not sec_res.is_allowed:
                raise PermissionError(f"Navigation blocked by security policy: {sec_res.rejection_reason}")

        tab = await live.tab_manager.create_tab(url=url)
        self._attach_tab_listeners(live, tab, db_session)

        # Persist new tab record
        tab_rec = BrowserTabRecord(
            id=tab.tab_id,
            session_id=session_id,
            tab_index=tab.tab_index,
            title=tab.title,
            url=tab.url,
            status=tab.status.value,
            is_active=tab.is_active,
            created_at=tab.created_at,
            updated_at=tab.updated_at,
            closed_at=None,
        )
        db_session.add(tab_rec)
        await db_session.commit()

        live.touch()
        return tab.to_tab_info()

    async def switch_tab(self, session_id: str, tab_id: str) -> bool:
        """Switches the active tab in a session."""
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not active.")
        success = live.tab_manager.set_active_tab(tab_id)
        if success:
            live.touch()
        return success

    async def close_tab(self, session_id: str, tab_id: str) -> bool:
        """Closes a specific tab."""
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not active.")
        success = await live.tab_manager.close_tab(tab_id)
        if success:
            live.touch()
        return success

    async def navigate(
        self,
        db_session: AsyncSession,
        session_id: str,
        req: BrowserNavigateRequest,
    ) -> BrowserNavigateResponse:
        """Safely navigates the active tab to a permitted URL."""
        self._check_emergency_stop()
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not currently running.")

        # Origin Security Validation
        sec_result = self.origin_validator.validate_url(req.url)
        if not sec_result.is_allowed:
            logger.warning(f"Blocked navigation to {req.url}: {sec_result.rejection_reason}")
            raise PermissionError(f"Navigation blocked by security policy: {sec_result.rejection_reason}")

        # Target tab
        if req.tab_id:
            tab = live.tab_manager.tabs.get(req.tab_id)
            if not tab:
                raise ValueError(f"Tab {req.tab_id} not found in session {session_id}.")
            page = tab.page
            target_tab_id = req.tab_id
        else:
            page = live.get_active_page()
            active_tab = live.tab_manager.get_active_tab()
            target_tab_id = active_tab.tab_id if active_tab else "unknown"

        start_time = asyncio.get_event_loop().time()
        tab_obj = live.tab_manager.tabs.get(target_tab_id)
        if tab_obj:
            tab_obj.status = BrowserTabStatus.NAVIGATING

        try:
            resp = await page.goto(sec_result.normalized_url, wait_until=req.wait_until, timeout=req.timeout_ms)
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            current_title = await page.title()
            status_code = resp.status if resp else 200

            if tab_obj:
                await tab_obj.update_info()
                tab_obj.status = BrowserTabStatus.READY

            # Update tab record in DB
            stmt = (
                update(BrowserTabRecord)
                .where(BrowserTabRecord.id == target_tab_id)
                .values(
                    title=current_title,
                    url=page.url,
                    status=BrowserTabStatus.READY.value,
                    updated_at=utc_now(),
                )
            )
            await db_session.execute(stmt)
            await db_session.commit()

            live.touch()

            # Record action in DB
            action_rec = BrowserActionRecord(
                id=str(uuid4()),
                session_id=session_id,
                tab_id=target_tab_id,
                task_id=None,
                action_type=BrowserActionType.NAVIGATE.value,
                target_locator=None,
                parameters_json={"url": sec_result.normalized_url, "wait_until": req.wait_until},
                status=BrowserActionStatus.SUCCEEDED.value,
                result_json={"url": page.url, "title": current_title, "status_code": status_code},
                error_message=None,
                screenshot_path=None,
                started_at=utc_now(),
                completed_at=utc_now(),
                duration_ms=round(elapsed_ms, 2),
            )
            db_session.add(action_rec)
            await db_session.commit()

            return BrowserNavigateResponse(
                session_id=session_id,
                tab_id=target_tab_id,
                url=page.url,
                title=current_title,
                status_code=status_code,
                navigation_time_ms=round(elapsed_ms, 2),
                is_secure_origin=sec_result.scheme == "https",
            )

        except Exception as exc:
            if tab_obj:
                tab_obj.status = BrowserTabStatus.READY
            logger.error(f"Navigation failed for {req.url}: {exc}")
            raise exc

    async def inspect_dom(
        self,
        session_id: str,
        req: DOMInspectionRequest | None = None,
    ) -> DOMInspectionResponse:
        """Inspects and returns a structured, compact DOM tree of interactive elements."""
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not active.")

        tab_id = req.tab_id if req and req.tab_id else (live.tab_manager.active_tab_id or "unknown")
        if req and req.tab_id and req.tab_id in live.tab_manager.tabs:
            page = live.tab_manager.tabs[req.tab_id].page
        else:
            page = live.get_active_page()

        live.touch()
        return await DOMExtractor.inspect(page, session_id=session_id, tab_id=tab_id, request=req)

    async def execute_action(
        self,
        db_session: AsyncSession,
        session_id: str,
        req: BrowserActionRequest,
    ) -> BrowserActionResponse:
        """Executes a single browser action, verifies outcomes, and audits execution."""
        self._check_emergency_stop()
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not active.")

        tab_id = req.tab_id if req.tab_id else (live.tab_manager.active_tab_id or "unknown")
        if req.tab_id and req.tab_id in live.tab_manager.tabs:
            page = live.tab_manager.tabs[req.tab_id].page
        else:
            page = live.get_active_page()

        # If navigate action, validate origin
        if req.action_type == BrowserActionType.NAVIGATE:
            url = req.parameters.get("url", "")
            sec = self.origin_validator.validate_url(url)
            if not sec.is_allowed:
                raise PermissionError(f"Action navigation blocked by security policy: {sec.rejection_reason}")

        pre_url = page.url
        action_resp = await ActionExecutor.execute(page, session_id=session_id, tab_id=tab_id, req=req)

        # Post-action verification
        if action_resp.status == BrowserActionStatus.SUCCEEDED:
            verification = await ActionVerifier.verify(
                page=page,
                action_type=req.action_type,
                target_locator=req.target_locator,
                parameters=req.parameters,
                pre_url=pre_url,
            )
            if action_resp.result is not None:
                action_resp.result["verification"] = verification

        # Update live tab info
        target_tab = live.tab_manager.tabs.get(tab_id)
        if target_tab:
            await target_tab.update_info()

        live.touch()

        # Log action record in database
        action_rec = BrowserActionRecord(
            id=action_resp.id,
            session_id=session_id,
            tab_id=tab_id,
            task_id=None,
            action_type=req.action_type.value,
            target_locator=req.target_locator,
            parameters_json=req.parameters,
            status=action_resp.status.value,
            result_json=action_resp.result,
            error_message=action_resp.error_message,
            screenshot_path=action_resp.screenshot_path,
            started_at=utc_now(),
            completed_at=utc_now(),
            duration_ms=action_resp.duration_ms,
        )
        db_session.add(action_rec)
        await db_session.commit()

        return action_resp

    async def execute_batch_actions(
        self,
        db_session: AsyncSession,
        session_id: str,
        req: BrowserBatchActionsRequest,
    ) -> BrowserBatchActionsResponse:
        """Executes a sequential sequence of browser actions."""
        results: list[BrowserActionResponse] = []
        succeeded = 0
        failed = 0

        for a_req in req.actions:
            if req.tab_id and not a_req.tab_id:
                a_req.tab_id = req.tab_id
            resp = await self.execute_action(db_session, session_id, a_req)
            results.append(resp)
            if resp.status == BrowserActionStatus.SUCCEEDED:
                succeeded += 1
            else:
                failed += 1
                if req.stop_on_failure:
                    break

        return BrowserBatchActionsResponse(
            session_id=session_id,
            total_actions=len(req.actions),
            succeeded_count=succeeded,
            failed_count=failed,
            results=results,
        )

    async def capture_screenshot(
        self,
        session_id: str,
        req: BrowserScreenshotRequest | None = None,
    ) -> BrowserScreenshotResponse:
        """Captures a screenshot of the active or requested tab."""
        live = self.session_manager.get_live_session(session_id)
        if not live:
            raise ValueError(f"Session {session_id} is not active.")

        tab_id = req.tab_id if req and req.tab_id else (live.tab_manager.active_tab_id or "unknown")
        if req and req.tab_id and req.tab_id in live.tab_manager.tabs:
            page = live.tab_manager.tabs[req.tab_id].page
        else:
            page = live.get_active_page()

        live.touch()
        return await self.screenshot_manager.capture(page, session_id=session_id, tab_id=tab_id, req=req)

    async def create_profile(
        self, db_session: AsyncSession, req: BrowserProfileCreateRequest
    ) -> BrowserProfileResponse:
        """Creates a new browser profile."""
        return await self.profile_service.create_profile(db_session, req)

    async def list_profiles(self, db_session: AsyncSession) -> list[BrowserProfileResponse]:
        """Lists available browser profiles."""
        return await self.profile_service.list_profiles(db_session)

    async def list_downloads(self, db_session: AsyncSession) -> list[BrowserDownloadResponse]:
        """Lists recent downloads across sessions."""
        return await self.download_manager.list_downloads(db_session)

    async def create_task(
        self, db_session: AsyncSession, req: BrowserTaskCreateRequest
    ) -> BrowserTaskResponse:
        """Registers a new autonomous browsing task."""
        self._check_emergency_stop()
        task_id = str(uuid4())
        task_rec = BrowserTaskRecord(
            id=task_id,
            workflow_id=req.workflow_id,
            step_id=req.step_id,
            agent_id="browser_agent",
            session_id=req.session_id,
            goal=req.goal,
            status=BrowserTaskStatus.PENDING.value,
            current_step=0,
            total_steps=req.max_steps,
            result_json=None,
            error_message=None,
            created_at=utc_now(),
            started_at=None,
            completed_at=None,
        )
        db_session.add(task_rec)
        await db_session.commit()
        await db_session.refresh(task_rec)

        return self._to_task_response(task_rec)

    async def list_tasks(self, db_session: AsyncSession) -> list[BrowserTaskResponse]:
        """Lists browser automation tasks."""
        stmt = select(BrowserTaskRecord).order_by(BrowserTaskRecord.created_at.desc()).limit(50)
        res = await db_session.execute(stmt)
        records = res.scalars().all()
        return [self._to_task_response(r) for r in records]

    def _to_task_response(self, r: BrowserTaskRecord) -> BrowserTaskResponse:
        return BrowserTaskResponse(
            id=r.id,
            agent_id=r.agent_id,
            session_id=r.session_id,
            workflow_id=r.workflow_id,
            step_id=r.step_id,
            goal=r.goal,
            status=BrowserTaskStatus(r.status) if r.status in BrowserTaskStatus._value2member_map_ else BrowserTaskStatus.PENDING,
            current_step=r.current_step,
            total_steps=r.total_steps,
            result=r.result_json,
            error_message=r.error_message,
            created_at=r.created_at,
            started_at=r.started_at,
            completed_at=r.completed_at,
        )
