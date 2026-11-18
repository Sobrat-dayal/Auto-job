# Visual Automation Testing & Verification Guide (Stage 18)

## 1. Test Suite Architecture

Stage 18 is backed by comprehensive end-to-end unit, integration, live desktop, and frontend test suites:

| Test File | Tests | Coverage Scope |
|---|---|---|
| `test_visual_capture.py` | 3 | Physical monitor enumeration, image preprocessing, session lifecycle |
| `test_visual_coordinates.py` | 5 | NormalizedBox denormalization, inward offset, coordinate xforms, SendInput space |
| `test_visual_ocr_grounding.py` | 3 | Offline WinRT OCR extraction, fuzzy text matching, ambiguity resolution |
| `test_visual_actions.py` | 3 | Input ownership leases, state machine transitions, bounded recovery retries |
| `test_visual_real_desktop.py` | 3 | Genuine physical display capture, live desktop WinRT OCR, live grounding |
| `test_api_visual.py` | 6 | Authenticated REST endpoints: sessions, frames, OCR, grounding, tasks |
| `test_specialist_agents.py` | 6 | VisualGroundingAgent manifest, capability execution, multi-agent workflows |
| `visual-automation.test.tsx` | 5 | React workspace tabs, metrics, live query grounding, action dispatch |

Total dedicated Stage 18 tests: **34 tests passing 100%**.
Full backend regression suite: **189 tests passing 100%**.

---

## 2. Running Verification Tests

### Backend Tests
```bash
# Run all visual automation tests
pytest services/api/tests/test_visual_capture.py \
       services/api/tests/test_visual_coordinates.py \
       services/api/tests/test_visual_ocr_grounding.py \
       services/api/tests/test_visual_actions.py \
       services/api/tests/test_visual_real_desktop.py \
       services/api/tests/test_api_visual.py -v

# Run full backend regression suite
pytest services/api/tests/ -v
```

### Frontend Tests & Production Build
```bash
# Run Vitest on visual workspace
pnpm --filter desktop test visual-automation

# Typecheck and build frontend
pnpm --filter @autonom/shared-types typecheck
pnpm --filter desktop typecheck
pnpm --filter desktop build
```
