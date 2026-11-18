# Stage 19: Intelligent Hybrid Computer Interaction Engine Architecture

## 1. Executive Summary & Objective

AUTONOM Stage 19 unifies the three disparate computer interaction modalities developed across Stages 16 through 18 into a single, cohesive, production-grade **Intelligent Hybrid Computer Interaction Engine**:

- **Stage 16:** Browser Automation via Playwright DOM Inspection & CDP Execution.
- **Stage 17:** Windows Native Structural Automation via Microsoft UI Automation (UIA) & Win32 Messaging.
- **Stage 18:** Visual Computer Control via Windows Screen Capture (MSS/GDI/WGC), Offline WinRT OCR, and Visual Coordinate Grounding.

Prior to Stage 19, agents and users had to manually choose which interaction system to employ. In complex, real-world desktop environments—such as Electron applications, embedded Chromium web views, custom-rendered Canvas/DirectX interfaces, and legacy Win32 dialogs—no single method suffices.

Stage 19 introduces deterministic multi-method control routing, unified target classification, context-aware fallback with bounded switch limits, multi-method mutual exclusion leases, and seamless Stage 14 policy-enforced security boundaries.

---

## 2. High-Level Architectural Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                    AUTONOM SUPERVISOR / AGENTS                                     |
|                       (windows_computer_agent, browser_agent, desktop_agent)                       |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                         STAGE 19: HYBRID COMPUTER SERVICE FACADE (`service.py`)                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
       +------------------------------------------+-------------------------------------------+
       |                                          |                                           |
       v                                          v                                           v
+-------------------------------+  +-------------------------------+  +-------------------------------+
|    SURFACE & TARGET ENGINE    |  |     HYBRID ROUTING ENGINE     |  |    OBSERVATION COORDINATOR    |
| - SurfaceClassifier           |  | - MethodScorer (0..100)       |  | - Cross-Method Snapshots      |
| - TargetIdentityValidator     |  | - RoutingPolicies             |  | - Text/DOM/UIA/Visual Merging |
| - TargetResolver              |  | - FallbackController (max=3)  |  | - Stale Cache Invalidation    |
| - Recycled HWND Protection    |  | - MethodHealthTracker         |  |                               |
+-------------------------------+  +-------------------------------+  +-------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                         HYBRID ACTION COORDINATOR & STATE MACHINE                                  |
|               Cycle: Observe -> Classify -> Route -> Authorize -> Act -> Verify                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
         v                                        v                                        v
+-------------------+                    +-------------------+                    +-------------------+
|  SECURITY GUARDS  |                    | INPUT LEASE MGR   |                    | VERIFICATION ENG  |
| - Emergency Stop  |                    | - Exclusive Lock  |                    | - Post-Act Verify |
| - Session Lock    |                    | - SendInput Lease |                    | - Mutate Detect   |
| - Stage 14 Bridge |                    | - Steal Protection|                    | - Failure Classify|
+-------------------+                    +-------------------+                    +-------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                        INTERACTION ADAPTER REGISTRY                             |
         +-------------------+--------------------+-------------------+--------------------+
                             |                    |                   |                    |
                             v                    v                   v                    v
                     +---------------+    +---------------+   +---------------+    +---------------+
                     |  BROWSER DOM  |    |  WINDOWS UIA  |   | WINDOWS WIN32 |    |    VISUAL     |
                     | Playwright CDP|    | UI Automation |   | HWND Messages |    | WinRT OCR/MSS |
                     +---------------+    +---------------+   +---------------+    +---------------+
```

---

## 3. Core Engine Lifecycle (The Observe-Route-Act-Verify Loop)

1. **Target Identification & Surface Classification:**
   - Resolves target references (DOM selector, Window title, PID, HWND, UIA AutomationId, screen coordinates).
   - Validates HWND against live OS process IDs to prevent target redirection via recycled window handles.
   - Classifies target surface (`BROWSER_DOM`, `NATIVE_UIA`, `NATIVE_WIN32`, `CUSTOM_RENDERED`, `EMBEDDED_WEBVIEW`, or `UNKNOWN`).

2. **Probe Fan-Out & Capability Scoring:**
   - Probes registered adapters concurrently.
   - Evaluates applicability, capability match, latency estimates, and adapter health status.
   - Scores candidates across a 0..100 scale favoring fast, deterministic structural methods over expensive visual grounding.

3. **Stage 14 Authorization Pre-Flight:**
   - Evaluates caller autonomy grants, action effect (`ALLOW`, `DENY`, `REQUIRE_APPROVAL`), and permission category.
   - Verifies system killswitch and desktop session interactivity (asserting user desktop is unlocked).

4. **Input Ownership Lease Acquisition:**
   - Acquires exclusive foreground input lock for physical interaction methods (`VISUAL_GROUNDING`, `WINDOWS_WIN32`) to prevent race conditions.
   - Background non-intrusive operations (`BROWSER_DOM`, `WINDOWS_UIA` ValuePattern) execute without stealing the system mouse pointer.

5. **Action Execution & Verification:**
   - Executes requested action via selected adapter.
   - Verifies resulting state mutation (DOM attribute change, UIA property update, OCR text mutation, or pixel difference).

6. **Context-Aware Fallback (On Failure):**
   - If action fails or returns `unknown_outcome`, evaluates fallback eligibility.
   - Bounded to a maximum depth of 3 switches.
   - Enforces strict non-idempotency protections: non-repeatable actions (such as payment submission or form POST) are blocked from speculative fallback.
