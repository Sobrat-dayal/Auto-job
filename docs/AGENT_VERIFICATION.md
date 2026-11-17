# Verification Agent Architecture (Stage 12)

## 1. Multi-Layer Verification Design

The **Verification Agent** (`verifier`) guarantees that step outputs adhere to strict schemas and qualitative criteria before downstream dependent steps consume them.

```
                  Step Output Produced
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  Layer 1: Deterministic Verification          │
    │  - Non-null & Dictionary format check         │
    │  - Required JSON schema field checks          │
    │  - Non-empty heuristic assertions             │
    │  - Strong type checking                       │
    └───────────────────────┬───────────────────────┘
                            │ (Passed)
                            ▼
    ┌───────────────────────────────────────────────┐
    │  Layer 2: Semantic Verification (Optional)    │
    │  - AI Gateway Code Review / Evaluation        │
    │  - Prompt compliance scoring (0.0 to 1.0)     │
    │  - Instruction fulfillment review             │
    └───────────────────────┬───────────────────────┘
                            │
                            ▼
          [ VerificationResult: Pass / Fail / NeedsReview ]
```

---

## 2. Verification Outcomes

The Verification Agent produces four normalized outcomes:
- **`PASS`**: Output meets all deterministic schema contracts and qualitative thresholds. Downstream steps are unblocked.
- **`FAIL`**: Output violated required fields, contained syntax errors, or failed semantic review. Triggers Recovery Agent.
- **`NEEDS_REVIEW`**: Output passed basic schema checks but fell below qualitative confidence threshold. Can trigger human-in-the-loop inspection.
- **`UNVERIFIABLE`**: Step produced unparseable or inaccessible external artifacts.

---

## 3. Persistent Audit Evidence

Every verification is saved to the SQLite `verification_results` table with complete evidence, verification type, and detailed audit notes, queryable at `/api/v1/orchestration/workflows/{workflow_id}/verifications`.
