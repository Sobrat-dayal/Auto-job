# AUTONOM Applicant Profile Data Quality & Completeness Engine (Stage 21)

## 1. Overview

The Data Quality Engine (`DataQualityEngine`) performs deterministic evaluation of profile completeness, internal consistency, and recruitment readiness. It guarantees that an applicant profile has sufficient verified information before automated recruitment agents attempt job matching or application submissions.

---

## 2. Completeness Scoring Algorithm

The completeness score (0–100%) is calculated across weighted profile categories:

| Category | Weight | Evaluation Criteria |
| :--- | :--- | :--- |
| **Identity & Headline** | 20% | `display_label`, `headline`, `summary` present and descriptive |
| **Contact Information** | 15% | `primary_email`, `phone`, `city`, `country` present |
| **Education** | 20% | At least 1 verified academic degree with institution and graduation date |
| **Skills Taxonomy** | 20% | At least 3 categorized skills with assigned proficiency levels |
| **Experience / Projects**| 15% | At least 1 employment record or 1 technical project record |
| **Evidence Provenance** | 10% | At least 1 verified document in the Evidence Vault backing claims |

---

## 3. Recruitment Readiness Checks

A profile is flagged as `is_recruitment_ready: true` only if all mandatory conditions are satisfied:
1. `contact.legal_name` is populated.
2. `contact.primary_email` is valid RFC 5322.
3. At least 1 `EducationRecord` exists.
4. At least 3 `SkillItem` records exist.
5. At least 1 `EmploymentRecord` OR 1 `ProjectRecord` exists.
6. `completeness_score >= 60.0`.

---

## 4. Quality Issue Codes & Severities

The engine reports issues with structured codes and remediation guidance:

| Code | Severity | Description | Suggested Fix |
| :--- | :--- | :--- | :--- |
| `MISSING_EMAIL` | `ERROR` | Primary contact email is missing | Enter a valid contact email in the Identity tab |
| `MISSING_LEGAL_NAME` | `ERROR` | Legal name is missing | Enter applicant legal name |
| `MISSING_EDUCATION` | `WARNING` | No education degrees recorded | Add completed or in-progress degree |
| `INSUFFICIENT_SKILLS` | `WARNING` | Less than 3 technical skills | Add relevant technical skills with proficiency |
| `FUTURE_GRADUATION_NOT_MARKED_ENROLLED` | `WARNING` | End date is in the future but marked completed | Update status to `in_progress` |
| `UNBACKED_CLAIMS` | `INFO` | Claims lack supporting vault evidence | Upload resume, diploma, or certificate to Evidence Vault |
| `MISSING_SUMMARY` | `INFO` | Career narrative summary is empty | Write a brief executive career summary |
