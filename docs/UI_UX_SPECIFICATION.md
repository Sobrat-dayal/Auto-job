# AUTONOM — User Interface & User Experience (UI/UX) Specification

## 1. Visual Direction & Design Philosophy

AUTONOM is an information-dense, high-utility desktop tool for Windows 11. It rejects decorative vanity metrics, gamified badges, oversized pill buttons, purple gradients, and cinematic illustrations. Every pixel is allocated to actionable operational controls, live agent state monitoring, and workflow transparency.

### 1.1 Color Palette & Theme Tokens

```
Surface Tokens:
- Background Deep:      #090d16 (Deep charcoal navy)
- Surface Elevated:     #0f172a (Slate-900 / Card background)
- Surface Overlay:      #1e293b (Slate-800 / Dropdown & modal background)
- Border Subtle:        #1e293b (Slate-800 / Default separator)
- Border Focused:       #334155 (Slate-700 / Active element border)

Accent & Semantic Tokens:
- Primary Accent:       #2563eb (Engineered royal blue)
- Primary Accent Hover: #1d4ed8 (Deep blue)
- Secondary Accent:     #06b6d4 (Telemetry cyan)
- Success / Live:       #10b981 (Emerald-500 / Healthy state)
- Warning / Pending:    #f59e0b (Amber-500 / Awaiting approval)
- Error / Critical:     #ef4444 (Rose-500 / Action failed)
- Muted / Inactive:     #64748b (Slate-500 / Secondary text)

Typography:
- Primary Font:         Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
- Monospace Font:       "JetBrains Mono", Consolas, "Fira Code", monospace
- Base Scale:           13px / 14px compact default desktop density
```

### 1.2 Anti-Patterns Explicitly Prohibited

- NO purple gradients or neon glow halos.
- NO oversized rounded pill buttons that waste vertical space.
- NO cinematic background wallpapers or illustrative cartoon avatars.
- NO fabricated user reviews, fake achievements, or gamified leveling bars.
- NO unlinked mock buttons; all interactive elements must trigger backend operations or display genuine system state.

---

## 2. Shell Navigation Architecture & Sidebar

The layout consists of a native Windows title bar, an expandable and collapsible vertical sidebar on the left, a breadcrumb/status header, and an expansive primary workspace viewport.

```
+----------------------------------------------------------------------------------------------------+
| [AUTONOM v0.1.0]                          [Backend: HEALTHY 8765] [Kill Switch: Ctrl+Shift+Esc] [-][+][x]|
+-------------------+--------------------------------------------------------------------------------+
| (<< / >>) Toggle  | Command Center > Overview                                    [Refresh] [Pause] |
+-------------------+--------------------------------------------------------------------------------+
| [O] Command Center|  +--------------------+ +--------------------+ +--------------------+           |
| [J] Jobs & Apps   |  | Active Agents: 4   | | Jobs Discovered: 48| | Pending Approvals:0|           |
| [A] Agents (Swarm)|  | Status: All Idle   | | High Match (>85%):12| | Daily Cap: 25 / 100|           |
| [C] Computer Ctrl |  +--------------------+ +--------------------+ +--------------------+           |
| [M] Communications|                                                                                |
| [I] Interviews    |  +--------------------------------------------------------------------------+  |
| [D] Documents     |  | Live Agent Swarm Stream & Task Execution                                 |  |
| [</>] Coding      |  | [12:30:01] Supervisor: Initialized runtime DAG for career discovery.     |  |
| [P] Creative      |  | [12:30:02] Scout-01: Discovered 14 new Senior Full-Stack roles on ATS.   |  |
| [R] Research      |  +--------------------------------------------------------------------------+  |
| [W] Workflows     |                                                                                |
| [G] Analytics     |  +--------------------------------------------------------------------------+  |
| [L] Activity Logs |  | High-Priority Matches Awaiting Review                                    |  |
| [T] Integrations  |  | - Staff Engineer @ Datadog (Match: 94%) [View Match] [Tailor Resume]     |  |
| [S] Settings      |  | - Principal Systems Engineer @ Cloudflare (Match: 91%) [Review]          |  |
+-------------------+--------------------------------------------------------------------------------+
```

### 2.1 Sidebar Operating Modes

1. **Expanded Mode (Width: 240px)**:
   - Displays icon + section label + badge counts (e.g., `Jobs (12)`).
   - Grouped into functional sections: `Core Operations`, `Specialist Tools`, and `System`.
   - Smooth CSS collapse animation (< 150ms).
2. **Compact Rail Mode (Width: 60px)**:
   - Displays centered icon-only rail.
   - Hovering an icon displays a high-contrast floating tooltip with module title and quick shortcut.
   - Clicking active icon maintains navigation; sub-navigation opens in a flyout popover.

---

## 3. Full Navigation Tree (15 Top-Level Modules)

```
1. Command Center
   ├── 1.1 Overview Dashboard
   ├── 1.2 Active Swarm Monitor
   └── 1.3 System Telemetry & VRAM Monitor

2. Jobs & Applications
   ├── 2.1 Discovered Job Queue
   ├── 2.2 Semantic Match Explorer & Gap Analysis
   ├── 2.3 Tailored Application Tracker
   └── 2.4 User Career Profile & Factual Evidence

3. Agents
   ├── 3.1 Swarm Coordinator & Live Board
   ├── 3.2 Specialist Catalog (24 Agents)
   └── 3.3 Dynamic Tool Registry & Permissions

4. Computer Control
   ├── 4.1 Live Desktop Observer & Frame Inspector
   ├── 4.2 Structural UIA Tree & DOM Explorer
   ├── 4.3 Safe Boundary Mask & Forbidden Zones
   └── 4.4 Macro Recorder & Playback Console

5. Communications
   ├── 5.1 Recruiter Inbox Tracker
   ├── 5.2 Application Status Sync
   └── 5.3 Automated Response Drafter

6. Interviews
   ├── 6.1 Scheduled Interview Timeline
   ├── 6.2 Company Research Dossiers
   └── 6.3 Technical & Behavioral Q&A Flashcards

7. Documents
   ├── 7.1 Factual Resume Manager & AST Editor
   ├── 7.2 ATS-Compliant PDF Exporter
   └── 7.3 Cover Letter Generator

8. Coding
   ├── 8.1 Local Workspace IDE & Git Dashboard
   ├── 8.2 Sandboxed Script Execution Terminal
   └── 8.3 Test Suite & Code Review Inspector

9. Creative Studio
   ├── 9.1 Blender 3D Automation & Asset Preview
   ├── 9.2 2D Graphics & Media Processing
   └── 9.3 FFmpeg Video/Audio Pipeline

10. Research & Markets
    ├── 10.1 Autonomous Web Research Compiler
    ├── 10.2 Compensation & Salary Benchmarks
    └── 10.3 Company Financials & Tech Stack Radar

11. Workflows
    ├── 11.1 Scheduled Automation Recipes (Cron)
    ├── 11.2 Visual DAG Workflow Studio
    └── 11.3 Execution History & Run Inspector

12. Analytics
    ├── 12.1 Funnel Metrics (Found -> Tailored -> Interview)
    ├── 12.2 Model Latency & Token Expenditure
    └── 12.3 Time Saved & Efficiency Accounting

13. Activity Logs
    ├── 13.1 Immutable Audit Log Viewer
    ├── 13.2 Causal Execution Trace Debugger
    └── 13.3 Replay Inspector

14. Integrations
    ├── 14.1 ATS Portals & Career Sources
    ├── 14.2 Model Providers (Cloud & Local)
    ├── 14.3 Model Context Protocol (MCP) Clients
    └── 14.4 Messaging Webhooks (Telegram / Slack)

15. Settings
    ├── 15.1 Advance Autonomy & Approval Policies
    ├── 15.2 Windows DPAPI Secure Credential Vault
    ├── 15.3 Hardware, GPU & Model Context Tuning
    └── 15.4 System Updates & Diagnostics
```

---

## 4. Key Functional Dashboard Components

1. **Live Backend Heartbeat Pill**:
   - Permanently visible in the top header.
   - States: `HEALTHY (8765)` (emerald green dot), `DEGRADED` (amber pulse), `DISCONNECTED` (rose red with automatic reconnect counter).
   - Clicking opens IPC diagnostic popover showing database latency, active worker count, and memory RSS.
2. **Approval Gateway Toast / Modal**:
   - Slides smoothly into view when a Tier 3 action is intercepted.
   - Shows action diff (e.g., "Submit Application to Datadog for Staff Engineer").
   - Clearly displays: Target URL, Attached Resume PDF hash, Screening Answers provided, and Risk Category.
   - Buttons: `Approve & Submit`, `Reject & Skip`, `Review in Visible Browser`.
3. **Emergency Disengage Status**:
   - Prominently displays the global hotkey (`Ctrl+Shift+Esc`).
   - If triggered, screen displays a distinct yellow banner: `AUTOMATION PAUSED BY USER — INPUT UNHOOKED`.
