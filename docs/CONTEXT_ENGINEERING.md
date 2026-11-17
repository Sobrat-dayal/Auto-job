# AUTONOM Context Engineering & Prompt Budgeting (Stage 15)

## 1. Context Builder Overview

The Context Builder (`services/api/app/memory/retrieval/context_builder.py`) formats retrieved memories into structured prompt blocks for autonomous agents and the unified AI Model Gateway.

Prompt pollution (dumping hundreds of unranked lines into prompts) causes context window bloat, increases inference costs, and induces hallucinations. The Context Builder enforces strict token budgeting and section partitioning.

---

## 2. Structured Section Layout

Memories are segmented into three explicit evidence blocks:

```markdown
### [VERIFIED FACTS & PROFILE EVIDENCE]
- Candidate Technical Skills: 5 years of production Rust backend development [Verification: verified, Source: verified_profile]
- Target Role: Senior Distributed Systems Architect [Verification: user_confirmed, Source: user_statement]

### [REUSABLE PROCEDURES & VALIDATED METHODS]
- Document Extraction Procedure (v1): Multi-stage fallback for text extraction from PDF files [Verification: candidate]

### [PRIOR WORKFLOW EXPERIENCES & LESSONS]
- Workflow Outcome (wf_982): PDF text layer required OCR fallback for scanned header section.
```

---

## 3. Token Budget Management

- **Configurable Limit**: Defaults to 1,500 tokens (adjustable per agent role and model context window).
- **Priority Eviction**: High-confidence verified facts take precedence over episodic notes and unverified claims.
- **Deduplication**: Filters out redundant topics before prompt assembly.
