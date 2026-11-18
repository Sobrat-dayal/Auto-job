# Sensitive Application Questions & Attestation Policies

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

Recruitment portals routinely include questions that carry severe legal, immigration, ethical, and personal consequences. These include work authorization, immigration visa sponsorship, salary requirements, voluntary demographic self-identification (Equal Employment Opportunity / EEO), and legal attestations (background checks, truthfulness warranties).

AUTONOM enforces strict architectural safeguards (`SensitiveQuestionGuards`) to ensure the AI **NEVER** answers or submits these questions autonomously.

---

### Protected Categories & Enforcement Rules

| Sensitive Category | Rule & Guard Behavior | Allowed AI Assistance | Forbidden AI Actions |
|---|---|---|---|
| **Work Authorization** | `requires_user_confirmation` | Surface applicant's verified country of citizenship and existing authorization documents. | Never guess authorization status; never auto-answer "Yes" or "No". |
| **Visa Sponsorship** | `requires_user_confirmation` | Display past user preferences regarding H-1B, TN, O-1, or STEM OPT. | Never fabricate visa eligibility or make binding sponsorship commitments. |
| **Compensation / Salary** | `requires_user_confirmation` | Display user-configured target range or market benchmarks if requested. | Never commit to a specific number or accept a lowball offer without applicant confirmation. |
| **EEO Demographics** (Race, Gender, Veteran, Disability) | `sensitive_optional` | Offer standard "I do not wish to self-identify" option and respect applicant preferences. | Never infer demographics from names, photos, or audio; never auto-fill protected traits. |
| **Legal Attestations** | `requires_user_attestation` | Highlight the exact declaration text, legal clauses, and penalties for false statements. | Never auto-sign or forge applicant electronic signature. |

---

### Attestation Audit Logging

When an applicant reviews and confirms a sensitive answer or signs a legal declaration, AUTONOM records an immutable attestation entry:

```json
{
  "question_id": "q_work_auth_01",
  "category": "work_authorization",
  "confirmed_answer": "Yes, authorized to work in the United States without restriction",
  "user_attestation_actor": "sobrat.dayal@autonom.local",
  "user_attestation_timestamp": "2026-11-18T16:45:00.123Z",
  "ip_address": "127.0.0.1",
  "profile_snapshot_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

This audit trail protects the applicant by proving that all representations submitted to employers were deliberately reviewed and authorized by the human user.

---

### UI Safeguards in Desktop Application

In the AUTONOM desktop application (`SensitiveDecisionsTab.tsx`):
- Sensitive questions are rendered with distinct visual warning badges (amber shield icons).
- Form inputs default to neutral unselected states.
- The "Apply All" or "Batch Accept" buttons explicitly exclude sensitive questions.
- A prominent amber alert informs the applicant of their legal rights and the non-binding nature of voluntary demographic disclosures.
