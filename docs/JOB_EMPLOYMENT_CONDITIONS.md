# Employment Conditions & Workplace Types (Stage 28)

## 1. Overview
The Employment Conditions module parses the physical and contractual terms of a role, including remote vs. hybrid vs. onsite work, hybrid weekly schedules, travel requirements, and contract durations.

## 2. Workplace Classification
- `REMOTE_GLOBAL`: 100% remote, work from anywhere worldwide.
- `REMOTE_COUNTRY_ONLY`: Remote role restricted to specific geographic jurisdictions (e.g. "Remote (US only)").
- `HYBRID`: Combination of remote and office-based work.
- `ONSITE`: 100% in-person office attendance required.
- `FLEXIBLE`: Employee-chosen arrangement.
- `UNKNOWN`: Not specified by employer.

## 3. Hybrid Schedule Extraction
When a role is designated as hybrid, the parser extracts the weekly office attendance commitment:
- "Hybrid role with 2 days per week in our Seattle office" -> `office_days_per_week = 2`.
- "3 days weekly onsite / 2 days remote" -> `office_days_per_week = 3`.

## 4. Business Travel Requirements
- Quantified travel percentages:
  - "Up to 20% travel" -> `travel_percentage = 20.0`.
  - "Minimal travel" / "No regular travel required" -> `travel_percentage = 0.0`.

## 5. Contractual Types
- Full-Time (`FULL_TIME`)
- Part-Time (`PART_TIME`)
- Fixed-Term Contract (`CONTRACT`) with duration parsing ("6-month contract")
- Internship (`INTERNSHIP`)
