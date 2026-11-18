# Visual Automation Architecture Specification (Stage 18)

## 1. Overview & Vision

Stage 18 implements the third pillar of AUTONOM's tri-modality computer interaction stack: **Vision-Based Desktop Automation**. While Stage 16 introduced Playwright browser automation and Stage 17 established Microsoft UI Automation (UIA) native structural control, many mission-critical legacy applications, specialized tooling, virtualized controls, and rich custom canvases lack reliable accessibility tree definitions.

Visual automation equips AUTONOM to observe the Windows desktop like a human user: taking high-speed screenshots, running genuine offline WinRT Optical Character Recognition (OCR), grounding visual targets via Vision-Language Model (VLM) heuristics and bounding boxes, dispatching coordinate-targeted Windows `SendInput` actions, and verifying state transitions through visual diffing and post-action OCR.

---

## 2. Architectural Components

```
+-----------------------------------------------------------------------------------+
|                            AUTONOM SUPERVISOR / AGENTS                            |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                        VisualComputerService (Facade)                             |
|  - Active session lifecycle        - Element detection      - Verification       |
|  - Multimodal grounding            - Input dispatch         - Fault recovery     |
+-----------------------------------------------------------------------------------+
           │                                │                           │
           ▼                                ▼                           ▼
+-----------------------+       +-----------------------+   +-----------------------+
|  Capture Subsystem    |       |  Grounding Subsystem  |   |    Input Subsystem    |
|  - MSS (Direct Grab)  |       |  - WinRT Offline OCR  |   |  - Windows SendInput  |
|  - GDI (PrintWindow)  |       |  - Box Geometry / IoU |   |  - Ownership Leases   |
|  - WGC (Win Graphics) |       |  - Coordinate Xform   |   |  - Rate Limiter       |
|  - Preprocessing      |       |  - Target Validator   |   |  - Emergency Stop     |
+-----------------------+       +-----------------------+   +-----------------------+
           │                                │                           │
           └────────────────────────────────┼───────────────────────────┘
                                            ▼
+-----------------------------------------------------------------------------------+
|                         Execution & Recovery Subsystem                            |
|  - VisualStateMachine (Observing -> Grounding -> Acting -> Verifying -> Recovery)  |
|  - VisualActionVerifier (Pixel Diff + OCR delta assertion)                        |
|  - VisualRecoveryManager (Bounded retries, jittered delays, alternate strategies) |
+-----------------------------------------------------------------------------------+
```

---

## 3. Data Contracts & Standards

All visual automation state transitions and representations adhere to strict Pydantic v2 schemas:
- `CapturedFrame`: Encapsulates `FrameMetadata`, base64 PNG data, and lazily decoded Pillow image representations.
- `FrameMetadata`: DPI scale, timestamp, source provider, physical resolution, virtual desktop offset, and content SHA-256 hash.
- `BoundingBox`: Integer pixel coordinates `{left, top, width, height, right, bottom, center}`.
- `NormalizedBox`: Normalized floating-point space `[0.0, 1.0]` with flexible alias resolution (`xmin`, `ymin`, `xmax`, `ymax`).
- `VisualElementDetection`: Category classification (`BUTTON`, `INPUT`, `TEXT`, `DIALOG`), confidence, and source attribution (`ocr_engine`, `vlm_local`, `heuristic`).
- `VisualGroundingResult`: Resolved center target, physical desktop point, ambiguity classification (`unique`, `ambiguous`, `none`), and reasoning trail.
- `VisualActionResult`: Execution timing, verification outcome (`verified_success`, `verified_failure`, `uncertain`), pixel difference percentage, and before/after frame IDs.

---

## 4. Integration with Stage 14 Security Gate

All visual operations are strictly guarded by `VisualSecurityGuard`:
1. **Emergency Stop (Killswitch)**: Global `Pause/Break` and UI killswitch halts frame capture and keyboard/mouse dispatch immediately.
2. **Session Lock Guard**: Automation halts if Windows desktop session is locked or workstation switches to a secure desktop (UAC/Winlogon).
3. **Allowlist & Privacy Boundaries**: Passwords, banking portals, and sensitive credential windows are automatically redacted or forbidden from capture and interaction.
