# AUTONOM Applicant Education & Employment Experience (Stage 21)

## 1. Overview

Education and work experience form the core qualifications used by AUTONOM's recruitment intelligence pipeline. Stage 21 structures these records into queryable, verified entities with granular metric statements and technological attribution.

---

## 2. Academic Education Model

### 2.1 Schema Attributes
- `institution`: Accredited university or educational institution.
- `degree`: Level (Associate, Bachelor's, Master's, Doctorate, Diploma).
- `field_of_study`: Major specialization (e.g., Computer Science, Electrical Engineering).
- `academic_status`: `completed`, `in_progress`, `deferred`, `incomplete`.
- `start_date` & `end_date`: ISO 8601 date strings (`YYYY-MM` or `YYYY-MM-DD`).
- `gpa` & `gpa_scale`: Numeric GPA with explicit denominator (e.g. 3.92 on a 4.0 scale).
- `coursework`: Key academic subjects relevant to job applications.
- `distinctions`: Honors, Dean's List, summa cum laude, fellowships.
- `evidence_refs`: Foreign keys pointing to transcripts or diplomas in the Evidence Vault.

### 2.2 Quality & Validation Rules
- `end_date` must not precede `start_date`.
- If `end_date` is in the future and `academic_status` is `completed`, the Data Quality Engine raises a `FUTURE_GRADUATION_NOT_MARKED_ENROLLED` warning.
- `gpa` must not exceed `gpa_scale`.

---

## 3. Employment Experience Model

### 3.1 Schema Attributes
- `employer`: Organization or company name.
- `job_title`: Position held.
- `employment_type`: `full_time`, `part_time`, `contract`, `internship`, `freelance`.
- `work_arrangement`: `remote`, `hybrid`, `onsite`.
- `start_date` & `end_date`: `YYYY-MM`. If `is_current: true`, `end_date` is null.
- `responsibilities`: List of narrative duties.
- `technologies`: Array of tools, frameworks, and programming languages actively used in the role.
- `achievements`: Structured quantifiable achievements (`AchievementItem`):
  - `statement`: Narrative description of impact (e.g., "Reduced latency by 45%").
  - `metric_value`: Explicit quantitative figure (e.g., "45%").
  - `metric_unit`: Metric category (e.g., "latency", "revenue", "uptime").

### 3.2 Timeline Consistency Checks
- Overlapping full-time positions generate an informational check in the Data Quality Engine.
- Missing achievements on experiences exceeding 1 year trigger a completeness recommendation.
