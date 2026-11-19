# Qualification Gap Intelligence & Remediation

## 1. Gap Taxonomy & Severity Levels
Gaps represent identified deficiencies between job prerequisites and confirmed profile evidence:

| Gap Type | Description | Trigger | Default Severity |
| :--- | :--- | :--- | :--- |
| `MissingMandatorySkill` | Absence of required core skill | Mandatory skill not evidenced in profile | `BLOCKING` |
| `DurationDeficit` | Tenure is below mandated years | Candidate has 2 yrs, job requires 5 yrs | `MODERATE` / `BLOCKING` |
| `MissingPreferredSkill` | Absence of desirable bonus skill | Preferred skill not evidenced | `MODERATE` / `MINOR` |
| `RelatedOnly` | Conceptual relative without direct proof | Vue claimed, React required | `MODERATE` |
| `MissingEvidence` | Skill mentioned informally without verification | Unconfirmed claim | `CRITICAL_REVIEW` |
| `EducationDeficit` | Degree level or status incompatible | Enrolled student vs completed | `BLOCKING` |

## 2. Grounded Remediation Suggestions
- Every gap produces an actionable suggestion tailored to the applicant's existing portfolio:
  - For `RelatedOnly`: Recommends highlighting transferable architectural concepts or building a verified targeted project.
  - For `DurationDeficit`: Recommends expanding project contributions or open-source tenure.
  - For `MissingEvidence`: Suggests connecting GitHub repository evidence (Stage 22) or submitting profile updates.
- Gaps are suppressed when alternative logic groups (`OR`) are satisfied by other members.
