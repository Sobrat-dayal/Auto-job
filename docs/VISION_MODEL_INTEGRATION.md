# Vision-Language Model Integration Specification (Stage 18)

## 1. Offline & Local-First Perception Strategy

In accordance with AUTONOM's core privacy guidelines, Visual Perception prioritizes **offline local inference** before routing to cloud multimodal models:

1. **Primary Perception Layer: Offline Windows Media OCR (`winsdk.windows.media.ocr`)**
   - Utilizes Windows 11 native WinRT OCR engine.
   - 100% offline, zero network egress, zero token consumption.
   - Extracts character-level bounding boxes and confidence scores in under 50 ms.
2. **Secondary Perception Layer: Local Vision Models (VLM)**
   - Local multimodal models (e.g. Qwen2-VL, Moondream, or Florence-2 via local Ollama/llama.cpp runtime).
   - Detects non-text visual icons, buttons, sliders, switches, and custom widgets.
3. **Cloud Fallback Perception Layer**
   - Routed through Stage 11 AI Model Gateway when authorized by user policy and local confidence is insufficient.

---

## 2. Text Target Search & Heuristic Classification

`WindowsMediaOCREngine` (`app/visual/grounding/ocr.py`) implements text target search:
- **Exact & Fuzzy String Matching**: Token similarity calculation using `difflib.SequenceMatcher` with a configurable threshold (default `0.7`).
- **Semantic Classification**: Text labels are automatically categorized into `ElementCategory`:
  - `BUTTON`: Contains action triggers like "Save", "Submit", "Cancel", "Apply", "OK".
  - `INPUT`: Contains input placeholders like "Search", "Email", "Password", "Enter...".
  - `DIALOG`: Error or confirmation modals.

---

## 3. Visual Prompt Engineering & Annotation Formatting

When delegating frames to multimodal models, `FramePreprocessor` produces optimized prompts with annotated grids or element outlines:
- Image resolution clamped to 1600px max side.
- System prompt instructs model to return strictly typed JSON with `[ymin, xmin, ymax, xmax]` normalized coordinates and descriptive reasoning.
- Output parsed directly into `VisualElementDetection` objects.
