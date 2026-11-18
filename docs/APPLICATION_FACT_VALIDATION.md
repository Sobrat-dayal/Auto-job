# Application Fact Validation & Hallucination Prevention

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

AUTONOM's **Zero-Hallucination Mandate** requires that all material statements in cover letters, screening answers, and portfolio narratives are strictly grounded in canonical applicant profile records or verified external evidence. The **WritingFactValidator** acts as an automated compliance auditor, evaluating every generated sentence before it is presented to the user or included in an application package.

---

### Verification Dimensions

The validator audits documents across 5 key dimensions:

1. **Employment History & Titles**:
   - Compares job titles, company names, and date ranges against verified `EmploymentRecord` entries.
   - Detects title inflation (e.g. promoting "Software Engineer" to "Staff Architect").

2. **Skill Assertions & Tooling**:
   - Scans text for technical buzzwords and frameworks.
   - Checks presence in verified `SkillItem` list or attributed GitHub repositories.
   - Rejects unverified technologies.

3. **Numerical Metrics & Performance Claims**:
   - Extracts numeric quantities, percentages, and performance multipliers (e.g. "reduced latency by 45%", "managed team of 12").
   - Cross-references metrics against verified `AchievementItem` records.
   - Flags invented numbers as critical validation errors.

4. **Academic Credentials & Degree Status**:
   - Compares degree designations, institutions, majors, and graduation years against `EducationRecord`.
   - Prevents premature claims of degree conferral for currently enrolled students.

5. **Certification & License Numbers**:
   - Verifies credential IDs and issuing organizations against canonical records.

---

### Validation Severity Levels

```typescript
export interface WritingValidationIssue {
  severity: 'info' | 'warning' | 'error' | 'critical';
  block_id?: string;
  field_name?: string;
  message: string;
  unverified_token?: string;
  suggested_correction?: string;
}
```

- **`info`**: Style or readability suggestion (e.g. long sentence or passive voice).
- **`warning`**: Claim is user-reported but lacks formal document or repository evidence.
- **`error`**: Skill or tool mentioned in text does not exist in applicant's profile.
- **`critical`**: Contradiction of verified profile facts (e.g. claiming a degree that was not earned, or claiming unverified executive leadership).

---

### Zero-Hallucination Gatekeeper Logic

```python
class WritingFactValidator:
    def validate_cover_letter(self, doc: CoverLetterDocument, profile: ApplicantProfile) -> ValidationReport:
        issues = []
        canonical_skills = {s.name.lower() for s in profile.skills}
        canonical_employers = {e.company.lower() for e in profile.employment_records}
        
        for block in doc.blocks:
            # Audit metric assertions
            for metric in self.extract_metrics(block.text):
                if not self.is_metric_grounded(metric, profile):
                    issues.append(WritingValidationIssue(
                        severity="critical",
                        block_id=block.id,
                        message=f"Ungrounded metric assertion: '{metric.raw_text}'"
                    ))
            
            # Audit skill assertions
            for skill in self.extract_skill_mentions(block.text):
                if skill.lower() not in canonical_skills:
                    issues.append(WritingValidationIssue(
                        severity="error",
                        block_id=block.id,
                        message=f"Unverified skill mentioned: '{skill}'"
                    ))
                    
        is_passed = not any(i.severity in ("error", "critical") for i in issues)
        return ValidationReport(is_passed=is_passed, issues=issues)
```
