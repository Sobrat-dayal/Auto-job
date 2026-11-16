# AUTONOM — Workspace Navigation & Route Integration Specification (Stage 09)

## 1. Navigation Architecture

AUTONOM features a unified hierarchical navigation architecture defined in `apps/desktop/src/config/navigation.ts`. All 13 core modules and over 50 sub-paths are wired directly into the desktop router and sidebar.

---

## 2. Global Shortcuts & Interactions

| Shortcut                 | Scope  | Behavior                                                                 |
| :----------------------- | :----- | :----------------------------------------------------------------------- |
| `Ctrl+B` / `Cmd+B`       | Global | Toggles sidebar between expanded (240px) and collapsed (56px) modes      |
| `Ctrl+K` / `Cmd+K`       | Global | Opens Command Palette fuzzy search over all modules and actions          |
| `Ctrl+1`                 | Global | Jumps directly to Command Center (`/dashboard`)                          |
| `Escape`                 | Global | Closes slide-over `ModuleDetailPanel`, Command Palette, or active flyout |
| `Pause` / `Ctrl+Alt+Esc` | Global | Emergency computer control killswitch (detaches OS input hooks)          |

---

## 3. Route Mapping Table

| Parent Route      | Sub-Routes                                                                                                                                                                         | Rendered Workspace        | Sub-Tab Synchronized                                                      |
| :---------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------ | :------------------------------------------------------------------------ |
| `/dashboard`      | `/dashboard`                                                                                                                                                                       | `Overview`                | Command Center Overview                                                   |
| `/agents`         | `/agents/all`, `/agents/active`, `/agents/tasks`, `/agents/performance`, `/agents/config`                                                                                          | `AgentsWorkspace`         | All, Active, Tasks, Performance, Config                                   |
| `/recruitment`    | `/recruitment/discovery`, `/recruitment/recommended`, `/recruitment/pipeline`, `/recruitment/submitted`, `/recruitment/history`, `/recruitment/excluded`, `/recruitment/analytics` | `RecruitmentWorkspace`    | Discovery, Recommended, Pipeline, Submitted, History, Excluded, Analytics |
| `/computer`       | `/computer/live`, `/computer/tasks`, `/computer/browser`, `/computer/history`, `/computer/permissions`                                                                             | `ComputerWorkspace`       | Live Viewport, Tasks, Browser, History, Permissions                       |
| `/communications` | `/communications/inbox`, `/communications/conversations`, `/communications/email`, `/communications/telegram`, `/communications/whatsapp`, `/communications/follow-ups`            | `CommunicationsWorkspace` | Inbox, Conversations, Email, Telegram, WhatsApp, Follow-ups               |
| `/interviews`     | `/interviews/upcoming`, `/interviews/calendar`, `/interviews/prep`, `/interviews/mock`, `/interviews/history`                                                                      | `InterviewsWorkspace`     | Upcoming, Calendar, Prep, Mock, History                                   |
| `/documents`      | `/documents/workspace`, `/documents/docs`, `/documents/spreadsheets`, `/documents/presentations`, `/documents/pdfs`, `/documents/artifacts`                                        | `DocumentsWorkspace`      | All Workspace, Docs, Spreadsheets, Presentations, PDFs, Blobs             |
| `/coding`         | `/coding/projects`, `/coding/agents`, `/coding/repos`, `/coding/builds`, `/coding/reviews`                                                                                         | `CodingWorkspace`         | Projects, Agents, Repos, Builds, Reviews                                  |
| `/creative`       | `/creative/3d`, `/creative/animation`, `/creative/graphics`, `/creative/media`, `/creative/renders`, `/creative/assets`                                                            | `CreativeWorkspace`       | 3D Viewport, Animation, Graphics, Media, Renders, Assets                  |
| `/research`       | `/research/projects`, `/research/web`, `/research/companies`, `/research/markets`, `/research/reports`, `/research/watchlists`                                                     | `ResearchWorkspace`       | Dossiers, Web Queries, Companies, Markets, Reports, Watchlists            |
| `/workflows`      | `/workflows/all`, `/workflows/active`, `/workflows/builder`, `/workflows/scheduled`, `/workflows/history`                                                                          | `WorkflowsWorkspace`      | All Tasks, Active, DAG Builder, Scheduled, History                        |
| `/analytics`      | `/analytics/overview`, `/analytics/jobs`, `/analytics/agents`, `/analytics/workflows`, `/analytics/resources`                                                                      | `AnalyticsWorkspace`      | Overview, Jobs, Agents, Workflows, Resources                              |
| `/activity`       | `/activity/timeline`, `/activity/agents`, `/activity/tasks`, `/activity/events`, `/activity/errors`, `/activity/audit`                                                             | `ActivityWorkspace`       | Timeline, Agents, Tasks, Events, Errors, Audit                            |
| `/integrations`   | `/integrations/connected`, `/integrations/ai`, `/integrations/mcp`, `/integrations/platforms`, `/integrations/comms`, `/integrations/health`                                       | `IntegrationsWorkspace`   | Connected, AI Models, MCP Servers, Platforms, Comms, Health               |
| `/settings`       | `/settings/diagnostics`, `/settings/desktop`, `/settings/storage`, `/settings/credentials`                                                                                         | Dedicated Views           | Settings & Diagnostics Panels                                             |

---

## 4. URL State Synchronization Pattern

Each workspace component reads `useLocation().pathname` on mount and URL transition:

```tsx
const getInitialTab = (): string => {
  if (location.pathname.includes('/recruitment/pipeline')) return 'pipeline';
  if (location.pathname.includes('/recruitment/submitted')) return 'submitted';
  // ...
  return 'discovery';
};

const handleTabChange = (tabId: string) => {
  setActiveTab(tabId);
  navigate(`/recruitment/${tabId}`);
};
```

This bidirectional synchronization ensures:

1. Direct deep-linking or browser back/forward buttons seamlessly switch the active workspace tab.
2. Clicking a tab updates the browser history and address bar without reloading.
3. Breadcrumb navigation in the header accurately tracks the user's active context.
