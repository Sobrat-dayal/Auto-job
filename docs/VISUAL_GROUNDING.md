# Visual UI Grounding & Disambiguation Specification (Stage 18)

## 1. Grounding Pipeline

Visual UI Grounding (`app/visual/grounding/vision.py` and `validation.py`) converts abstract intent (e.g. "Click the Apply Now button") into verified desktop interaction targets:

```
User Query: "Click Apply"
         │
         ▼
[1. Text OCR Pass] ──(Direct Match Found)──► Candidate Bounding Box
         │ (No direct match)
         ▼
[2. Visual Heuristic / VLM Detection] ──► Ranked Candidates [c1, c2, c3]
         │
         ▼
[3. TargetValidator]
   - Bounds validation (inside window/desktop)
   - Size threshold validation (min 5x5 px)
   - Ambiguity detection (score delta < 0.05)
         │
         ▼
[4. Coordinate Transformer] ──► Exact Desktop Target Point {x, y}
```

---

## 2. Ambiguity Detection & Disambiguation

When an application contains multiple identical or similar controls (e.g., three "Cancel" buttons in a multi-dialog wizard):
1. Candidates are ranked by detection confidence.
2. If the top two candidates have confidence scores within `0.05` and both exceed `0.80`:
   - `ambiguity_status` is flagged as `"ambiguous"`.
   - Confidence is down-weighted to prevent unintended interaction.
   - The reasoning trail details the candidate locations and requests contextual disambiguation from the agent supervisor or user.
3. If one candidate distinctly matches the parent panel or focus area, it is selected with `ambiguity_status = "unique"`.

---

## 3. Geometric Target Validation: `TargetValidator`

Before an action is dispatched to the input system, `TargetValidator` enforces:
- `validate_box`: Verifies box is not degenerate (`width >= 2`, `height >= 2`) and completely contained within frame boundaries.
- `min_size_check`: Prevents clicking 1x1 invisible tracking pixels or artifact noise.
- Safe inward click point calculation via `box_geometry.get_safe_target_point`.
