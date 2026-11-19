# Evidence Provenance & Traceability (Stage 28)

## 1. Overview
AUTONOM enforces complete, verifiable provenance for every extracted requirement. An applicant or recruiter can click on any structured requirement in the desktop workspace and view the exact source sentence and character offsets where the employer stated the condition.

## 2. Requirement Evidence Schema
Every atomic requirement references one or more `RequirementEvidence` records:
- `id`: Unique UUID.
- `requirement_id`: Foreign key to parent `job_requirements.id`.
- `section_name`: Identified section (`MINIMUM_QUALIFICATIONS`, `PREFERRED_QUALIFICATIONS`, `RESPONSIBILITIES`, etc.).
- `supporting_text`: Verbatim quote from the employer posting.
- `start_char`: Exact starting character offset in the cleaned description text.
- `end_char`: Exact ending character offset in the cleaned description text.
- `quote_hash`: SHA-256 digest of the normalized quote text.
- `extraction_method`: `DETERMINISTIC_RULES` or `AI_EXTRACTION`.
- `verified_in_source`: Boolean flag indicating whether the verbatim quote was verified against the raw text.

## 3. Provenance Verification Algorithm
```python
def find_source_span(full_text: str, target_quote: str) -> tuple[int, int, bool]:
    # 1. Exact string search
    idx = full_text.find(target_quote)
    if idx != -1:
        return idx, idx + len(target_quote), True

    # 2. Case-insensitive search
    idx = full_text.lower().find(target_quote.lower())
    if idx != -1:
        return idx, idx + len(target_quote), True

    # 3. Normalized whitespace regex search
    escaped_tokens = [re.escape(token) for token in target_quote.split()]
    pattern = r"\s+".join(escaped_tokens)
    match = re.search(pattern, full_text, flags=re.IGNORECASE)
    if match:
        return match.start(), match.end(), True

    return 0, 0, False
```
