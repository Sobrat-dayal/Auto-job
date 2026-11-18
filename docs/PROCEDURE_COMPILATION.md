# Procedure Compilation Pipeline

## 1. Overview & Goals

The Procedure Compiler (`app/computer/workflow_reliability/procedures/compiler.py`) transforms raw, noisy `RecordedAction` sequences into structured, validated, parameterized `ReusableProcedure` specifications.

Raw recordings typically contain:
- Unnecessary mouse movements and transient hover states.
- Duplicate keystrokes or repeated typing sequences.
- Hardcoded sensitive values and session-specific URLs.
- Fragile single-modality selectors.

The compilation pipeline sanitizes, normalizes, parameterizes, and validates the workflow through a 5-stage transformation pipeline.

---

## 2. Compilation Stages

```
+----------------------------------------------------------------------------------------------------+
|                                    RAW RECORDED ACTIONS SEQUENCE                                   |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| Stage 1: NOISE FILTERING & REDUNDANCY PRUNING                                                      |
| - Filter transient mouse moves and zero-delta scrolls                                              |
| - Collapse rapid repeated key inputs into single `fill` or `type` operations                       |
| - Prune aborted or error-flagged recorded actions                                                  |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| Stage 2: MULTI-MODAL TARGET ENRICHMENT                                                             |
| - Derive multi-modality selectors for each target (CSS + XPath + AutomationId + BoundingBox)      |
| - Construct relative anchor descriptions for visual targets                                        |
| - Set fallback search radiuses and tolerance bounds                                                |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| Stage 3: PARAMETER EXTRACTION & TEMPLATIZING                                                       |
| - Detect dynamic values (applicant names, emails, URLs, IDs)                                       |
| - Generate `ProcedureParameter` definitions with types and descriptions                            |
| - Replace literals with `{{param_name}}` bindings                                                  |
| - Tag redacted secret tokens as `is_secret=True` parameters                                        |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| Stage 4: PRECONDITION & POSTCONDITION SYNTHESIS                                                    |
| - Synthesize `element_exists` assertions from successful prior interactions                        |
| - Synthesize `url_matches` and `window_active` assertions from state fingerprints                   |
| - Classify actions into idempotent vs non-idempotent based on mutation semantics                  |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| Stage 5: STATIC RISK ANALYSIS & VALIDATION                                                         |
| - Compute composite static risk score (0.0 to 100.0)                                               |
| - Verify non-empty steps and valid parameter bindings                                              |
| - Output validated `ReusableProcedure` draft                                                      |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Static Risk Scoring Algorithm

The compiler calculates an automated risk score for every procedure based on the sensitivity of its steps:

```python
RISK_WEIGHTS = {
    "payment": 50.0,
    "form_submission": 30.0,
    "email_send": 25.0,
    "file_download": 15.0,
    "hotkey": 10.0,
    "click": 5.0,
    "type": 5.0,
    "navigate": 2.0,
}
```

The composite risk score is capped between `0.0` and `100.0`. Procedures scoring above `70.0` require explicit human-in-the-loop authorization approval under Stage 14 policy baselines before autonomous execution is permitted.

---

## 4. Compiler API & Usage

Compilation can be initiated via Python service or REST API:
```http
POST /api/v1/reliability/recordings/{session_id}/compile
Content-Type: application/json

{
  "name": "LinkedIn Job Application Flow",
  "description": "Submits application on LinkedIn careers portal",
  "parameter_bindings": {
    "applicant_email": "user@example.com"
  },
  "auto_publish": false
}
```

The resulting response returns the complete `ReusableProcedure` object including detected parameters, synthesized assertions, and validation status.
