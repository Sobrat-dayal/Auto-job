# AUTONOM — Creative, Communication, Coding, Research, & Automation Agents Architecture

## 1. Overview

In addition to Recruitment, Computer Control, and Productivity, AUTONOM deploys specialist agents across **Coding, Research, Market Intelligence, Creative Design, Messaging, and Workflow Automation**.

---

## 2. Coding & Software Agent (`coding_agent`)

- **Category**: Coding | **Availability**: Operational
- **Role**: Software engineering assistant focused on static code inspection, architectural explanations, and automated unit test generation.
- **Key Capabilities**:
  - `code_explain`: Breaks down complex code snippets, explains algorithmic complexity ($O(n)$ notation), and clarifies data flow.
  - `code_review_static`: Scans Python and TypeScript code for anti-patterns, security vulnerabilities (hardcoded credentials, SQL injection risks), and missing type annotations.
  - `code_generate_tests`: Generates production-ready `pytest` or `vitest` test suites for target functions.
- **End-to-End Collaboration**:
  Tested in Stage 13 via a 3-step collaborative DAG: static analysis -> test generation -> verifier contract review.

---

## 3. Research & Knowledge Agents

### 3.1 Research & Knowledge Agent (`research_agent`)
- **Category**: Research | **Availability**: Operational
- **Role**: Synthesizes unstructured information across multiple documentation and text sources.
- **Key Capabilities**:
  - `research_summarize_sources`: Produces cohesive executive summaries from multiple raw texts.
  - `research_extract_evidence`: Pulls verifiable facts, citations, and quantitative claims from source materials.
  - `research_compare_sources`: Highlights consensus, conflicting claims, and coverage gaps across documents.

### 3.2 Market Intelligence Agent (`market_intelligence_agent`)
- **Category**: Research | **Availability**: Operational
- **Role**: Analyzes market compensation trends, hiring demand patterns, and employer benchmark metrics.
- **Key Capabilities**:
  - `market_analyze_supplied_data`: Computes percentile distributions, salary benchmarks, and regional variance across supplied industry datasets.

---

## 4. Creative & Messaging Agents

### 4.1 Creative Design Agent (`creative_agent`)
- **Category**: Creative | **Availability**: Limited (Scene and layout specifications operational; image generation rendering planned)
- **Role**: Generates multimodal design briefs, layout specifications, and color palette tokens.
- **Key Capabilities**:
  - `creative_scene_specification`: Creates detailed composition, lighting, aspect ratio, and asset descriptions for graphical media workflows.

### 4.2 Communication & Messaging Agent (`messaging_agent`)
- **Category**: Communication | **Availability**: Operational
- **Role**: Classifies incoming messages (urgency, sentiment, category) and drafts polite, concise responses.
- **Key Capabilities**:
  - `msg_classify_message`: Categorizes messages (Action Required, Informational, Inquiry, Spam) with urgency ratings.
  - `msg_draft_response`: Formulates professional, contextual replies adhering to user tone preferences.

---

## 5. Workflow Automation Agent (`workflow_automation_agent`)

- **Category**: Automation | **Availability**: Operational
- **Role**: Generates and validates multi-agent DAG configurations, recurring schedules, and pipeline schemas.
- **Key Capabilities**:
  - `workflow_propose_template`: Constructs valid JSON/YAML DAG templates for common enterprise and recruitment workflows.
  - `workflow_validate_config`: Verifies workflow configurations against schema constraints, ensuring cycle-free DAGs and valid agent mappings.
