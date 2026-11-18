# Application Question Intelligence

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

Job application portals (Workday, Greenhouse, Lever, Taleo, Ashby, SmartRecruiters) confront applicants with dozens of open-ended and structured screening questions. The **Application Question Intelligence Subsystem** ingests raw question sets, parses individual prompts, classifies questions into 16 standardized categories, and determines required input formats and validation boundaries.

---

### The 16 Question Categories

| Category | Identifier | Description | Processing Behavior |
|---|---|---|---|
| **Work Authorization** | `work_authorization` | Right to work, visa status, citizenship | Enforces sensitive guard: strictly human choice, no auto-approval. |
| **Visa Sponsorship** | `visa_sponsorship` | Future or immediate sponsorship needs | Enforces sensitive guard: strictly human choice, no auto-approval. |
| **Compensation** | `compensation` | Salary expectations, bonus, hourly rates | Enforces sensitive guard: applicant must define numbers or range. |
| **Availability** | `availability` | Start date, notice period, relocation | Grounded in profile availability metadata. |
| **Experience Years** | `experience_years` | Total tenure or technology-specific tenure | Evaluated using non-overlapping calendar month calculation. |
| **Technical Knowledge** | `technical_knowledge` | Language/framework proficiency, architecture | Distinguishes theoretical knowledge from hands-on production code. |
| **Behavioral STAR** | `behavioral_star` | Team conflict, leadership, overcoming failure | Formulated using verified employment and project milestones. |
| **Project Deep-Dive** | `project_deep_dive` | Technical challenges, scale, design choices | Anchored in verified GitHub repository commits and architecture. |
| **Company Motivation** | `company_motivation` | "Why this company?", "Why this role?" | Synthesizes genuine interest, company values, and skill match. |
| **Academic / Education** | `academic_education` | GPA, degree, majors, graduation date | Grounded in verified canonical education records. |
| **Certifications** | `certifications_licenses` | Professional licenses, cloud certifications | Grounded in verified certification records with credential IDs. |
| **Remote / Location** | `remote_location` | Onsite preferences, travel percentage | Matches applicant preferences against job requirements. |
| **Demographics / EEO** | `demographic_eeo` | Gender, race, ethnicity, veteran, disability | Voluntary self-identification: strictly optional, user-controlled. |
| **Legal Attestation** | `legal_attestation` | Background checks, non-competes, accuracy | Strict user attestation guard: signature/confirmation required. |
| **Short Answer** | `short_answer` | General open-ended prompts under 100 words | Factually grounded concise response. |
| **General / Other** | `general` | Uncategorized inquiries | Analyzed via profile fact matching. |

---

### Input Format Discovery

The engine identifies 10 distinct expected answer formats (`AnswerType`):
1. `free_text`: Multi-paragraph open answers.
2. `short_text`: Single-line text (<150 characters).
3. `paragraph`: Single-paragraph structured response (<500 characters).
4. `numeric`: Exact numbers (e.g. years of experience, desired salary).
5. `date`: Calendar dates (e.g. earliest start date).
6. `boolean_yes_no`: Strict Yes/No binaries.
7. `single_choice`: Select one option from radio buttons.
8. `multiple_choice`: Multi-select checkboxes.
9. `dropdown`: Select item from enumerated list.
10. `conditional`: Questions dependent on prior answers.

---

### Non-Overlapping Experience Calculator

A frequent failure mode in automated job applications is tenure inflation caused by counting overlapping roles twice. AUTONOM implements a calendar-aware interval union algorithm (`ExperienceCalculator`):

- **Algorithm**:
  1. Gathers all employment and internship date ranges: $[S_i, E_i]$.
  2. If an end date is null, clamps to the current date.
  3. Projects intervals onto a unified calendar timeline.
  4. Merges overlapping and contiguous date ranges into disjoint intervals $[U_k, V_k]$.
  5. Computes total elapsed months across disjoint intervals:
     $$\text{Total Months} = \sum_k (V_k - U_k)$$
  6. Divides total months by 12 to yield accurate, non-inflated years of experience.
  7. Supports technology-specific filtering (e.g. calculating only years where Python was actively used).

---

### Text Parsing and Question Extraction

The parsing engine accepts unstructured text (pasted directly from application portals) and executes pattern-based extraction:
- Strips question numbering (`1.`, `Q1:`, `[Question]`).
- Isolates character/word limits (e.g. `(Max 500 characters)` or `[Word limit: 150]`).
- Detects required flags (`*`, `(Required)`).
- Identifies embedded option sets (`[ ] Yes  [ ] No`).
