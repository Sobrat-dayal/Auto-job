# Compensation Intelligence & Zero Synthetic Guessing (Stage 28)

## 1. Overview
The Compensation Intelligence module parses salary ranges, hourly rates, currencies, pay periods, bonuses, equity, and employee benefits.

## 2. Invariant: Zero Synthetic Guessing
**AUTONOM never fabricates or estimates salary values.**
- If compensation is omitted from the job posting or structured data, `is_disclosed = False`, and `base_min` and `base_max` remain `None`.
- The system never converts missing data into fabricated industry averages or Glassdoor estimates.

## 3. Range and Rate Parsing
The parser supports varied currency symbols and delimiters:
- Hyphens (`-`), En-dashes (`–`), Em-dashes (`—`), and `"to"`.
- Thousands abbreviations: `"$140k - $180k"` -> `140000.0` - `180000.0`.
- ISO Currencies: `USD` (`$`), `EUR` (`€`), `GBP` (`£`), `CAD`, `AUD`.
- Pay Periods:
  - `ANNUAL`: `$140,000 - $180,000 / year`, `annually`.
  - `HOURLY`: `$65 - $85 / hour`, `per hour`.
  - `MONTHLY`: `€6,000 - €8,000 / month`.

## 4. Total Rewards Breakdown
- **Base Salary**: Fixed guaranteed cash compensation.
- **Bonus & Incentives**: Performance bonuses, annual target percentages, sign-on bonuses.
- **Equity**: Stock options, RSUs, employee share purchase plans.
- **Benefits**: Health insurance, 401(k) / pension matching, dental/vision, paid time off (PTO), learning budgets, wellness stipends.
