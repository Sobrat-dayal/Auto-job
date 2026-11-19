# Experience Matching & Calendar Duration Math

## 1. Non-Overlapping Calendar Interval Math
To prevent double-counting experience when an applicant holds multiple concurrent positions (e.g. consulting or dual employment):
1. Roles are filtered by employment type (`full_time`, `contract`, `permanent`).
2. Start and end dates are converted to UTC calendar intervals `[start_date, end_date]`.
3. Overlapping and contiguous intervals are merged into disjoint calendar segments.
4. Total professional elapsed tenure is calculated as the sum of disjoint days divided by 365.25.
5. Example: Two concurrent roles from Jan 2021 to Dec 2022 yield exactly 2.0 years (24 months), NOT 4.0 years.

## 2. Category Distinction: Academic Projects vs Professional Roles
- Academic coursework, school capstones, and personal hobby projects receive separate attribution.
- Academic projects are explicitly classified under `projects`.
- If an employer requires 3+ years professional software engineering experience, academic projects receive `RELATED_EXPERIENCE_ONLY` and do NOT satisfy mandatory professional employment tenure.
- Full-time internships are tracked separately as internship months and evaluated cautiously.
