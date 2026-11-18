"""Action dispatcher and execution engine for Windows desktop operations (Stage 17)."""

from datetime import UTC, datetime
import logging
import time
from uuid import uuid4

from app.computer.actions.keyboard import focused_keyboard
from app.computer.actions.verifier import action_verifier
from app.computer.contracts import DesktopActionRequest, DesktopActionResult, DesktopActionType, WindowManageAction
from app.computer.uia.locators import locator_resolver
from app.computer.uia.patterns import pattern_executor
from app.computer.win32.adapter import win32_adapter
from app.computer.windows.focus import focus_manager
from app.computer.windows.management import window_state_manager
from app.computer.windows.windows import window_discovery_manager

logger = logging.getLogger("autonom.computer.actions.executor")


class ActionExecutor:
    """Dispatches typed structural desktop actions to UIA patterns, Win32 adapters, or focused keyboard."""

    @classmethod
    def execute_action(cls, request: DesktopActionRequest) -> DesktopActionResult:
        """Executes a desktop action with window validation and structural post-action verification."""
        start_time = time.perf_counter()
        action_id = f"act_{uuid4().hex[:12]}"

        # 1. Validate target window
        win = window_discovery_manager.validate_window_ref(request.window_ref)
        if not win:
            return DesktopActionResult(
                action_id=action_id,
                action_type=request.action_type.value,
                status="failed",
                verification_status="failed",
                duration_ms=(time.perf_counter() - start_time) * 1000,
                error_message=f"Target window reference invalid or window has closed: {request.window_ref}",
                executed_at=datetime.now(UTC),
            )

        hwnd = win.hwnd
        result_data: dict = {}
        error_msg: str | None = None
        status = "succeeded"
        target_com_element = None

        try:
            # Window management actions
            if request.action_type == DesktopActionType.ACTIVATE_WINDOW:
                success = focus_manager.activate_window(hwnd)
                result_data["activated"] = success

            elif request.action_type == DesktopActionType.CLOSE_WINDOW:
                success = window_state_manager.execute_window_action(request.window_ref, WindowManageAction.CLOSE)
                result_data["closed"] = success

            elif request.action_type == DesktopActionType.GET_WINDOW_STATE:
                result_data["window"] = win.model_dump()

            elif request.action_type == DesktopActionType.PRESS_KEY:
                if not request.key:
                    raise ValueError("Key parameter must be specified for PRESS_KEY action")
                success = focused_keyboard.send_key_to_window(hwnd, request.key, request.modifiers)
                result_data["key_sent"] = success

            # Element-based actions
            else:
                # Resolve target element
                if request.locator:
                    res = locator_resolver.resolve_single_element(hwnd, request.window_ref, request.locator)
                    if not res:
                        raise ValueError(f"No UI element found matching locator criteria: {request.locator.model_dump()}")
                    target_com_element, el_info = res
                    result_data["target_element"] = el_info.model_dump()
                else:
                    raise ValueError("Element locator must be provided for element-based actions")

                if request.action_type == DesktopActionType.INVOKE:
                    try:
                        pattern_executor.invoke(target_com_element)
                        result_data["invoked"] = True
                    except Exception as e:
                        # Fallback to Win32 click if it's a window control
                        logger.debug(f"UIA invoke failed, trying Win32 fallback: {e}")
                        win32_adapter.click_button(hwnd)
                        result_data["invoked_win32_fallback"] = True

                elif request.action_type == DesktopActionType.SET_VALUE:
                    text_to_set = str(request.value or "")
                    try:
                        pattern_executor.set_value(target_com_element, text_to_set)
                        result_data["set_value"] = text_to_set
                    except Exception as e:
                        logger.debug(f"UIA set_value failed, trying keyboard fallback: {e}")
                        focused_keyboard.send_text_to_window(hwnd, text_to_set)
                        result_data["set_value_keyboard_fallback"] = text_to_set

                elif request.action_type == DesktopActionType.READ_TEXT:
                    text_val = pattern_executor.get_value(target_com_element)
                    result_data["text"] = text_val

                elif request.action_type == DesktopActionType.TOGGLE:
                    new_state = pattern_executor.toggle(target_com_element)
                    result_data["toggle_state"] = new_state

                elif request.action_type == DesktopActionType.SELECT:
                    pattern_executor.select(target_com_element)
                    result_data["selected"] = True

                elif request.action_type == DesktopActionType.EXPAND:
                    pattern_executor.expand(target_com_element)
                    result_data["expanded"] = True

                elif request.action_type == DesktopActionType.COLLAPSE:
                    pattern_executor.collapse(target_com_element)
                    result_data["collapsed"] = True

                elif request.action_type == DesktopActionType.SCROLL:
                    pattern_executor.scroll(target_com_element, vertical_percent=1.0)
                    result_data["scrolled"] = True

        except Exception as e:
            status = "failed"
            error_msg = str(e)
            logger.error(f"Action execution error: {e}")

        # Verification step
        verification_status = "skipped"
        if status == "succeeded" and request.verify:
            verification_status, v_evidence = action_verifier.verify_action_result(
                request.action_type,
                hwnd,
                target_com_element,
                request.value,
            )
            result_data["verification_evidence"] = v_evidence

        duration_ms = (time.perf_counter() - start_time) * 1000

        return DesktopActionResult(
            action_id=action_id,
            action_type=request.action_type.value,
            status=status,
            verification_status=verification_status,
            duration_ms=duration_ms,
            result_data=result_data,
            error_message=error_msg,
            executed_at=datetime.now(UTC),
        )


action_executor = ActionExecutor()
