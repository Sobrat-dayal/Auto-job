# Semantic Job Change Detection & Classification (Stage 30)

## 1. Overview
When fresh observations are discovered for existing job listings, the change detection engine evaluates differences to prevent churn and superficial alert fatigue.

## 2. Semantic Normalization & Content Hashing
1. **HTML & Tag Stripping**: Removes non-semantic markup (`<p>`, `<div>`, `<style>`, formatting attributes).
2. **Whitespace Normalization**: Collapses repeated spaces, tabs, and newlines into single spaces.
3. **Case Folding**: Converts text to lowercase for comparison.
4. **SHA-256 Hashing**: Generates an immutable content digest. Changes in indentation, font styling, or tracking tags do not trigger material alerts.

## 3. Change Classification Matrix
| Change Type | Material? | Action Triggered |
|---|---|---|
| `NEW_VACANCY` | Yes | New canonical record + initial requirement extraction + match evaluation |
| `JOB_CLOSED` | Yes | Marks listing `closed`; updates queue entry to `closed`; closes active readiness handoff |
| `JOB_REOPENED` | Yes | Re-activates listing; re-evaluates match freshness |
| `SALARY_CHANGED` | Yes | Invalidates compensation dimension score; re-ranks opportunity |
| `LOCATION_CHANGED` | Yes | Invalidate location compatibility; re-checks eligibility |
| `REMOTE_CONDITIONS_CHANGED` | Yes | Invalidate remote eligibility; re-evaluates career policy compliance |
| `APPLICATION_URL_CHANGED` | Yes | Updates application URL for Stage 31 readiness contract |
| `DESCRIPTION_UPDATED` | Conditional | Material if SHA-256 changes; invalidates intelligence and requirements |

## 4. Partial Snapshot Safety Invariant
The change engine strictly requires confirmation of complete source snapshots before marking unobserved listings as closed. Feeds returning paginated or keyword-filtered partial listings never mass-close vacancies.
