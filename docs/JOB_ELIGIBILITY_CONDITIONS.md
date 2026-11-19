# Work Authorization, Visa Sponsorship & Legal Eligibility (Stage 28)

## 1. Overview
The Eligibility Conditions module extracts legal employment prerequisites, work authorization requirements, visa sponsorship status, citizenship constraints, and security clearance levels.

## 2. Invariant: Zero Inference on Legal Status
AUTONOM strictly adheres to the principle that legal eligibility cannot be inferred:
- If visa sponsorship is not mentioned in the posting, both `visa_sponsorship_offered` and `visa_sponsorship_refused` remain `None`.
- The system never assumes an employer offers sponsorship merely because they are a large tech company.

## 3. Work Authorization & Sponsorship Classification
| Statement in Job Posting | Classification |
|---|---|
| "Must be legally authorized to work in the United States" | `work_authorization_required = True` |
| "Visa sponsorship available for qualified candidates" | `visa_sponsorship_offered = True, visa_sponsorship_refused = False` |
| "No visa sponsorship available now or in the future" | `visa_sponsorship_refused = True, visa_sponsorship_offered = False` |
| "Unable to sponsor work visas at this time" | `visa_sponsorship_refused = True, visa_sponsorship_offered = False` |
| (Not mentioned) | `visa_sponsorship_offered = None, visa_sponsorship_refused = None` |

## 4. Citizenship & Security Clearance
- Citizenship constraints:
  - `US_CITIZEN_ONLY`: "US citizenship required due to federal compliance."
  - `US_PERSON`: "Must qualify as a US Person under ITAR regulations."
- Security clearances:
  - `Secret`, `Top Secret`, `TS/SCI`, `Public Trust`.
  - Distinguishes between active clearance required vs. ability to obtain clearance.
