# Job Matching Engine Architecture

## 1. System Overview
The AUTONOM Job Matching Engine (Stage 29) bridges canonical job records (Stage 27) and structured job requirements (Stage 28) with canonical applicant profiles (Stage 21), technical evidence (Stage 22), and active recruitment policies (Stage 25).

```
                      +-----------------------------+
                      |   Canonical Job Listing     |
                      |        (Stage 27)           |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Structured Intelligence   |
                      |        (Stage 28)           |
                      +--------------+--------------+
                                     |
                                     v
+---------------------+   +-------------------------+   +----------------------+
|  Applicant Profile  |-->|    JOB MATCHING ENGINE  |<--| Active Career Policy |
|     (Stage 21)      |   |       (Stage 29)        |   |      (Stage 25)      |
+---------------------+   +------------+------------+   +----------------------+
                                       |
                   +-------------------+-------------------+
                   |                   |                   |
                   v                   v                   v
           +---------------+   +---------------+   +---------------+
           | 4-Question    |   | Gap & Review  |   | Explainable   |
           | Eligibility   |   | Intelligence  |   | Ranking (0-100|
           +---------------+   +---------------+   +---------------+
```

## 2. Core Operational Tenets
1. **Four Independent Questions**:
   - *Eligibility*: Can the applicant legally and policy-wise be hired for this position?
   - *Qualification Coverage*: Does the applicant possess verified evidence satisfying mandatory prerequisites?
   - *Preference Alignment*: Does this role meet the applicant's compensation floor, location, and role desires?
   - *Operational Readiness*: Is the vacancy ready for downstream preparation (NOT submission grant)?
2. **Hard Constraint Precedence**:
   Employer blocklists, visa sponsorship conflicts, and geographic exclusions completely override soft ranking scores. An applicant with a 100% skill match will still receive `REJECTED_BY_HARD_POLICY` if the employer is blocked.
3. **Zero Synthetic Guessing**:
   No hallucinated skills, inferred citizenships, or fabricated salaries. Unobserved facts remain explicitly unobserved, producing measurable ranking uncertainty.
4. **No Autonomous Submission**:
   Application readiness is separated from authorization. `READY_FOR_PREPARATION` enables resume tailoring (Stage 23) and cover letter generation (Stage 24), but never triggers an unapproved application submission.
