# AUTONOM — Module Capabilities & Roadmap Activation Matrix (Stage 09)

## 1. Overview

Each of AUTONOM's 13 core modules integrates an operational user interface foundation in Stage 09, connected to backend SQLite storage and genuine telemetry where available. Autonomous AI generation and computer automation engines activate according to the 50-stage roadmap.

---

## 2. Capabilities & Roadmap Matrix

| Module               | Stage 09 Operational Foundation                                                | Upcoming Engine Activation                                                                               | Security Boundary                                                            |
| :------------------- | :----------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| **Agents**           | 24-agent catalog, active worker capacity, live task query, agent inspector     | **Stage 12**: Multi-agent swarm runtime, dynamic Plan-Execute-Verify (PEV) cycles, inter-agent messaging | Read-only process inspection; worker pool bound to local loopback            |
| **Recruitment**      | SQLite job listings, 10-stage pipeline status, attempt logs, listing inspector | **Stage 26**: Automated LinkedIn/Indeed ATS scrapers; **Stage 31**: Resume tailor scribe                 | Human authorization required before application submission                   |
| **Computer Control** | Canvas viewport shell, safety bounds, hardware killswitch trigger              | **Stage 16**: Chromium CDP driver; **Stage 17**: Visual Grounding; **Stage 18**: Windows UIA bridge      | Global panic killswitch (`Pause` / `Ctrl+Alt+Esc`) detaches OS hooks         |
| **Communications**   | Unified inbox layout, channel categorization, draft staging view               | **Stage 36**: OAuth Gmail/O365 IMAP sync; **Stage 38**: Telegram bot dispatcher                          | Outgoing messages staged in drafts; sending requires explicit human approval |
| **Interviews**       | ICS calendar view, STAR prep dossier layout, mock studio shell                 | **Stage 39**: Automated calendar syncing; **Stage 40**: Conversational AI mock simulator                 | Local speech synthesis/recognition; no unencrypted recording storage         |
| **Documents**        | SQLite artifact metadata, file size, SHA-256 checksums, retention class        | **Stage 42**: Office document compiler (DOCX, XLSX, PPTX, LaTeX)                                         | Files stored in sandboxed application directory; read-only metadata          |
| **Coding**           | Repository directory view, test run history, diff review shell                 | **Stage 41**: Autonomous multi-file editor, AST transformations, Git branch automation                   | All filesystem edits execute in sandboxed branch; commit confirmation gate   |
| **Creative Studio**  | Three.js WebGL canvas shell, render queue, asset catalog                       | **Stage 43**: Headless Blender Python rendering, procedural geometry synthesis                           | Headless render processes capped to background priority; CPU/GPU limits      |
| **Research**         | Market intelligence queries, company profile dossier viewer                    | **Stage 44**: Deep recursive web search, citation verification, executive briefs                         | Sandboxed web fetching; transparent citation attribution                     |
| **Workflows**        | Persistent task execution, diagnostic task dispatch, cancellation              | **Stage 45**: Visual drag-and-drop DAG editor, MCP tool graph authoring                                  | Cooperative task cancellation; strict timeout limits per handler             |
| **Analytics**        | Real-time Recharts charts, completion rates, durations, volume trends          | **Stage 08 Active**: Aggregate telemetry from durable SQLite task events                                 | Anonymized local telemetry; zero telemetry sent to third parties             |
| **Activity**         | Immutable SQLite event ledger, state transitions, JSON payload inspector       | **Stage 03/04 Active**: Real-time event bus subscriber and durable history                               | Immutable audit logs; read-only inspection                                   |
| **Integrations**     | Provider service catalog, connection status, DPAPI vault keys                  | **Stage 11**: Multi-LLM provider failover; **Stage 45**: MCP server router                               | Credentials encrypted with Windows DPAPI AES-256-GCM; zero plain secrets     |
