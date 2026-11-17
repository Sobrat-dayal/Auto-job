# AUTONOM Recruitment Authorization Governance

## 1. Multi-Tier Recruitment Safety Gates

AUTONOM's primary flagship application is autonomous job search and recruitment coordination. The recruitment workflow enforces strict authorization boundaries at every phase of the pipeline:

```
  1. Discovery & Scraping ──► Allowed Sources (LinkedIn, Greenhouse, Lever, Workday)
             │
             ▼
  2. Job Matching ─────────► Excluded Companies & Minimum Match Score Filters
             │
             ▼
  3. Resume Tailoring ─────► Moderate Synthesis Baseline (Local Markdown Drafting)
             │
             ▼
  4. Screening Questions ──► Sensitive Questions Escalation Check
             │                ├── Salary / Work Auth? Auto-Draft from Profile.
             │                └── Criminal History / Drug Screen? Escalates to Human Sign-Off.
             ▼
  5. Live Application ─────► MANDATORY Human-in-the-Loop Approval Gate
             │
             ▼
  6. Recruiter Reply ──────► Outbound Communications Gate (Approval Required)
```

---

## 2. Sensitive Screening Question Escalation

Screening questions extracted from job application forms are categorized into standard vs. sensitive:
- **Standard**: Technical questions, education dates, LinkedIn URLs.
- **Sensitive**: Criminal background history, drug testing consent, equity/visa sponsorship requirements, non-compete agreements.
Any question containing sensitive keywords (`criminal`, `convicted`, `drug test`, `background check`, `clearance`) automatically escalates to `REQUIRE_APPROVAL` even if a standing application grant exists.

---

## 3. Excluded Companies & Minimum Match Thresholds

Policy resource scopes enforce employer restrictions:
```json
{
  "excluded_companies": ["CurrentEmployerCorp", "CompetitorLLC"],
  "min_match_score": 75.0,
  "allowed_sources": ["greenhouse", "lever", "workday"]
}
```
If an agent discovers an otherwise lucrative role at an excluded company, the scope evaluator (`matches_resource_scope`) rejects the action prior to application drafting.
