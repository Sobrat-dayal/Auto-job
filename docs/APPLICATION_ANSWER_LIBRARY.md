# Reusable Answer Library & Freshness Monitoring

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

Job applicants frequently encounter identical or closely related questions across different job applications (e.g. "Describe your leadership style", "What are your salary expectations?", "Explain your experience with distributed consensus"). The **Reusable Answer Library Subsystem** stores, organizes, versions, and monitors approved answers for reuse across applications while strictly preventing cross-employer data leaks.

---

### Parameterized Templates

Approved answers can be stored as parameterized templates containing dynamic variables:

```markdown
Over the past {{years_of_experience}} years, I have architected and maintained distributed systems with an emphasis on {{primary_tech_stack}}. At {{recent_company}}, I led the migration of legacy monolith services into asynchronous microservices, reducing p99 latency by 35%. My approach focuses on test-driven development, comprehensive observability, and zero-downtime deployment pipelines.
```

Supported substitution tokens include:
- `{{years_of_experience}}`: Non-overlapping years calculated from verified employment records.
- `{{primary_tech_stack}}`: Top technical skills sorted by proficiency and verified projects.
- `{{recent_company}}`: Most recent verified employer.
- `{{target_company}}`: Employer name for the current target application.
- `{{target_role}}`: Position title for the current target application.
- `{{degree_title}}`: Canonical degree name from verified education records.

---

### Cross-Employer Leak Prevention

Reusing previously submitted answers carries significant risk if company names or confidential details leak across applications (e.g. submitting a cover letter to Apple that mentions "excited to join Google").

The Answer Library incorporates active sanitization filters (`sanitize_for_reuse`):
1. **Target Organization Stripping**: Scans text for previous employer or company references and replaces them with parameterized placeholders.
2. **Proprietary Nomenclature Detection**: Flags internal tool names, private codenames, or unverified project metrics.
3. **Interactive Leak Audit**: Renders a side-by-side comparison preview before an archived answer is applied to a new application package.

---

### Freshness Monitoring Lifecycle

Answers in the library are tied to profile version hashes. When the canonical applicant profile changes (e.g. candidate adds a new job, completes a certification, or updates skills), the Answer Library evaluates freshness:

```
               [Canonical Profile Updated]
                           |
                           v
        +-------------------------------------+
        |  AnswerLibraryManager.check_freshness|
        +------------------+------------------+
                           |
              +------------+------------+
              |                         |
       [Facts Unchanged]         [Underlying Facts Changed]
              |                         |
              v                         v
       +--------------+          +------------------------+
       |    fresh     |          |        outdated        |
       +--------------+          | requires_revalidation  |
                                 +------------------------+
                                        |
                                        v
                                 [Flagged in UI]
                                 [Prompt User to Update]
```

- **`fresh`**: The underlying facts (tenure, skills, company) match current canonical data.
- **`outdated`**: Profile tenure or graduation dates have advanced, requiring parameter re-evaluation.
- **`superseded`**: A newer, more comprehensive answer has been approved for this category.
- **`requires_revalidation`**: A fundamental claim referenced by the answer was invalidated or removed from the profile.

---

### Answer Library Storage Schema

```typescript
export interface AnswerLibraryEntry {
  id: string;
  owner_id: string;
  title: string;
  category: QuestionCategory;
  parameterized_template: string;
  sample_resolved_text: string;
  answer_type: AnswerType;
  tags: string[];
  usage_count: number;
  last_used_at?: string | null;
  created_at: string;
  updated_at: string;
  profile_snapshot_id?: string | null;
  is_archived: boolean;
}
```
