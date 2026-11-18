# AUTONOM Recruitment Policy Engine

## Stage 25 of 50 — Technical Reference

---

### 10-Level Precedence Hierarchy

The core evaluation loop executes an immutable 10-tier rule ladder. Higher-priority rules immediately veto evaluation, returning deterministic decision outcomes before lower-level preferences are even inspected.

| Level | Invariant Rule | Decision Outcome | Description |
|---|---|---|---|
| **Level 1** | Emergency Stop Engaged | `PROHIBITED_BY_POLICY` | Stage 14 kill-switch halts all autonomous activities across agents. |
| **Level 2** | Security & Auth Invariants | `PROHIBITED_BY_POLICY` | Violations of DPAPI vault integrity, tenant boundaries, or permissions. |
| **Level 3** | Explicit Denials & Revocations | `PROHIBITED_BY_POLICY` | Previously recorded administrative denials or user revocations. |
| **Level 4** | Platform / Source Restrictions | `PROHIBITED_BY_POLICY` | Blocked job boards, unauthorized scraping domains, recruiter spam. |
| **Level 5** | Sensitive Legal & Safeguards | `NEEDS_REVIEW` | Clearance requirements, visa attestations, or non-compete clauses. |
| **Level 6** | Employer Blocklists | `PROHIBITED_BY_POLICY` | Current employers, competitor blocks, restricted parent companies. |
| **Level 7** | Hard Eligibility Failures | `INELIGIBLE` | Degree level shortfalls, experience year limits, work auth barriers. |
| **Level 8** | Hard Career Preferences | `REJECTED_BY_PREFERENCE` | Salary below floor, disallowed arrangements (e.g. onsite), excluded cities. |
| **Level 9** | Scoped Standing Grants | `PROCEED_WITH_CONDITIONS` | Permitted preparation within daily quotas without interactive prompts. |
| **Level 10** | Soft Preference Ranking | `PROCEED` | Multi-dimensional scoring (0.0 to 100.0) based on weighted affinities. |

---

### Evaluation Data Flow

```
JobOpportunityContext
        │
        ▼
Level 1: Emergency Stop Check? ───────► YES ──► PROHIBITED (Level 1)
        │ NO
        ▼
Level 5: Sensitive Legal Trigger? ────► YES ──► NEEDS_REVIEW (Level 5)
        │ NO
        ▼
Level 6: Blocked Employer Match? ─────► YES ──► PROHIBITED (Level 6)
        │ NO
        ▼
Level 7: Hard Eligibility Audit? ─────► FAIL ─► INELIGIBLE (Level 7)
        │ PASS
        ▼
Level 8: Hard Career Preference? ─────► FAIL ─► REJECTED (Level 8)
        │ PASS
        ▼
Level 9/10: Standing Grant & Scoring ──► PROCEED / PROCEED_WITH_CONDITIONS
```
