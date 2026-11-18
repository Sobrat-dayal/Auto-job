# AUTONOM Autonomous Application Authorization

## Stage 25 of 50 — Scoped Standing Grants & Revocation

---

### Standing Grants Architecture

Scoped standing grants (`StandingGrantRecord`) bridge Stage 14 (Authorization Engine) with Stage 25 (Recruitment Policy). They allow specialist agents to perform high-frequency operations without prompting the user on every iteration.

```
+-------------------------------------------------------+
|               Standing Grant Data Structure           |
+-------------------------------------------------------+
| id: string                                            |
| grantee_role: "application_agent" | "resume_agent"   |
| scope: "prepare_application" | "tailor_resume"        |
| max_actions_per_day: number                           |
| actions_taken_today: number                           |
| conditions: Record<string, any>                       |
| issued_at: ISO-8601                                   |
| is_revoked: boolean                                   |
| revocation_reason?: string                            |
+-------------------------------------------------------+
```

---

### Verification Protocol

Before any agent executes an action:
1. **Scope Check**: Does the agent possess an active grant matching `(grantee_role, action)`?
2. **Quota Check**: Has `actions_taken_today` reached `max_actions_per_day`?
3. **Revocation Check**: Is `is_revoked: false`?
4. **Precedence Check**: Does the target job pass Levels 1 through 8 with zero hard vetoes?

If all conditions hold, the action proceeds under `PROCEED_WITH_CONDITIONS`. If any check fails, the action is denied or queued for human review.
