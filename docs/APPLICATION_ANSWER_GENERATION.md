# Application Answer Generation

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

The **Answer Generation Subsystem** transforms parsed screening questions into truthful, high-quality, formatted responses. Unlike generic chat models that hallucinate credentials or inflate metrics, AUTONOM grounds every assertion in verified claims from Stage 21, GitHub repositories from Stage 22, and approved bullet points from Stage 23.

---

### Answer States & Lifecycle

Every generated answer moves through explicit lifecycle states (`AnswerState`):

```
                   +------------------------+
                   |    Question Parsed     |
                   +-----------+------------+
                               |
               +---------------+---------------+
               |                               |
       [Requires User]                 [Direct Profile Match]
               |                               |
               v                               v
+-----------------------------+  +-------------------------------+
| requires_user_confirmation  |  |      available_confirmed      |
| requires_user_attestation   |  | available_evidence_supported  |
| sensitive_optional          |  |    available_user_reported    |
+--------------+--------------+  +---------------+---------------+
               |                                 |
               |                                 v
               |                 +-------------------------------+
               |                 |        draft_generated        |
               |                 +---------------+---------------+
               |                                 |
               +---------------+                 |
                               |                 |
                               v                 v
                       +---------------------------------+
                       |         User Review             |
                       +----------------+----------------+
                                        |
                         +--------------+--------------+
                         |                             |
                         v                             v
                 +---------------+             +---------------+
                 |   approved    |             |   rejected    |
                 +---------------+             +---------------+
```

- **`available_confirmed`**: Answer derived directly from verified canonical profile fields (e.g. graduation year, legal name).
- **`available_evidence_supported`**: Answer supported by concrete GitHub or portfolio evidence (e.g. Rust concurrency project).
- **`available_user_reported`**: Fact reported by the user but lacking formal documentary evidence.
- **`draft_generated`**: Formatted long-form response prepared for user inspection.
- **`requires_user_confirmation`**: Sensitive or subjective inquiry requiring direct human confirmation.
- **`requires_user_attestation`**: Legal attestation or declaration requiring human sign-off.
- **`missing_information`**: Required facts are completely absent from the applicant's profile.
- **`conflicting_information`**: Conflicting data points discovered across profile versions or evidence items.

---

### Behavioral Questions & The STAR Framework

For situational and behavioral prompts ("Tell me about a time you resolved a conflict", "Describe your most challenging architectural bug"), the engine organizes responses using the structured **STAR** methodology:

1. **Situation**: Establishes context, company, and project scale derived from verified employment records.
2. **Task**: Defines the explicit technical or organizational objective.
3. **Action**: Details specific actions taken by the applicant, referencing verified skills and technologies.
4. **Result**: Highlights verified outcomes, latency improvements, reliability metrics, or delivered milestones.

---

### Technical Knowledge & Production Experience

When responding to technical inquiries (e.g. "Do you have experience with Kubernetes in production?"):
- The engine checks whether the skill is listed in canonical skills.
- It examines whether the skill is backed by verified employment experience or repository contributions.
- If the skill exists only in academic or personal projects, the engine explicitly states:
  > *"I have hands-on experience building and deploying containerized applications with Kubernetes in development and staging environments, though my production enterprise experience has primarily focused on Docker and ECS."*
- This level of honesty prevents catastrophic interview mismatches and builds trust with hiring teams.

---

### Character and Word Limit Enforcement

Application forms enforce strict constraints (e.g. 150 words or 500 characters). AUTONOM incorporates sentence-boundary-preserving condensation algorithms:
- Computes character count with and without whitespace.
- Trims peripheral filler while preserving all verified factual assertions and technical keywords.
- Flags answers exceeding hard portal limits with immediate visual indicators in the desktop interface.
