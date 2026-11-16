# AUTONOM — Agent Preferences & Swarm Directory Configuration

## 1. Overview & Architectural Role

The Agent Configuration system established in **Stage 10** provides centralized governance, execution profiles, autonomy tiers, and model assignments for all 24 autonomous agents in the AUTONOM swarm directory.

While agent runtime lifecycle orchestration, inter-agent messaging, and swarm consensus are scheduled for **Stage 12 (Multi-Agent Swarm Orchestration)** and **Stage 13 (Autonomous Job Application Engine)**, Stage 10 implements the configuration schema, persistence layer, and administrative UI controls.

```
+-----------------------------------------------------------------------------------------+
|                                FRONTEND: /settings/agents                               |
| - Global Swarm Concurrency Controls (Max Active Agents, Default Priority)               |
| - Directory Filter & Search (24 Specialized Agent Profiles across 6 Functional Domains) |
| - Per-Agent Configuration Drawer / Card:                                                |
|   * Target Model Assignment (Local Default, Fast Claude Haiku, Deep Reasoning Sonnet)   |
|   * Autonomy Tier (Full Autonomy, Supervised Approval, Disabled)                        |
|   * Execution Constraints (Timeout Seconds, Max Retries, Memory Retention Depth)        |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v PATCH /api/v1/settings/agents
+-----------------------------------------------------------------------------------------+
|                               FASTAPI LOCAL BACKEND (8765)                              |
| - AgentSettings Pydantic Schema Validation                                              |
| - 24-Agent Directory Validation & Default Fallbacks                                     |
| - SettingsRepository (Persisted to SQLite WAL `app_settings` under key `agents`)        |
+-----------------------------------------------------------------------------------------+
```

---

## 2. The 24-Agent Swarm Directory

AUTONOM categorizes its 24 specialized agent profiles across six operational domains:

### 2.1 Core Orchestration & Governance

1. `orchestrator_main`: Swarm Director, task decomposition, goal dispatch, and consensus coordination.
2. `task_decomposer`: High-level prompt breakdown into directed acyclic graph (DAG) task steps.
3. `agent_supervisor`: Runtime health monitoring, heartbeat tracking, and zombie task recovery.
4. `verifier_auditor`: Output validation, truthfulness evaluation, and policy compliance verification.

### 2.2 Recruitment & Career Automation (Primary Mission)

5. `job_hunter`: Multi-channel job discovery (LinkedIn, Indeed, greenhouse, lever, workdays).
6. `job_analyst`: Job description parsing, skill extraction, ATS suitability scoring, and gap analysis.
7. `resume_tailorer`: Contextual resume tailoring, LaTeX/DOCX generation, and keyword alignment.
8. `cover_letter_writer`: Personalized cover letter creation matching tone and recruiter criteria.
9. `application_submitter`: Automated form filling and multi-stage application submission.
10. `recruiter_communicator`: Inbound recruiter email parsing, automated draft responses, and outreach.
11. `interview_coach`: Interview question prediction, STAR-framework response prep, and role-play simulation.

### 2.3 Computer Control & Browser Automation

12. `browser_navigator`: Headless/headed Playwright browser automation, DOM traversal, and session handling.
13. `desktop_automator`: Windows UI Automation (UIA) accessibility tree navigation and native control.
14. `form_filler`: Complex multi-step form parsing, file upload attachment, and captcha escalation.

### 2.4 Research & Intelligence

15. `market_researcher`: Company financial research, industry trend analysis, and competitor mapping.
16. `company_profiler`: Executive team profiling, hiring manager identification, and culture analysis.
17. `compensation_analyst`: Salary benchmarking, equity valuation, and total compensation estimation.

### 2.5 Content Creation & Productivity

18. `document_writer`: Technical reports, documentation drafting, and Markdown/PDF synthesis.
19. `presentation_designer`: Slide deck structure, visual layout generation, and Marp presentation authoring.
20. `spreadsheet_analyst`: Excel/CSV financial analysis, formula creation, and data cleaning.
21. `creative_media`: Visual asset prompting, diagram creation, and 3D preview coordination.

### 2.6 Operations & Infrastructure

22. `diagnostics_monitor`: System telemetry inspection, CPU/RAM/VRAM tracking, and leak detection.
23. `security_auditor`: Windows DPAPI vault auditing, permission boundary enforcement, and log scrubbing.
24. `backup_manager`: Automated SQLite snapshot management, WAL compaction, and rollback handling.

---

## 3. Configuration Schema Specification (`AgentSettings`)

The configuration contract is declared in `services/api/app/schemas/settings.py` and `packages/shared-types/src/settings.ts`:

```typescript
export interface AgentProfileConfig {
  agent_id: string; // e.g. "job_hunter", "resume_tailorer"
  name: string; // User-facing display name
  description: string; // Role description
  category:
    'orchestration' | 'recruitment' | 'automation' | 'research' | 'productivity' | 'operations';
  enabled: boolean; // Enable or disable this agent in swarm dispatch
  preferred_model: 'local_default' | 'cloud_fast' | 'cloud_reasoning' | 'custom';
  custom_model_id?: string;
  autonomy_tier: 'full_autonomy' | 'supervised_approval' | 'disabled';
  max_execution_timeout_seconds: number; // 30 - 1800 (Default: 300)
  max_retries_on_failure: number; // 0 - 5 (Default: 2)
  memory_retention_steps: number; // 5 - 100 (Default: 20)
  require_audit_logging: boolean; // Default: true
}

export interface AgentSettings {
  max_concurrent_agents: number; // 1 - 8 (Default: 3, bound to hardware capacity)
  default_timeout_seconds: number; // Default: 300
  enable_agent_telemetry: boolean; // Default: true
  enable_human_in_the_loop: boolean; // Default: true
  directory: Record<string, AgentProfileConfig>;
}
```

---

## 4. Autonomy Tiers & Safety Policies

Each agent operates under an assigned **Autonomy Tier**:

1. **`full_autonomy`**:
   - The agent executes designated tasks without blocking for user confirmation.
   - Limited strictly to read-only or low-impact operations (e.g. searching jobs, parsing job descriptions, drafting resumes).
2. **`supervised_approval`** (Default for high-impact agents):
   - The agent prepares action plans and application payloads, but halts before final execution (e.g. submitting a job application, sending an email to a recruiter).
   - Generates an approval request card in the Command Center dashboard and waits for explicit user confirmation.
3. **`disabled`**:
   - The agent is excluded from all swarm decomposition trees and will not be invoked.

---

## 5. User Interface Controls (`/settings/agents`)

The frontend implementation in [AgentPreferencesPage.tsx](file:///e:/proooo/AUTO%20JOB/apps/desktop/src/features/settings/pages/AgentPreferencesPage.tsx) provides:

- **Global Concurrency Slider**: Configures `max_concurrent_agents` (1–8) with real-time feedback on workstation thread bounds.
- **Category Filter Tabs**: Quick filtering across Orchestration, Recruitment, Automation, Research, Productivity, and Operations.
- **Searchable Agent Directory**: Instant client-side filtering by agent name, ID, or description.
- **Detailed Agent Cards**:
  - Direct toggles for enable/disable state.
  - Autonomy Tier selection dropdown (`Full Autonomy` vs `Requires Approval`).
  - Model assignment dropdown (`Local Default` vs `Cloud Fast / Claude 3.5 Haiku` vs `Cloud Reasoning / Claude 3.5 Sonnet`).
  - Timeout and retry adjustment fields.
- **Truthful Status Attribution**: Badges clearly state that agent runtime dispatch will activate in Stage 12, preventing false claims of live running agents.

---

## 6. Stage 12 & 13 Integration Contracts

Stage 12 (Swarm Orchestration) will interface with `AgentSettings` as follows:

1. **Swarm Init**: The Orchestrator reads `directory` from `/api/v1/settings/agents` to build the agent availability registry.
2. **Task Graph Construction**: Disabled agents (`enabled: false`) are pruned from candidate execution graphs.
3. **Approval Interception**: Before dispatching an action from an agent marked `supervised_approval`, the task runner registers a pending approval record with `POST /api/v1/tasks/{id}/pause-for-approval`.
