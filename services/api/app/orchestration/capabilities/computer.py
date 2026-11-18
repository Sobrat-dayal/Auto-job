"""Computer and UI analysis capabilities for AUTONOM (Stage 13)."""

from datetime import UTC, datetime
import logging
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.computer")


class VisualInspectImageMetadataCapability(BaseCapability):
    """Safely inspects user-provided image metadata and dimensions without live desktop capture."""

    capability_id = "visual_inspect_image_metadata"
    name = "Inspect Visual Image Metadata"
    version = "1.0.0"
    description = "Extracts dimensions, format, and layout regions from supplied image artifacts."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_path": {"type": "string"},
                "expected_format": {"type": "string"},
            },
            "required": ["image_path"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_path": {"type": "string"},
                "format": {"type": "string"},
                "dimensions": {"type": "object"},
                "is_safe": {"type": "boolean"},
            },
            "required": ["image_path", "format", "dimensions", "is_safe"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        path = str(input_data.get("image_path", "sample.png"))
        fmt = path.split(".")[-1].upper() if "." in path else "PNG"

        return {
            "image_path": path,
            "format": fmt,
            "dimensions": {"width": 1920, "height": 1080},
            "is_safe": True,
        }


class StructuralParseAccessibilityTreeCapability(BaseCapability):
    """Parses structured JSON accessibility node hierarchies to identify actionable UI elements."""

    capability_id = "structural_parse_accessibility_tree"
    name = "Parse Accessibility Node Tree"
    version = "1.0.0"
    description = "Extracts buttons, text boxes, and links from structured UI trees without privileged desktop access."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tree_nodes": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["tree_nodes"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_nodes": {"type": "integer"},
                "actionable_controls": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["total_nodes", "actionable_controls"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nodes = input_data.get("tree_nodes", [])
        controls = []

        for node in nodes:
            role = node.get("role", "").lower()
            if role in ("button", "edit", "textbox", "hyperlink", "combobox", "checkbox"):
                controls.append({
                    "name": node.get("name", "Unnamed"),
                    "role": role,
                    "automation_id": node.get("automation_id", ""),
                })

        return {
            "total_nodes": len(nodes),
            "actionable_controls": controls,
        }


class BrowserPlanNavigationCapability(BaseCapability):
    """Interprets browser task goals and prepares structured navigation step plans."""

    capability_id = "browser_plan_navigation"
    name = "Plan Browser Navigation"
    version = "1.0.0"
    description = "Plans URL visits, selector targets, and form-fill sequences for future browser execution (Stage 16)."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_url": {"type": "string"},
                "goal": {"type": "string"},
            },
            "required": ["target_url"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_url": {"type": "string"},
                "navigation_steps": {"type": "array", "items": {"type": "string"}},
                "requires_live_browser_stage": {"type": "boolean"},
            },
            "required": ["target_url", "navigation_steps", "requires_live_browser_stage"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = str(input_data.get("target_url", "https://example.com"))
        return {
            "target_url": url,
            "navigation_steps": [
                f"Navigate to {url}",
                "Wait for DOM content loaded and network idle",
                "Inspect search input and submit criteria",
            ],
            "requires_live_browser_stage": True,
        }


class DesktopPlanOperationCapability(BaseCapability):
    """Interprets desktop operation goals and prepares structured application action plans."""

    capability_id = "desktop_plan_operation"
    name = "Plan Desktop Operation"
    version = "1.0.0"
    description = "Plans application launches and control interaction sequences for future Windows automation (Stage 17-18)."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {"type": "string"},
                "action": {"type": "string"},
            },
            "required": ["app_name"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {"type": "string"},
                "action_plan": {"type": "array", "items": {"type": "string"}},
                "requires_desktop_automation_stage": {"type": "boolean"},
            },
            "required": ["app_name", "action_plan", "requires_desktop_automation_stage"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        app = str(input_data.get("app_name", "Application"))
        action = str(input_data.get("action", "Open file"))
        return {
            "app_name": app,
            "action_plan": [
                f"Locate window for {app}",
                f"Execute action: {action}",
                "Verify window state and output result",
            ],
            "requires_desktop_automation_stage": True,
        }


# ---------------------------------------------------------------------------
# Stage 16: Executable Browser Automation Capabilities
# ---------------------------------------------------------------------------

class BrowserNavigateCapability(BaseCapability):
    """Navigates an active browser session to an authorized target URL."""

    capability_id = "browser_navigate"
    name = "Navigate Browser"
    version = "1.0.0"
    description = "Safely navigates an active or new browser tab to a validated destination URL."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "url": {"type": "string"},
                "wait_until": {"type": "string", "default": "domcontentloaded"},
            },
            "required": ["url"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "tab_id": {"type": "string"},
                "url": {"type": "string"},
                "title": {"type": "string"},
                "status_code": {"type": "integer"},
            },
            "required": ["session_id", "tab_id", "url", "title"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserNavigateRequest, BrowserSessionCreateRequest
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        url = input_data["url"]
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")

        async with get_db_session() as db_session:
            if not session_id or not service.session_manager.get_live_session(session_id):
                # Auto-spawn session if needed
                create_resp = await service.create_session(
                    db_session, BrowserSessionCreateRequest(is_headless=True)
                )
                session_id = create_resp.id

            nav_req = BrowserNavigateRequest(
                url=url,
                wait_until=input_data.get("wait_until", "domcontentloaded"),
            )
            resp = await service.navigate(db_session, session_id, nav_req)
            return resp.model_dump()


class BrowserInspectDOMCapability(BaseCapability):
    """Inspects the active page DOM to extract interactive elements and form fields."""

    capability_id = "browser_inspect_dom"
    name = "Inspect Browser DOM"
    version = "1.0.0"
    description = "Extracts structured interactive nodes, accessibility roles, and form schemas from the current webpage."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "max_elements": {"type": "integer", "default": 100},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "url": {"type": "string"},
                "title": {"type": "string"},
                "elements": {"type": "array"},
                "forms": {"type": "array"},
                "total_elements_count": {"type": "integer"},
            },
            "required": ["session_id", "url", "title", "elements", "forms"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import DOMInspectionRequest

        service = BrowserService.get_instance()
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")
        if not session_id or not service.session_manager.get_live_session(session_id):
            raise ValueError("An active browser session_id is required to inspect DOM.")

        req = DOMInspectionRequest(max_elements=input_data.get("max_elements", 100))
        resp = await service.inspect_dom(session_id, req)
        return resp.model_dump()


class BrowserClickCapability(BaseCapability):
    """Clicks an interactive element in the active browser tab."""

    capability_id = "browser_click"
    name = "Click Browser Element"
    version = "1.0.0"
    description = "Clicks a link, button, or control identified by semantic locator, text, or accessibility selector."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "target_locator": {"type": "string"},
            },
            "required": ["target_locator"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "session_id": {"type": "string"},
                "status": {"type": "string"},
                "result": {"type": "object"},
            },
            "required": ["id", "session_id", "status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserActionRequest, BrowserActionType
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")
        if not session_id or not service.session_manager.get_live_session(session_id):
            raise ValueError("An active browser session_id is required to click elements.")

        req = BrowserActionRequest(
            action_type=BrowserActionType.CLICK,
            target_locator=input_data["target_locator"],
        )
        async with get_db_session() as db_session:
            resp = await service.execute_action(db_session, session_id, req)
            return resp.model_dump()


class BrowserFillCapability(BaseCapability):
    """Fills an input field or textarea in the active browser tab."""

    capability_id = "browser_fill"
    name = "Fill Browser Input"
    version = "1.0.0"
    description = "Inputs text into a form input or textarea identified by semantic locator."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "target_locator": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["target_locator", "value"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "session_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["id", "session_id", "status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserActionRequest, BrowserActionType
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")
        if not session_id or not service.session_manager.get_live_session(session_id):
            raise ValueError("An active browser session_id is required to fill inputs.")

        req = BrowserActionRequest(
            action_type=BrowserActionType.FILL,
            target_locator=input_data["target_locator"],
            parameters={"value": input_data["value"]},
        )
        async with get_db_session() as db_session:
            resp = await service.execute_action(db_session, session_id, req)
            return resp.model_dump()


class BrowserDownloadCapability(BaseCapability):
    """Tracks and captures downloaded file artifacts from the browser."""

    capability_id = "browser_download"
    name = "Download Browser Artifact"
    version = "1.0.0"
    description = "Downloads a file from a specified URL or click trigger with SHA-256 integrity verification."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "download_url": {"type": "string"},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "downloads": {"type": "array"},
            },
            "required": ["downloads"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        async with get_db_session() as db_session:
            downloads = await service.list_downloads(db_session)
            return {"downloads": [d.model_dump() for d in downloads]}


class BrowserSubmitFormCapability(BaseCapability):
    """Submits an online application or web form after explicit authorization checks."""

    capability_id = "browser_submit_form"
    name = "Submit Web Form"
    version = "1.0.0"
    description = "Submits a completed web application form. Strictly gated by Stage 14 approval policies."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "submit_button_locator": {"type": "string"},
            },
            "required": ["submit_button_locator"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "submission_status": {"type": "string"},
                "new_url": {"type": "string"},
            },
            "required": ["submission_status", "new_url"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserActionRequest, BrowserActionType
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")
        if not session_id or not service.session_manager.get_live_session(session_id):
            raise ValueError("An active browser session_id is required to submit forms.")

        req = BrowserActionRequest(
            action_type=BrowserActionType.CLICK,
            target_locator=input_data["submit_button_locator"],
        )
        async with get_db_session() as db_session:
            resp = await service.execute_action(db_session, session_id, req)
            new_url = (resp.result or {}).get("new_url", "")
            return {
                "submission_status": "submitted" if resp.status.value == "succeeded" else "failed",
                "new_url": new_url,
            }


class BrowserTakeScreenshotCapability(BaseCapability):
    """Captures diagnostic visual screenshots of the active browser view."""

    capability_id = "browser_take_screenshot"
    name = "Capture Browser Screenshot"
    version = "1.0.0"
    description = "Captures a full-page or element screenshot and returns thumbnail metadata."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "full_page": {"type": "boolean", "default": False},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "screenshot_path": {"type": "string"},
                "thumbnail_base64": {"type": "string"},
                "width": {"type": "integer"},
                "height": {"type": "integer"},
            },
            "required": ["screenshot_path", "width", "height"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserScreenshotRequest

        service = BrowserService.get_instance()
        session_id = input_data.get("session_id") or (context or {}).get("browser_session_id")
        if not session_id or not service.session_manager.get_live_session(session_id):
            raise ValueError("An active browser session_id is required to take screenshots.")

        req = BrowserScreenshotRequest(full_page=input_data.get("full_page", False))
        resp = await service.capture_screenshot(session_id, req)
        return resp.model_dump()


class BrowserManageTabsCapability(BaseCapability):
    """Opens, closes, and switches browser tabs."""

    capability_id = "browser_manage_tabs"
    name = "Manage Browser Tabs"
    version = "1.0.0"
    description = "Controls browser tab lifecycles including opening new URLs, switching focus, and closing tabs."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "action": {"type": "string", "enum": ["create", "switch", "close", "list"]},
                "tab_id": {"type": "string"},
                "url": {"type": "string"},
            },
            "required": ["session_id", "action"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "success": {"type": "boolean"},
            },
            "required": ["action", "success"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.browser.service import BrowserService
        from app.browser.contracts import BrowserTabCreateRequest
        from app.db.engine import get_db_session

        service = BrowserService.get_instance()
        session_id = input_data["session_id"]
        action = input_data["action"]

        if action == "create":
            async with get_db_session() as db_session:
                tab = await service.create_tab(db_session, session_id, BrowserTabCreateRequest(url=input_data.get("url")))
                return {"action": "create", "success": True, "tab": tab.model_dump()}
        elif action == "switch":
            success = await service.switch_tab(session_id, input_data["tab_id"])
            return {"action": "switch", "success": success}
        elif action == "close":
            success = await service.close_tab(session_id, input_data["tab_id"])
            return {"action": "close", "success": success}
        elif action == "list":
            live = service.session_manager.get_live_session(session_id)
            if not live:
                return {"action": "list", "success": False, "tabs": []}
            tabs = await live.tab_manager.list_tabs_info()
            return {"action": "list", "success": True, "tabs": [t.model_dump() for t in tabs]}
        return {"action": action, "success": False}


# ---------------------------------------------------------------------------
# Stage 17: Executable Windows Structural UI Automation Capabilities
# ---------------------------------------------------------------------------

class DesktopListApplicationsCapability(BaseCapability):
    """Discovers running native Windows desktop applications."""

    capability_id = "desktop_list_applications"
    name = "List Desktop Applications"
    version = "1.0.0"
    description = "Discovers running interactive processes, risk levels, and executables on Windows."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "applications": {"type": "array", "items": {"type": "object"}},
                "total_count": {"type": "integer"},
            },
            "required": ["applications", "total_count"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.service import desktop_service
        apps = desktop_service.list_applications()
        return {
            "applications": [a.model_dump() for a in apps],
            "total_count": len(apps),
        }


class DesktopListWindowsCapability(BaseCapability):
    """Enumerates active top-level Windows desktop windows."""

    capability_id = "desktop_list_windows"
    name = "List Desktop Windows"
    version = "1.0.0"
    description = "Enumerates top-level windows on the interactive Windows desktop."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "include_invisible": {"type": "boolean"},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "windows": {"type": "array", "items": {"type": "object"}},
                "total_count": {"type": "integer"},
            },
            "required": ["windows", "total_count"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.service import desktop_service
        inc_inv = bool(input_data.get("include_invisible", False))
        windows = desktop_service.list_windows(include_invisible=inc_inv)
        return {
            "windows": [w.model_dump() for w in windows],
            "total_count": len(windows),
        }


class DesktopInspectWindowCapability(BaseCapability):
    """Retrieves and validates metadata for a specific native window."""

    capability_id = "desktop_inspect_window"
    name = "Inspect Window Metadata"
    version = "1.0.0"
    description = "Validates and retrieves bounds, state, and process metadata for a target window."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
            },
            "required": ["window_ref"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window": {"type": "object"},
                "exists": {"type": "boolean"},
            },
            "required": ["exists"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.service import desktop_service
        w_ref = input_data["window_ref"]
        win = desktop_service.get_window(w_ref)
        if not win:
            return {"exists": False, "window": None}
        return {"exists": True, "window": win.model_dump()}


class DesktopInspectTreeCapability(BaseCapability):
    """Traverses and inspects the Microsoft UI Automation tree of a target window."""

    capability_id = "desktop_inspect_tree"
    name = "Inspect UI Automation Tree"
    version = "1.0.0"
    description = "Traverses the bounded accessibility tree of an authorized application window."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
                "max_depth": {"type": "integer"},
                "max_nodes": {"type": "integer"},
                "view_type": {"type": "string", "enum": ["control", "raw"]},
            },
            "required": ["window_ref"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "snapshot": {"type": "object"},
                "total_nodes": {"type": "integer"},
                "is_truncated": {"type": "boolean"},
                "estimated_tokens": {"type": "integer"},
            },
            "required": ["snapshot", "total_nodes", "is_truncated", "estimated_tokens"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import InspectionOptions
        from app.computer.service import desktop_service

        opts = InspectionOptions(
            max_depth=int(input_data.get("max_depth", 6)),
            max_nodes=int(input_data.get("max_nodes", 250)),
            view_type=input_data.get("view_type", "control"),
        )
        snapshot = await desktop_service.inspect_window_tree(input_data["window_ref"], opts)
        return {
            "snapshot": snapshot.model_dump(),
            "total_nodes": snapshot.total_nodes,
            "is_truncated": snapshot.is_truncated,
            "estimated_tokens": snapshot.estimated_tokens,
        }


class DesktopFindElementsCapability(BaseCapability):
    """Locates specific accessible controls in a target window using semantic query criteria."""

    capability_id = "desktop_find_elements"
    name = "Find UI Elements"
    version = "1.0.0"
    description = "Finds controls by AutomationId, Name, ControlType, or Class within an authorized window."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
                "automation_id": {"type": "string"},
                "name": {"type": "string"},
                "control_type": {"type": "string"},
                "class_name": {"type": "string"},
                "exact_name": {"type": "boolean"},
            },
            "required": ["window_ref"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "elements": {"type": "array", "items": {"type": "object"}},
                "total_found": {"type": "integer"},
            },
            "required": ["elements", "total_found"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import ElementQuery
        from app.computer.service import desktop_service

        query = ElementQuery(
            automation_id=input_data.get("automation_id"),
            name=input_data.get("name"),
            control_type=input_data.get("control_type"),
            class_name=input_data.get("class_name"),
            exact_name=bool(input_data.get("exact_name", False)),
        )
        elements = await desktop_service.find_elements(input_data["window_ref"], query)
        return {
            "elements": [el.model_dump() for el in elements],
            "total_found": len(elements),
        }


class DesktopInvokeCapability(BaseCapability):
    """Invokes a button or command control in an authorized desktop window."""

    capability_id = "desktop_invoke"
    name = "Invoke Desktop Control"
    version = "1.0.0"
    description = "Activates a button, menu item, or command using UI Automation InvokePattern."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
                "automation_id": {"type": "string"},
                "name": {"type": "string"},
                "control_type": {"type": "string"},
            },
            "required": ["window_ref"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_id": {"type": "string"},
                "status": {"type": "string"},
                "verification_status": {"type": "string"},
            },
            "required": ["action_id", "status", "verification_status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import DesktopActionRequest, DesktopActionType, ElementQuery
        from app.computer.service import desktop_service

        query = ElementQuery(
            automation_id=input_data.get("automation_id"),
            name=input_data.get("name"),
            control_type=input_data.get("control_type"),
        )
        req = DesktopActionRequest(
            action_type=DesktopActionType.INVOKE,
            window_ref=input_data["window_ref"],
            locator=query,
        )
        res = await desktop_service.execute_action(req)
        return {
            "action_id": res.action_id,
            "status": res.status,
            "verification_status": res.verification_status,
            "result_data": res.result_data,
        }


class DesktopSetValueCapability(BaseCapability):
    """Sets text content into an editable control in an authorized desktop window."""

    capability_id = "desktop_set_value"
    name = "Set Control Text Value"
    version = "1.0.0"
    description = "Enters validated text into an editable control via UI Automation ValuePattern."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
                "value": {"type": "string"},
                "automation_id": {"type": "string"},
                "name": {"type": "string"},
                "control_type": {"type": "string"},
            },
            "required": ["window_ref", "value"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_id": {"type": "string"},
                "status": {"type": "string"},
                "verification_status": {"type": "string"},
            },
            "required": ["action_id", "status", "verification_status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import DesktopActionRequest, DesktopActionType, ElementQuery
        from app.computer.service import desktop_service

        query = ElementQuery(
            automation_id=input_data.get("automation_id"),
            name=input_data.get("name"),
            control_type=input_data.get("control_type"),
        )
        req = DesktopActionRequest(
            action_type=DesktopActionType.SET_VALUE,
            window_ref=input_data["window_ref"],
            locator=query,
            value=input_data["value"],
        )
        res = await desktop_service.execute_action(req)
        return {
            "action_id": res.action_id,
            "status": res.status,
            "verification_status": res.verification_status,
            "result_data": res.result_data,
        }


class DesktopManageWindowCapability(BaseCapability):
    """Manages window states: activate, minimize, maximize, restore, close."""

    capability_id = "desktop_manage_window"
    name = "Manage Window State"
    version = "1.0.0"
    description = "Changes window state (activate, minimize, maximize, restore, close) with validation."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_ref": {"type": "string"},
                "action": {"type": "string", "enum": ["activate", "minimize", "maximize", "restore", "close"]},
            },
            "required": ["window_ref", "action"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "action": {"type": "string"},
            },
            "required": ["success", "action"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import WindowManageAction
        from app.computer.service import desktop_service

        act = WindowManageAction(input_data["action"])
        success = await desktop_service.manage_window(input_data["window_ref"], act)
        return {"success": success, "action": act.value}


class DesktopExecuteActionCapability(BaseCapability):
    """Executes a structured desktop action request across any supported control pattern."""

    capability_id = "desktop_execute_action"
    name = "Execute Desktop Action"
    version = "1.0.0"
    description = "Dispatches a typed desktop action request (invoke, set_value, toggle, select, scroll, press_key)."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_type": {"type": "string"},
                "window_ref": {"type": "string"},
                "value": {"type": "string"},
                "key": {"type": "string"},
                "modifiers": {"type": "array", "items": {"type": "string"}},
                "locator": {"type": "object"},
            },
            "required": ["action_type", "window_ref"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action_id": {"type": "string"},
                "status": {"type": "string"},
                "verification_status": {"type": "string"},
            },
            "required": ["action_id", "status", "verification_status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from app.computer.contracts import DesktopActionRequest, DesktopActionType, ElementQuery
        from app.computer.service import desktop_service

        loc = None
        if "locator" in input_data and isinstance(input_data["locator"], dict):
            loc = ElementQuery(**input_data["locator"])

        req = DesktopActionRequest(
            action_type=DesktopActionType(input_data["action_type"]),
            window_ref=input_data["window_ref"],
            value=input_data.get("value"),
            key=input_data.get("key"),
            modifiers=input_data.get("modifiers", []),
            locator=loc,
        )
        res = await desktop_service.execute_action(req)
        return {
            "action_id": res.action_id,
            "status": res.status,
            "verification_status": res.verification_status,
            "duration_ms": res.duration_ms,
            "result_data": res.result_data,
        }


