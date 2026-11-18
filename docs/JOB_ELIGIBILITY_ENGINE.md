# AUTONOM Job Eligibility Engine

## Stage 25 of 50 — Deterministic Qualification Verification

---

### Purpose & Constraints

The **Job Eligibility Evaluator** audits prospective job listings against the applicant's canonical factual records established in Stage 21 (Profile) and Stage 22 (GitHub). It executes completely deterministically with zero LLM improvisation, ensuring that AUTONOM never claims qualifications the user does not possess.

---

### Verification Dimensions

#### 1. Educational Attainment
- Evaluates candidate's highest completed degree against job requirements (`HighSchool` < `Associate` < `Bachelor` < `Master` < `Doctorate`).
- **Student Enrollment Exception**: If `allow_enrolled_for_future_grads` is enabled and the job is an internship or entry-level role, current enrollment with expected graduation within 12 months satisfies degree criteria.

#### 2. Verified Years of Experience
- Calculates cumulative days from verified `EmploymentRecord` entries.
- If a listing specifies `required_experience_years: 5`, and the applicant's verified employment is 2.5 years, the evaluator flags an eligibility shortfall.

#### 3. Skill Overlap & Code Evidence
- Distinguishes between:
  1. *Direct profile claim*: User added Python to their skills list.
  2. *Project-evidenced claim*: Skill linked to verified repositories or production deliverables.
  3. *Unevidenced claim*: Skill requested by job but absent from verified records.
- Calculates `skill_match_percentage = (matched_skills / required_skills) * 100`.

#### 4. Legal Work Authorization
- Checks whether applicant country of citizenship or permanent residency matches job location.
- If `work_authorization_required: True` and candidate country does not match, flags `ReviewTrigger.WORK_AUTH_UNCERTAIN` and triggers `NEEDS_REVIEW` rather than assuming sponsorship.
