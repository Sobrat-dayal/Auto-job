# AUTONOM — Specialist AI Agent Catalog

## 1. Overview

AUTONOM features 24 logical AI agents organized into 9 functional domains. Each agent possesses a formal manifest detailing its operational status, registered capabilities, model requirements, and context isolation policy.

### Availability State Summary

- **Operational**: Fully functional with local deterministic engines and AI Gateway inference.
- **Limited**: Operational for analysis, drafting, and planning; external network/system mutations are planned for future integration stages.
- **Planned**: Agent definition and capability contracts are established; execution engine arrives in later stages.

---

## 2. Master Agent Table

| # | Agent ID | Agent Name | Category | Availability | Primary Capabilities |
|---|---|---|---|---|---|
| 1 | `supervisor` | Supervisor Agent | Core Orchestration | Operational | Goal decomposition, multi-agent supervision, plan review |
| 2 | `planner` | Planning Agent | Core Orchestration | Operational | DAG construction, dependency analysis, milestone planning |
| 3 | `router` | Task Router Agent | Core Orchestration | Operational | Agent capability matching, load balancing, cost-aware dispatching |
| 4 | `verifier` | Verification Agent | Core Orchestration | Operational | Contract verification, schema validation, output quality review |
| 5 | `recovery` | Recovery Agent | Core Orchestration | Operational | Failure triage, alternative strategy generation, self-healing |
| 6 | `job_discovery_agent` | Job Discovery Agent | Recruitment | Limited | `recruitment_parse_search_criteria`, `recruitment_normalize_job_listing` |
| 7 | `job_matching_agent` | Job Matching Agent | Recruitment | Operational | `recruitment_match_skills`, `recruitment_extract_job_requirements` |
| 8 | `resume_agent` | Resume & Tailoring Agent | Recruitment | Operational | `recruitment_draft_resume_bullets`, `recruitment_match_skills` |
| 9 | `application_agent` | Application Agent | Recruitment | Limited | `recruitment_classify_application_fields` |
| 10 | `recruitment_comms_agent` | Recruitment Comms Agent | Recruitment | Limited | `recruitment_summarize_conversation`, `recruitment_draft_recruiter_reply` |
| 11 | `interview_prep_agent` | Interview Prep Agent | Recruitment | Operational | `recruitment_generate_interview_questions` |
| 12 | `browser_agent` | Browser Automation Agent | Computer | Limited | `browser_plan_navigation` |
| 13 | `windows_computer_agent` | Windows Computer Agent | Computer | Limited | `desktop_plan_operation` |
| 14 | `visual_grounding_agent` | Visual Grounding Agent | Computer | Limited | `visual_inspect_image_metadata` |
| 15 | `structural_ui_agent` | Structural UI Agent | Computer | Limited | `structural_parse_accessibility_tree` |
| 16 | `coding_agent` | Coding & Software Agent | Coding | Operational | `code_explain`, `code_review_static`, `code_generate_tests` |
| 17 | `research_agent` | Research & Knowledge Agent | Research | Operational | `research_summarize_sources`, `research_extract_evidence`, `research_compare_sources` |
| 18 | `market_intelligence_agent`| Market Intelligence Agent| Research | Operational | `market_analyze_supplied_data` |
| 19 | `document_agent` | Document & Report Agent | Productivity | Operational | `doc_generate_outline`, `doc_draft_report`, `doc_rewrite_text` |
| 20 | `spreadsheet_agent` | Spreadsheet Analysis Agent | Productivity | Operational | `sheet_summarize_tabular`, `sheet_explain_formula` |
| 21 | `presentation_agent` | Presentation Agent | Productivity | Operational | `pres_generate_outline`, `pres_draft_speaker_notes` |
| 22 | `creative_agent` | Creative Design Agent | Creative | Limited | `creative_scene_specification` |
| 23 | `messaging_agent` | Communication & Messaging Agent | Communication | Operational | `msg_classify_message`, `msg_draft_response` |
| 24 | `workflow_automation_agent`| Workflow Automation Agent | Automation | Operational | `workflow_propose_template`, `workflow_validate_config` |

*(Note: `job_search_specialist` is retained as a legacy backward-compatible alias mapped to `job_discovery_agent`.)*

---

## 3. Domain Details

### 3.1 Core Orchestration (5 Agents)
- **Role**: Coordinates all sub-tasks, structures execution graphs, routes work to specialists, checks quality against contracts, and recovers from edge cases.
- **Hardware Profile**: High reasoning effort, zero temperature for deterministic planning, local-first model routing (`qwen2.5:7b` / `gemini-1.5-pro`).

### 3.2 Recruitment Automation (6 Agents)
- **Role**: Powers the end-to-end recruitment lifecycle from job discovery and parsing to qualification scoring, resume tailoring, form classification, email communication, and mock interview generation.
- **Privacy Policy**: Strictly isolates user contact details and credentials. Resume tailoring is performed using verified candidate facts only, strictly prohibiting hallucinations.

### 3.3 Computer & OS Operations (4 Agents)
- **Role**: Translates user goals into planned UI operations across web browsers and native Windows applications using visual grounding and accessibility trees.
- **Safety Policy**: Currently in `limited` status. Execution engines only produce structured navigation plans, action sequences, and bounding-box calculations. No unauthorized OS input injection is performed without human confirmation.

### 3.4 Coding & Engineering (1 Agent)
- **Role**: Static code analysis, security auditing, explanation, test generation, and multi-file refactoring suggestions.
- **Safety Policy**: Read-only static analysis and test generation; does not execute untrusted binaries outside sandbox environments.

### 3.5 Research & Intelligence (2 Agents)
- **Role**: Ingests, compares, and summarizes structured knowledge sources, market compensation datasets, and technical documentation.

### 3.6 Productivity (3 Agents)
- **Role**: Content drafting, outline synthesis, tabular financial data analysis, spreadsheet formula explanation, and presentation slide deck authoring.

### 3.7 Creative & Communication (2 Agents)
- **Role**: Generates multimodal design briefs, layout specifications, drafts contextual replies for incoming messages, and categorizes communication urgency.

### 3.8 Workflow Automation (1 Agent)
- **Role**: Proposes multi-agent execution templates, configures scheduled pipelines, and verifies recurring workflow schemas.
