# AUTONOM — Productivity Specialist Agents Architecture

## 1. Overview

AUTONOM includes **3 Productivity Specialist Agents** designed to assist users with core document drafting, financial and tabular analysis, spreadsheet formulas, and executive presentation preparation.

All three productivity agents are **fully operational** in Stage 13, featuring both AI Gateway LLM support and rich deterministic fallback algorithms.

---

## 2. The 3 Productivity Specialists

### 2.1 Document & Report Agent (`document_agent`)
- **Category**: Productivity | **Availability**: Operational
- **Role**: Assists in structural document design, professional report drafting, technical writing, and text refinement.
- **Key Capabilities**:
  - `doc_generate_outline`: Generates structured document outlines with hierarchical headings, estimated word counts, and section briefs.
  - `doc_draft_report`: Synthesizes comprehensive reports from raw source notes, research findings, and applicant portfolios.
  - `doc_rewrite_text`: Refines, condenses, or adapts tone (executive, formal, concise) for existing content.

### 2.2 Spreadsheet Analysis Agent (`spreadsheet_agent`)
- **Category**: Productivity | **Availability**: Operational
- **Role**: Analyzes tabular datasets, computes summary statistics (sums, averages, counts, distributions), and explains or constructs complex Excel/Sheets formulas.
- **Key Capabilities**:
  - `sheet_summarize_tabular`: Computes statistical summaries, identifies column data types, detects missing values, and pinpoints numerical anomalies.
  - `sheet_explain_formula`: Breaks down complex nested formulas (e.g., `INDEX/MATCH`, `XLOOKUP`, `SUMIFS`, lambda functions) into plain English descriptions.

### 2.3 Presentation Agent (`presentation_agent`)
- **Category**: Productivity | **Availability**: Operational
- **Role**: Plans slide structures, speaker notes, and visual presentation narratives for business, technical, and interview reviews.
- **Key Capabilities**:
  - `pres_generate_outline`: Generates structured slide-by-slide outlines including slide titles, bullet points, visual layout suggestions, and transition ideas.
  - `pres_draft_speaker_notes`: Drafts concise, professional speaker notes and timing allocations tailored for presentation delivery.

---

## 3. Deterministic Fallbacks & Data Safety

To ensure productivity workflows never block when external LLM endpoints are unavailable or rate-limited:
1. **Outline Synthesis**:
   If LLM inference is disabled, the deterministic engine extracts semantic clusters and headings from input text, producing standard executive outlines.
2. **Tabular Math**:
   Tabular summaries are computed using Python native mathematics rather than prompting an LLM to guess sums and averages, preventing mathematical hallucination.
3. **Context Privacy**:
   Productivity agents adhere to `AgentContextPolicy` with `allow_credentials = False`, ensuring sensitive credentials from other workspaces are never exposed during document drafting.
