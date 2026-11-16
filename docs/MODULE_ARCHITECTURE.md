# AUTONOM — Module Architecture & Workspace Foundations (Stage 09)

## 1. Overview & Architectural Purpose

Stage 09 establishes the full-featured, multi-module workspace architecture for AUTONOM. While Stage 08 created the operational Command Center dashboard and Stage 07 implemented the expandable/collapsible sidebar, Stage 09 transforms the desktop shell into a cohesive 13-module operational environment.

AUTONOM is an autonomous multi-agent assistant designed for Windows 11. Its primary initial domain is recruitment automation (job discovery, application filing, recruiter communications, and interview preparation), expanding to universal computer control, software engineering, 3D modeling, document generation, and market research.

---

## 2. The 13 Core Workspaces

Every core capability is organized into a dedicated workspace under `apps/desktop/src/features/`:

| Module               | Route Prefix        | Primary Purpose                                                             | Roadmap State                                         |
| :------------------- | :------------------ | :-------------------------------------------------------------------------- | :---------------------------------------------------- |
| **Agents**           | `/agents/*`         | 24-agent swarm catalog, worker pool monitoring, model configuration         | Stage 03 Worker Pool Active / Stage 12 Swarm Planned  |
| **Recruitment**      | `/recruitment/*`    | Discovered job listings, 10-stage pipeline, application attempts            | SQLite Storage Active / Stage 26 & 31 Engines Planned |
| **Computer Control** | `/computer/*`       | Dual-modality perception (Visual Grounding + Windows UIA), safety gates     | Rust Bridge Ready / Stage 16–18 Planned               |
| **Communications**   | `/communications/*` | Unified recruiter inbox (Email, Telegram, WhatsApp, Follow-ups)             | Staging Interface Active / Stage 36 Planned           |
| **Interviews**       | `/interviews/*`     | Calendar schedule, STAR prep dossiers, live mock interview studio           | Prep Shell Active / Stage 39 & 40 Planned             |
| **Documents**        | `/documents/*`      | PDF resumes, reports, spreadsheets, presentations, encrypted artifacts      | SQLite Artifact Metadata Active / Stage 42 Planned    |
| **Coding**           | `/coding/*`         | Repository manager, test runners, AST code edits, diff reviews              | Workspace Shell Active / Stage 41 Planned             |
| **Creative Studio**  | `/creative/*`       | 3D WebGL viewport, Blender render queue, animation timelines                | WebGL Canvas Active / Stage 43 Planned                |
| **Research**         | `/research/*`       | Web intelligence, target company profiles, compensation benchmarks          | Dossier Viewer Active / Stage 44 Planned              |
| **Workflows**        | `/workflows/*`      | Persistent task execution, diagnostic task dispatch, cancellation, DAGs     | Stage 03 Task Engine Active / Stage 45 Planned        |
| **Analytics**        | `/analytics/*`      | Task throughput, execution latency, success ratios, resource telemetry      | Recharts Aggregations Active (Stage 08)               |
| **Activity**         | `/activity/*`       | Immutable SQLite event ledger, state transition tracking, payload inspector | Real-Time Ledger Active (Stage 03/04)                 |
| **Integrations**     | `/integrations/*`   | AI model providers, MCP tool servers, ATS platforms, DPAPI vault            | Windows DPAPI Vault Active / Stage 11 & 45 Planned    |

---

## 3. Shared Module Primitives (`components/module/`)

To guarantee design uniformity, keyboard accessibility, and maintainability across all 13 modules, Stage 09 provides a shared primitive library:

1. **`ModulePage`**: Fluid container layout supporting responsive scroll areas and an optional slide-over `ModuleDetailPanel`.
2. **`ModuleHeader`**: Standardized header containing module title, description, category icon, roadmap stage tag, and action button bar.
3. **`ModuleToolbar`**: Debounced search input, status/role filter chips, grid/list view mode toggles, and live refresh buttons.
4. **`ModuleTabs`**: Accessible tab navigation strip that synchronizes with route sub-paths (`navigate()`) and renders live item count badges.
5. **`ModuleEmptyState`**: Zero-data fallback that informs the user why no records exist and presents a primary call-to-action.
6. **`ModuleUnavailableState`**: Honest roadmap stage attribution banner explaining upcoming engine activations and planned capabilities per the Zero-Fake-Data rule.
7. **`ModuleLoadingState`**: Accessible skeleton layout placeholders for cards and tables during asynchronous data fetches.
8. **`ModuleErrorState`**: Actionable error fallback displaying diagnostic messages and a one-click connection retry action.
9. **`ModuleDetailPanel`**: Slide-over right drawer (384px) for inspecting selected items (jobs, applications, tasks, agents, artifacts).

---

## 4. Code-Splitting and Lazy Loading Architecture

To maintain desktop performance and avoid inflating the initial bundle size, all 13 module workspaces are loaded on-demand using `React.lazy()` and `Suspense`:

```tsx
// apps/desktop/src/App.tsx
const AgentsWorkspace = React.lazy(() => import('@/features/agents/AgentsWorkspace'));
const RecruitmentWorkspace = React.lazy(
  () => import('@/features/recruitment/RecruitmentWorkspace')
);
// ...
<Suspense fallback={<WorkspaceSuspenseFallback />}>
  <Routes>
    <Route path="/agents/*" element={<AgentsWorkspace />} />
    <Route path="/recruitment/*" element={<RecruitmentWorkspace />} />
    {/* ... */}
  </Routes>
</Suspense>;
```

When built via `vite build`, Vite generates distinct async chunks (e.g. `AgentsWorkspace-*.js`, `RecruitmentWorkspace-*.js`), keeping the initial launch instantaneous.

---

## 5. Zero-Fake-Data Integrity Principle

Stage 09 strictly abides by the project's zero-fake-data integrity rule:

- **No synthetic job listings**: Listings come exclusively from the SQLite `job_listings` table.
- **No artificial applications**: Pipeline cards reflect genuine records in the SQLite `applications` table.
- **No fake recruiter emails**: Inbox and communications displays remain honest until Stage 36 connects genuine IMAP/OAuth feeds.
- **No fabricated agent metrics**: Agent status and worker pools reflect actual running Python processes and SQLite task records.
