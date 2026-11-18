# AUTONOM — ATS Readability Analysis (Stage 23)

## 1. Transparent ATS Readability Methodology

Traditional resume tools present users with an opaque, unsubstantiated "ATS Score" (such as "88/100") that has no correlation with real recruiting software.

AUTONOM rejects deceptive scoring in favor of **inspectable, deterministic structural audits** that evaluate the exact physical properties ATS parsers require.

---

## 2. The 7 Deterministic Structural Checks

The `ATSReadabilityAuditor` runs 7 inspectable checks on every resume before and after export:

```
+---------------------------------------------------------------------------------------+
| Check Name                  | Severity | Target Condition                             |
+---------------------------------------------------------------------------------------+
| 1. Machine-Readable Text    | ERROR    | Document emits raw extractable UTF-8 text    |
| 2. Single-Column Layout     | WARNING  | Disallows multi-column flow in ATS templates |
| 3. Standard Section Headings| ERROR    | Headings match recognized taxonomy standards |
| 4. Accessible Contact Info  | ERROR    | Legal name, email, and phone clearly parsed  |
| 5. Chronological Integrity  | WARNING  | Entries contain valid YYYY or YYYY-MM dates  |
| 6. Standard Safe Typography | INFO     | Uses proven sans/serif fonts (Helvetica, etc)|
| 7. Bullet Structure & Length| WARNING  | Bullets between 20 and 400 characters        |
+---------------------------------------------------------------------------------------+
```

### Check 1: Machine-Readable Text
- **Rationale**: Scanned images, rasterized text, or vector outlines result in immediate rejection by automated ATS screening.
- **Rule**: Round-trip text extraction must retrieve at least 80% of the candidate's canonical profile content.

### Check 2: Single-Column Layout
- **Rationale**: Multi-column tables often result in horizontally crossed reading orders in older parsing engines (e.g. reading column 1 line 1, then column 2 line 1).
- **Rule**: Templates designated `is_ats_optimized` must maintain single-column reading order.

### Check 3: Standard Section Headings
- **Rationale**: Custom headings like *"Where I've Been"* or *"Tech Arsenal"* fail keyword dictionary lookups.
- **Rule**: Headings must map to standard categories: `SUMMARY`, `EXPERIENCE`, `EDUCATION`, `SKILLS`, `PROJECTS`, `CERTIFICATIONS`.

### Check 4: Accessible Contact Coordinates
- **Rationale**: Contact information placed in deep Word headers/footers is frequently skipped by resume parsers.
- **Rule**: Contact info must be located at the top of the main document flow.

### Check 5: Chronological Integrity
- **Rationale**: Experience records must have recognizable date strings to calculate total years of experience.
- **Rule**: Date strings must follow standard formats (e.g. `2022 - Present` or `2020-05 - 2023-11`).

### Check 6: Standard Safe Typography
- **Rationale**: Exotic decorative fonts lack standard character encoding tables on headless server parsers.
- **Rule**: Uses Helvetica, Arial, Calibri, Times New Roman, or Garamond.

### Check 7: Bullet Structure & Length
- **Rationale**: Overly dense paragraphs (>500 chars) are difficult to parse; single-word fragments indicate missing context.
- **Rule**: Each bullet must be between 20 and 400 characters.

---

## 3. Auditing Response Contract

```python
class ATSReport(BaseModel):
    id: str = Field(default_factory=lambda: f"ats_{uuid4().hex[:8]}")
    resume_id: str
    overall_status: ATSCheckStatus  # "pass", "warning", "error"
    total_checks: int
    passed_checks: int
    warning_checks: int
    error_checks: int
    checks: list[ATSCheckResult]
    recommendations: list[str]
    audited_at: datetime
```
