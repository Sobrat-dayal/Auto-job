# AUTONOM Compensation Policies & Salary Normalizer

## Stage 25 of 50 — Financial Safeguards

---

### Core Principles

1. **Hard Salary Floors**:
   - `hard_floor_amount`: Absolute minimum acceptable salary. Opportunities offering less than this floor are automatically vetoed at Level 8.
2. **Standardized Annualization**:
   - The `CompensationNormalizer` mathematically standardizes rates into annualized USD comparisons without guessing:
     - `hourly`: Rate × 2,080 standard hours/year.
     - `daily`: Rate × 260 working days/year.
     - `weekly`: Rate × 52 weeks/year.
     - `monthly`: Rate × 12 months/year.
     - `annual`: Exact annual amount.
     - `stipend`: Annualized based on duration.
3. **Multi-Currency Safety**:
   - If a listing specifies a foreign currency without a verified exchange rate, the comparison returns `not_comparable`. AUTONOM refuses to invent arbitrary conversion rates.
4. **Undisclosed Salary Handling**:
   - `require_review` (Default): Flag posting and queue for human confirmation.
   - `consider`: Proceed assuming compensation is adequate if title and role match.
   - `exclude`: Reject unpriced postings at Level 8.
