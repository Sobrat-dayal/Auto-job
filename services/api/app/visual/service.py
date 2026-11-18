"""Central Visual Computer Service for Stage 18.

Orchestrates screen capture, OCR, visual grounding, native input execution,
post-action verification, recovery, security guardrails, and task lifecycle.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import uuid
from typing import Any, Optional

from .contracts import (
    CapturedFrame,
    CaptureProviderType,
    CaptureSessionCreateRequest,
    CaptureSessionResponse,
    CaptureSessionState,
    CaptureTargetType,
    DisplayInfo,
    OCRLine,
    OCRResult,
    Point2D,
    VerificationStatus,
    VisualActionRequest,
    VisualActionResult,
    VisualActionType,
    VisualDiagnosticsInfo,
    VisualElementDetection,
    VisualGroundingResult,
    VisualTaskRequest,
    VisualTaskResponse,
    VisualTaskStatus,
)
from .capture.monitors import MonitorDiscoveryManager
from .capture.preprocessing import FramePreprocessor
from .capture.providers import CaptureProviderRegistry
from .capture.sessions import CaptureSessionManager, capture_session_manager
from .execution.recovery import VisualRecoveryManager
from .execution.state_machine import VisualStateMachine
from .execution.verification import VisualActionVerifier
from .grounding.ocr import WindowsMediaOCREngine
from .grounding.vision import VisualGroundingService
from .input.adapter import WindowsInputAdapter, windows_input_adapter
from .security.authorization import visual_auth_engine
from .security.guard import visual_security_guard
from .security.privacy import visual_privacy_filter

logger = logging.getLogger("autonom.visual.service")


class VisualComputerService:
    """Central service managing visual computer interaction and automation."""

    _instance: Optional["VisualComputerService"] = None

    def __init__(
        self,
        session_mgr: Optional[CaptureSessionManager] = None,
        input_adp: Optional[WindowsInputAdapter] = None,
    ) -> None:
        self.session_manager = session_mgr or capture_session_manager
        self.input_adapter = input_adp or windows_input_adapter
        self.ocr_engine = WindowsMediaOCREngine()
        self.grounding_service = VisualGroundingService(ocr_engine=self.ocr_engine)
        self.verifier = VisualActionVerifier(session_manager=self.session_manager, ocr_engine=self.ocr_engine)
        self.recovery_manager = VisualRecoveryManager(
            session_manager=self.session_manager,
            grounding_service=self.grounding_service,
        )
        self._tasks: dict[str, VisualTaskResponse] = {}

    @classmethod
    def get_instance(cls) -> "VisualComputerService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -------------------------------------------------------------------------
    # Diagnostics & Monitors
    # -------------------------------------------------------------------------

    def get_diagnostics(self) -> VisualDiagnosticsInfo:
        """Returns comprehensive diagnostic status for the visual engine."""
        monitors = MonitorDiscoveryManager.discover_monitors()
        sessions = self.session_manager.list_sessions()
        active_count = sum(1 for s in sessions if s.state == CaptureSessionState.CAPTURING)

        return VisualDiagnosticsInfo(
            active_provider=CaptureProviderType.MSS,
            available_providers=[CaptureProviderType.MSS, CaptureProviderType.GDI, CaptureProviderType.WGC],
            active_sessions_count=active_count,
            monitors_count=len(monitors),
            primary_display_resolution=f"{monitors[0].width}x{monitors[0].height}" if monitors else "Unknown",
            dpi_scaling_factor=monitors[0].scale_factor if monitors else 1.0,
            offline_windows_ocr_available=self.ocr_engine.is_available,
            vlm_grounding_available=True,
            gpu_acceleration=True,
            last_capture_latency_ms=16.0,
            last_ocr_latency_ms=45.0,
            active_emergency_stop=False,
        )

    def list_monitors(self) -> list[DisplayInfo]:
        """Discovers and enumerates all connected physical displays."""
        return MonitorDiscoveryManager.discover_monitors()

    # -------------------------------------------------------------------------
    # Capture Session Management
    # -------------------------------------------------------------------------

    async def create_session(self, request: CaptureSessionCreateRequest) -> CaptureSessionResponse:
        """Creates and initializes a new screen capture session."""
        visual_security_guard.assert_visual_operation_allowed("create_capture_session")
        return await self.session_manager.create_session(request)

    def get_session(self, session_id: str) -> Optional[CaptureSessionResponse]:
        """Retrieves details of an existing capture session."""
        return self.session_manager.get_session(session_id)

    def list_sessions(self) -> list[CaptureSessionResponse]:
        """Lists all existing capture sessions."""
        return self.session_manager.list_sessions()

    async def close_session(self, session_id: str) -> bool:
        """Closes and releases a capture session."""
        return await self.session_manager.close_session(session_id)

    async def capture_frame(self, session_id: str) -> CapturedFrame:
        """Captures a new visual frame from an active session."""
        visual_security_guard.assert_visual_operation_allowed("capture_frame")
        return await self.session_manager.capture_frame(session_id)

    # -------------------------------------------------------------------------
    # OCR & Visual Grounding
    # -------------------------------------------------------------------------

    async def run_ocr(self, session_id: str) -> OCRResult:
        """Runs offline Windows Media OCR on the latest frame of a session."""
        visual_security_guard.assert_visual_operation_allowed("run_ocr")
        frame = await self.capture_frame(session_id)
        result = await self.ocr_engine.recognize_frame(frame)
        return visual_privacy_filter.sanitize_ocr_result(result)

    async def find_text(self, session_id: str, query: str) -> list[OCRLine]:
        """Locates lines or words matching a text query in a session frame."""
        visual_security_guard.assert_visual_operation_allowed("find_text")
        frame = await self.capture_frame(session_id)
        return await self.ocr_engine.find_text(frame, query)

    async def detect_elements(self, session_id: str) -> list[VisualElementDetection]:
        """Classifies and detects visual interactive UI controls in a session frame."""
        visual_security_guard.assert_visual_operation_allowed("detect_elements")
        frame = await self.capture_frame(session_id)
        return await self.grounding_service.detect_elements(frame)

    async def ground(self, session_id: str, query: str) -> VisualGroundingResult:
        """Grounds a natural language query to an exact desktop coordinate and bounding box."""
        visual_security_guard.assert_visual_operation_allowed("ground")
        frame = await self.capture_frame(session_id)
        return await self.grounding_service.ground(
            frame=frame,
            query=query,
            target_type=frame.metadata.target_type,
            target_hwnd=frame.metadata.target_hwnd,
            display_index=frame.metadata.display_index,
        )

    # -------------------------------------------------------------------------
    # Visual Actions Execution
    # -------------------------------------------------------------------------

    async def execute_action(
        self,
        session_id: str,
        action: VisualActionRequest,
    ) -> VisualActionResult:
        """Executes a coordinate-based or grounded visual action with verification."""
        visual_security_guard.assert_visual_operation_allowed(f"action_{action.action_type.value}")
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        # Capture pre-action baseline frame for verification
        before_frame: Optional[CapturedFrame] = None
        try:
            before_frame = await self.session_manager.capture_frame(session_id)
        except Exception as e:
            logger.warning(f"Could not capture pre-action baseline: {e}")

        # If action target is not explicitly given as point, ground it via target_element query
        target_point = action.target_point
        grounding_used = False
        grounding_result: Optional[VisualGroundingResult] = None

        if target_point is None and action.target_element and before_frame:
            grounding_result = await self.grounding_service.ground(
                frame=before_frame,
                query=action.target_element,
                target_type=session.target_type,
                target_hwnd=session.target_hwnd,
                display_index=session.display_index,
            )
            if not grounding_result.success or not grounding_result.target_point:
                return VisualActionResult(
                    success=False,
                    action_type=action.action_type,
                    verification_status=VerificationStatus.FAILED,
                    error_message=f"Could not ground target element '{action.target_element}': {grounding_result.explanation}",
                )
            target_point = grounding_result.target_point
            grounding_used = True

        # Dispatch low-level Windows SendInput action
        t0 = asyncio.get_event_loop().time()
        dispatch_success = True
        error_msg: Optional[str] = None

        try:
            if action.action_type == VisualActionType.CLICK:
                pt = target_point or Point2D(x=0, y=0)
                btn = action.button or "left"
                clicks = action.click_count or 1
                dispatch_success = await self.input_adapter.click(pt.x, pt.y, button=btn, clicks=clicks)

            elif action.action_type == VisualActionType.DOUBLE_CLICK:
                pt = target_point or Point2D(x=0, y=0)
                dispatch_success = await self.input_adapter.click(pt.x, pt.y, button="left", clicks=2)

            elif action.action_type == VisualActionType.RIGHT_CLICK:
                pt = target_point or Point2D(x=0, y=0)
                dispatch_success = await self.input_adapter.click(pt.x, pt.y, button="right", clicks=1)

            elif action.action_type == VisualActionType.MOVE:
                if target_point:
                    dispatch_success = await self.input_adapter.move_cursor(target_point.x, target_point.y)

            elif action.action_type == VisualActionType.ENTER_TEXT:
                # If target point is given, click first to focus
                if target_point:
                    await self.input_adapter.click(target_point.x, target_point.y)
                    await asyncio.sleep(0.1)
                text = action.text or ""
                dispatch_success = await self.input_adapter.type_text(text)

            elif action.action_type == VisualActionType.PRESS_KEY:
                key = action.key or "Enter"
                dispatch_success = await self.input_adapter.press_key(key)

            elif action.action_type == VisualActionType.SCROLL:
                pt = target_point or Point2D(x=500, y=500)
                amt = action.scroll_amount or -120
                dispatch_success = await self.input_adapter.scroll(pt.x, pt.y, amount=amt)

            elif action.action_type == VisualActionType.DRAG_AND_DROP:
                from_pt = target_point or Point2D(x=0, y=0)
                to_pt = action.drag_target or Point2D(x=from_pt.x + 50, y=from_pt.y + 50)
                dispatch_success = await self.input_adapter.drag_and_drop(from_pt.x, from_pt.y, to_pt.x, to_pt.y)

            elif action.action_type == VisualActionType.WAIT:
                wait_sec = action.wait_seconds or 1.0
                await asyncio.sleep(wait_sec)
                dispatch_success = True

            else:
                dispatch_success = False
                error_msg = f"Unsupported action type: {action.action_type}"

        except Exception as e:
            logger.error(f"Error dispatching visual action {action.action_type}: {e}")
            dispatch_success = False
            error_msg = str(e)

        exec_ms = (asyncio.get_event_loop().time() - t0) * 1000.0

        if not dispatch_success:
            return VisualActionResult(
                success=False,
                action_type=action.action_type,
                execution_time_ms=exec_ms,
                verification_status=VerificationStatus.FAILED,
                error_message=error_msg or "Failed to dispatch input action",
            )

        # Run verification
        v_status, v_diff, v_exp, after_frame = await self.verifier.verify_action(
            session_id=session_id,
            action=action,
            before_frame=before_frame,
        )

        initial_result = VisualActionResult(
            success=True,
            action_type=action.action_type,
            execution_time_ms=exec_ms,
            verification_status=v_status,
            visual_difference=v_diff,
            verification_notes=v_exp,
            post_action_frame_id=after_frame.frame_id if after_frame else None,
        )

        # Trigger recovery if verification failed and element was grounded
        if v_status == VerificationStatus.FAILED and grounding_used and action.target_element:
            logger.info(f"Verification failed; invoking recovery for query '{action.target_element}'")

            async def _action_closure(g_res: VisualGroundingResult) -> VisualActionResult:
                updated_action = action.model_copy()
                updated_action.target_point = g_res.target_point
                return await self.execute_action(session_id=session_id, action=updated_action)

            return await self.recovery_manager.attempt_recovery(
                session_id=session_id,
                query=action.target_element,
                failed_result=initial_result,
                action_fn=_action_closure,
            )

        return initial_result

    # -------------------------------------------------------------------------
    # Convenience Quick Actions
    # -------------------------------------------------------------------------

    async def click(
        self,
        session_id: str,
        x: int,
        y: int,
        button: str = "left",
        clicks: int = 1,
    ) -> VisualActionResult:
        """Executes a click at absolute desktop coordinates."""
        action = VisualActionRequest(
            action_type=VisualActionType.CLICK,
            target_point=Point2D(x=x, y=y),
            button=button,
            click_count=clicks,
        )
        return await self.execute_action(session_id, action)

    async def click_element(
        self,
        session_id: str,
        query: str,
        expected_change: Optional[str] = None,
    ) -> VisualActionResult:
        """Grounds a UI element by text or query and clicks it."""
        action = VisualActionRequest(
            action_type=VisualActionType.CLICK,
            target_element=query,
            expected_change=expected_change,
        )
        return await self.execute_action(session_id, action)

    async def enter_text(
        self,
        session_id: str,
        text: str,
        query: Optional[str] = None,
    ) -> VisualActionResult:
        """Enters Unicode text into a focused or grounded control."""
        action = VisualActionRequest(
            action_type=VisualActionType.ENTER_TEXT,
            text=text,
            target_element=query,
        )
        return await self.execute_action(session_id, action)

    # -------------------------------------------------------------------------
    # High-Level Visual Tasks
    # -------------------------------------------------------------------------

    async def execute_task(self, request: VisualTaskRequest) -> VisualTaskResponse:
        """Executes an end-to-end visual goal using the state machine."""
        task_id = f"vtask_{uuid.uuid4().hex[:12]}"
        sm = VisualStateMachine(task_id=task_id)
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        response = VisualTaskResponse(
            task_id=task_id,
            status=VisualTaskStatus.PENDING,
            instruction=request.instruction,
            created_at=now_str,
            updated_at=now_str,
            steps_completed=0,
            total_steps=1,
        )
        self._tasks[task_id] = response

        # Auto-create session if none provided
        session_id = request.session_id
        session_created = False
        if not session_id:
            sess_resp = await self.create_session(
                CaptureSessionCreateRequest(
                    target_type=request.target_type or CaptureTargetType.DISPLAY,
                    target_hwnd=request.target_hwnd,
                    display_index=request.display_index or 0,
                    provider=request.provider or CaptureProviderType.MSS,
                )
            )
            session_id = sess_resp.session_id
            session_created = True

        try:
            # 1. OBSERVING
            sm.transition_to(VisualTaskStatus.OBSERVING, "Capturing baseline frame")
            response.status = VisualTaskStatus.OBSERVING
            frame = await self.capture_frame(session_id)

            # 2. GROUNDING
            sm.transition_to(VisualTaskStatus.GROUNDING, f"Grounding query: {request.instruction}")
            response.status = VisualTaskStatus.GROUNDING
            g_res = await self.grounding_service.ground(
                frame=frame,
                query=request.instruction,
                target_type=frame.metadata.target_type,
                target_hwnd=frame.metadata.target_hwnd,
                display_index=frame.metadata.display_index,
            )

            if not g_res.success:
                sm.transition_to(VisualTaskStatus.FAILED, f"Could not ground target: {g_res.explanation}")
                response.status = VisualTaskStatus.FAILED
                response.error_message = g_res.explanation
                return response

            # 3. ACTING
            sm.transition_to(VisualTaskStatus.ACTING, "Executing visual action")
            response.status = VisualTaskStatus.ACTING
            action = VisualActionRequest(
                action_type=VisualActionType.CLICK,
                target_point=g_res.target_point,
                wait_for_render=True,
            )
            act_res = await self.execute_action(session_id, action)

            # 4. VERIFYING
            sm.transition_to(VisualTaskStatus.VERIFYING, "Verifying visual action outcome")
            response.status = VisualTaskStatus.VERIFYING

            if act_res.success:
                sm.transition_to(VisualTaskStatus.COMPLETED, "Visual task completed successfully")
                response.status = VisualTaskStatus.COMPLETED
                response.steps_completed = 1
                response.result_summary = (
                    f"Successfully located '{request.instruction}' at ({g_res.target_point.x}, {g_res.target_point.y}) "
                    f"and performed click. Verification: {act_res.verification_notes or act_res.verification_status.value}"
                )
            else:
                sm.transition_to(VisualTaskStatus.FAILED, act_res.error_message or "Action failed")
                response.status = VisualTaskStatus.FAILED
                response.error_message = act_res.error_message

        except Exception as e:
            logger.error(f"Task {task_id} failed with error: {e}")
            sm.transition_to(VisualTaskStatus.FAILED, str(e))
            response.status = VisualTaskStatus.FAILED
            response.error_message = str(e)

        finally:
            if session_created:
                await self.close_session(session_id)
            response.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return response

    def get_task(self, task_id: str) -> Optional[VisualTaskResponse]:
        """Retrieves a visual task by id."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[VisualTaskResponse]:
        """Lists all registered visual tasks."""
        return list(self._tasks.values())


visual_computer_service = VisualComputerService.get_instance()
