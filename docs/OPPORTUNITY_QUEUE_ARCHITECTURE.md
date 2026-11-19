# Opportunity Queue Architecture & Stage 31 Handoff (Stage 30)

## 1. Overview
The **Prioritized Opportunity Queue** is the operational focal point where discovered and matched vacancies are ranked, reviewed, and prepared for future application generation.

## 2. Priority Calculation Engine
Priority is calculated deterministically from match outcomes, policy compliance, and review flags:
- **`CRITICAL_REVIEW`**: Vacancies with ambiguous work authorization, contradictory claims, or pending review requests.
- **`HIGH`**: Verified relevance index $\ge 80\%$, hard policy passed, zero blocking qualification gaps.
- **`NORMAL`**: Verified relevance index between $60\%$ and $79\%$.
- **`LOW`**: Relevance index $< 60\%$.
- **`EXCLUDED`**: Hard policy violation (blocked employer, unauthorized country, hard visa conflict).

## 3. Supported User Actions
Users can override queue classifications directly in the UI:
- **`save`**: Bookmarks opportunity in `saved` status for later attention.
- **`prioritize`**: Manually elevates priority to `high`.
- **`defer`**: Temporarily mutes alerts and lowers priority.
- **`exclude`**: Manually dismisses vacancy from active queue.
- **`archive`**: Stores vacancy in historical archive.

Every user action records an immutable audit entry in `recruitment_opportunity_queue_history`.

## 4. Stage 31 Handoff Contract: `OpportunityPreparationCandidate`
When an opportunity is deemed `ready_for_preparation`, the queue generates a self-contained contract containing:
- Canonical Job ID & Version
- Applicant Profile ID & Version
- Match Evaluation ID & Verified Score
- Eligibility Outcome & Career Strategy ID
- Missing Information & Required Reviews
- Application URL & Employer Metadata
*(Note: Handoff enables application preparation in Stage 31; zero applications are submitted in Stage 30).*
