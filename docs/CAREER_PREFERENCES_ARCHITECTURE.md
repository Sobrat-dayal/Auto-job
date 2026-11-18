# AUTONOM Career Preferences Architecture

## Stage 25 of 50 — Recruitment Intelligence Foundation (Phase 5 Conclusion)

---

### Executive Overview

The **Career Preference Intelligence Engine** is the governance and steering subsystem of AUTONOM's recruitment stack. It sits above the profile (Stage 21), code evidence (Stage 22), resume intelligence (Stage 23), and application writing (Stage 24) engines, defining:
1. **What the applicant wants**: Target roles, industries, company tiers, location boundaries, and compensation goals.
2. **What the applicant can truthfully claim**: Objective qualification constraints audited against verified claims.
3. **What agents are permitted to execute autonomously**: Scoped standing grants, safety budgets, and human sign-off gates.

```
+========================================================================================+
|                       STAGE 25: RECRUITMENT POLICY & DECISION ENGINE                  |
+========================================================================================+
|                                                                                        |
|  +------------------------+  +------------------------+  +--------------------------+  |
|  |   CAREER PREFERENCES   |  |   JOB ELIGIBILITY      |  |  AUTOMATION PERMISSIONS  |  |
|  |      (Applicant        |  |     (Verified Facts    |  |     (Stage 14 Scoped     |  |
|  |     Aspirations)       |  |      & Claims)         |  |      Standing Grants)    |  |
|  +-----------+------------+  +-----------+------------+  +------------+-------------+  |
|              |                           |                            |                |
|              +--------------------+      |     +----------------------+                |
|                                   |      |     |                                       |
|                                   v      v     v                                       |
|                       +----------------------------------------+                       |
|                       |   10-Level Precedence Engine           |                       |
|                       |   - Hard Vetoes                        |                       |
|                       |   - Precedence Invariants              |                       |
|                       |   - Soft Ranking (0 - 100)             |                       |
|                       +-------------------+--------------------+                       |
|                                           |                                            |
|                                           v                                            |
|                       +----------------------------------------+                       |
|                       |  Deterministic Recruitment Decision    |                       |
|                       |  - Outcome: Proceed / Review / Reject  |                       |
|                       |  - Shared Multi-Agent Budget Check     |                       |
|                       +----------------------------------------+                       |
+========================================================================================+
```

---

### Core Principles

1. **Strict Separation of Aspirations, Facts, and Permissions**:
   - An applicant may want a Senior ML Engineer role (preference), but if their verified experience is 1 year in backend web development (fact), AUTONOM flags an eligibility violation rather than hallucinating machine learning achievements.
   - An agent may discover an eligible job (facts), but cannot submit without explicit permission (Stage 14 authorization grant).
2. **Multi-Strategy Isolation**:
   - Applicants can define multiple orthogonal strategies (e.g. *Backend Distributed Systems*, *Cloud Platform Engineering*, *AI/ML Infrastructure*). Exactly one strategy is active at any time, allowing swift context pivots without policy clobbering.
3. **Immutability & Cryptographic Audit Trails**:
   - Every policy update generates a SHA-256 digested version snapshot (`PolicyVersionSnapshot`) preserving historical decision context.
