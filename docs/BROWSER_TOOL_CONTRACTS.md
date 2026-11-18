# Browser Tool Contracts and API Endpoints (Stage 16)

## 1. Registered Multi-Agent Browser Capabilities

AUTONOM Stage 16 registers 9 executable browser capabilities in `services/api/app/orchestration/capabilities/computer.py` and `registry.py`, accessible to the `browser_agent` and multi-agent workflows:

| Capability Name | Tool Name | Scope / Permission Required | Description |
| :--- | :--- | :--- | :--- |
| **`browser_navigate`** | `browser.navigate` | `browser:navigate` | Navigates a browser tab to an allowed destination URL. |
| **`browser_inspect_dom`** | `browser.inspect_dom` | `browser:inspect` | Extracts interactive elements and forms with token estimation. |
| **`browser_click`** | `browser.click` | `browser:click` | Clicks an interactive element using smart locator resolution. |
| **`browser_fill`** | `browser.fill` | `browser:fill` | Fills an input or textarea with verified content. |
| **`browser_download`** | `browser.download` | `browser:download` | Intercepts, hashes, and stores file downloads safely. |
| **`browser_submit_form`**| `browser.submit_form` | `browser:submit_form` | Submits an application form subject to approval check. |
| **`browser_take_screenshot`**| `browser.take_screenshot` | `browser:inspect` | Captures viewport/full-page image with thumbnail. |
| **`browser_manage_tabs`**| `browser.manage_tabs` | `browser:tabs` | Creates, switches, or closes tabs in a session. |
| **`browser_plan_navigation`**| `browser.plan_navigation` | `browser:navigate` | Analyzes destination and determines required auth profile. |

---

## 2. Pydantic Contracts and Schemas

All browser operations are strongly typed in `services/api/app/browser/contracts.py`:

### `BrowserActionRequest`
```python
class BrowserActionRequest(BaseModel):
    action_type: BrowserActionType  # navigate, click, fill, select, check, press_key, hover, scroll, evaluate
    locator: Optional[str] = None
    value: Optional[str] = None
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)
    wait_until: Optional[str] = "load"
    expected_outcome: Optional[str] = None
    verify: bool = True
```

### `DOMExtractionResponse`
```python
class DOMExtractionResponse(BaseModel):
    session_id: str
    tab_id: str
    url: str
    title: str
    elements: List[InteractiveElementNode]
    forms: List[ExtractedFormDefinition]
    total_elements: int
    estimated_tokens: int
    extracted_at: datetime
```

---

## 3. REST API Endpoint Specification

Mounted under `/api/v1/browser/` in `services/api/app/api/v1/endpoints/browser.py`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/engines` | Lists detected browser engines (Chromium, Edge, Chrome) |
| `POST` | `/sessions` | Launches a new browser session context |
| `GET` | `/sessions` | Lists active and historical browser sessions |
| `GET` | `/sessions/{id}` | Retrieves session status, active tabs, and telemetry |
| `DELETE` | `/sessions/{id}` | Closes session, tabs, and persists final traces |
| `POST` | `/sessions/{id}/tabs` | Opens a new tab |
| `POST` | `/sessions/{id}/tabs/{tab_id}/switch` | Switches active tab |
| `DELETE` | `/sessions/{id}/tabs/{tab_id}` | Closes a tab |
| `POST` | `/sessions/{id}/actions` | Dispatches an action (click, fill, navigate, etc.) |
| `GET` | `/sessions/{id}/dom` | Extracts structured interactive DOM tree |
| `GET` | `/sessions/{id}/screenshot` | Captures viewport screenshot (raw image/png) |
| `GET` | `/sessions/{id}/forms` | Analyzes application forms and field mappings |
| `POST` | `/sessions/{id}/forms/{form_id}/submit` | Submits form with policy verification |
| `GET` | `/sessions/{id}/trace` | Stops tracing and exports zip diagnostic file |
| `GET` | `/downloads` | Lists tracked downloads with SHA-256 hashes |
| `GET` | `/downloads/{id}/file` | Streams downloaded file artifact |
| `GET` | `/profiles` | Lists saved encrypted browser profiles |
| `POST` | `/profiles` | Creates a new profile slot |
| `POST` | `/profiles/{id}/save-state` | Captures and DPAPI-encrypts session state |
| `DELETE` | `/profiles/{id}` | Deletes profile and encrypted credentials |
| `POST` | `/validate-url` | Validates target URL against security origin rules |
