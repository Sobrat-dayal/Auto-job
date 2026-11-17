# AUTONOM Authorization Policy Schema & System Baselines

## 1. Policy Definition Schema

Authorization policies define declarative governance rules governing what agents are allowed or forbidden from doing. Every policy is modeled via `PolicyDefinition` and persisted in SQLite (`authorization_policies` and `authorization_policy_versions`):

```json
{
  "id": "pol_external_submission_approval",
  "name": "External Job Application Submission Gate",
  "description": "Requires explicit human approval before submitting live job applications to employer ATS platforms.",
  "version": 1,
  "is_enabled": true,
  "is_system": true,
  "subject_scope": "*",
  "category_scope": "recruitment",
  "action_scope": ["recruitment_submit_application", "browser_submit_form"],
  "resource_scope": {
    "unrestricted": true
  },
  "effect": "require_approval",
  "conditions": {
    "max_risk_level": "critical"
  }
}
```

### Schema Attributes

- `id` (string, primary key): Unique policy identifier (e.g. `pol_system_read_baseline`).
- `name` (string): Human-readable name displayed in Settings and Approvals workspace.
- `description` (string): Intent and operational boundary summary.
- `version` (integer): Monotonically increasing version counter for optimistic concurrency.
- `is_enabled` (boolean): Whether the policy is currently active in the evaluation engine.
- `is_system` (boolean): Immutable baseline policies cannot be deleted.
- `subject_scope` (string): Identifies applicable actors:
  - `*`: Applies to all actors (users, agents, workflows).
  - `agent:*`: Applies to any specialist agent.
  - `user:*`: Applies to human operators.
  - Specific agent ID (e.g. `application_agent`).
- `category_scope` (string): Matches permission categories (e.g. `recruitment`, `filesystem`, `*`).
- `action_scope` (array of strings): Specific capability IDs or actions covered by this rule.
- `resource_scope` (object): Granular constraints (paths, origins, job sources).
- `effect` (string): `allow`, `deny`, or `require_approval`.
- `conditions` (object): Contextual predicates such as `max_risk_level`, time of day, or daily rate limits.

---

## 2. Built-in System Baseline Policies

AUTONOM ships with 6 immutable baseline policies loaded at startup:

1. **System Read-Only Baseline (`pol_system_read_baseline`)**:
   - Effect: `ALLOW`
   - Scope: Low-risk analytical operations (e.g. skill matching, job parsing, AST linting).
2. **Moderate Synthesis Baseline (`pol_moderate_synthesis_baseline`)**:
   - Effect: `ALLOW`
   - Scope: Local text drafting, resume tailoring, and test generation.
3. **Credential Access Strict Isolation (`pol_credential_protection`)**:
   - Effect: `DENY`
   - Scope: Direct extraction of raw API keys, passwords, and tokens by specialist agents.
4. **External Job Application Submission Gate (`pol_external_submission_approval`)**:
   - Effect: `REQUIRE_APPROVAL`
   - Scope: ATS form submissions, live job applications.
5. **Outbound Communications Gate (`pol_external_communications_approval`)**:
   - Effect: `REQUIRE_APPROVAL`
   - Scope: Outbound email transmissions, messaging sends.
6. **Destructive Operations Gate (`pol_destructive_filesystem_approval`)**:
   - Effect: `REQUIRE_APPROVAL`
   - Scope: File deletion, directory removal, database wipe.

---

## 3. Optimistic Concurrency & Audit Versioning

Policy updates verify `expected_version` before committing changes to SQLite. Every modification creates a record in `authorization_policy_versions` capturing the full snapshot, modified by identity, and modification timestamp.
