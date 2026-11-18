# AUTONOM Policy Simulator Architecture

## Stage 25 of 50 — Zero-Side-Effect Sandbox

---

### Objectives

The **Policy Simulator** allows the applicant or developer to test hypothetical or newly discovered job opportunities against the active policy engine without mutating live database records, consuming application budgets, or triggering external agent calls.

---

### Simulation Interface

```
POST /api/v1/recruitment/policies/simulate
{
  "synthetic_job": {
    "title": "Senior Distributed Systems Engineer",
    "employer_name": "TechCorp Global",
    "work_arrangement": "remote",
    "compensation_min": 145000.0,
    "location_city": "San Francisco",
    "required_skills": ["Go", "Kubernetes", "gRPC"],
    "required_experience_years": 4,
    "work_authorization_required": true
  },
  "strategy_override": null,
  "applicant_profile_id": null
}
```

---

### Response & Explanatory Output

The simulator returns:
1. **Decision Verdict**: `proceed`, `needs_review`, `rejected_by_preference`, `ineligible`, or `prohibited_by_policy`.
2. **Precedence Ladder Step**: The exact level (1 to 10) that triggered the decision.
3. **Primary Rationale**: Human-readable sentence explaining why the rule fired.
4. **Factual Qualification Assessment**: Detailed breakdown of education match, verified experience years vs required, skill overlap percentage, and work authorization check.
5. **Soft Score Breakdown**: Affinity score between 0.0 and 100.0.
