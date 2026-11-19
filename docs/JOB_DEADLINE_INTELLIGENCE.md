# Application Deadlines & Document Intelligence (Stage 28)

## 1. Overview
The Deadlines & Instructions module parses submission closing dates, rolling admissions statuses, application URLs, and required document checklists.

## 2. Deadline Parsing
The parser handles common date formats and converts them to UTC datetime objects:
- `"Applications close on May 30, 2026"` -> `2026-05-30T00:00:00Z`.
- `"Deadline: 2026-06-15"` -> `2026-06-15T00:00:00Z`.
- `"Apply by April 1st, 2026"` -> `2026-04-01T00:00:00Z`.

## 3. Rolling Review Status
When an employer does not specify a fixed closing date but indicates continuous evaluation, the parser sets `is_rolling = True`:
- "Applications are reviewed on a rolling basis."
- "Open until filled; early submissions encouraged."
- "Positions filled as qualified applicants are interviewed."

## 4. Required Application Documents
Extracted document prerequisites:
- `Resume / CV`: Tailored resume versions.
- `Cover Letter`: Role-specific statement of intent.
- `Portfolio / GitHub`: Code repositories, design portfolios, or project demos.
- `Academic Transcripts`: Relevant for new graduate and intern roles.
- `Letters of Recommendation / References`: Formal recommendations.
