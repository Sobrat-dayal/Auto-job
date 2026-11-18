"""Visual UI understanding, element detection, and multimodal grounding service (Stage 18)."""

import asyncio
import logging
from typing import Any
from PIL import Image
from app.visual.contracts import (
    BoundingBox,
    ElementCategory,
    FrameMetadata,
    NormalizedBox,
    VisualElementDetection,
    VisualGroundingResult,
)
from app.visual.grounding.boxes import box_geometry
from app.visual.grounding.ocr import ocr_engine
from app.visual.grounding.validation import target_validator

logger = logging.getLogger("autonom.visual.grounding.vision")


class VisualGroundingService:
    """Interprets screenshots, detects visual controls via OCR and vision models, and grounds targets."""

    def __init__(self, ocr_engine: Any = None) -> None:
        from app.visual.grounding.ocr import ocr_engine as default_ocr_engine
        self._ocr = ocr_engine or default_ocr_engine

    async def detect_elements(
        self,
        image: Any,
        metadata: FrameMetadata | None = None,
    ) -> list[VisualElementDetection]:
        """Detects visible UI controls in the frame using OCR and visual shape heuristics."""
        if hasattr(image, "metadata") and hasattr(image, "image"):
            # Called with CapturedFrame
            metadata = metadata or image.metadata
            image = image.image

        if metadata is None:
            w = image.size[0] if hasattr(image, "size") else 1920
            h = image.size[1] if hasattr(image, "size") else 1080
            metadata = FrameMetadata(width=w, height=h)

        detections: list[VisualElementDetection] = []
        w, h = image.size

        # 1. OCR text-based element detection
        if self._ocr.is_available:
            ocr_res = await self._ocr.extract_text_from_image(image)
            for line in ocr_res.lines:
                box = line.bounding_box
                norm_box = box_geometry.normalize_box(box, w, h)

                # Classify category based on text heuristics
                label_lower = line.text.lower()
                cat = ElementCategory.TEXT
                if any(w in label_lower for w in ["ok", "save", "cancel", "submit", "apply", "close", "launch", "run", "inspect"]):
                    cat = ElementCategory.BUTTON
                elif any(w in label_lower for w in ["search", "enter", "type", "password", "name", "email", "http"]):
                    cat = ElementCategory.INPUT
                elif any(w in label_lower for w in ["settings", "options", "preferences", "tools"]):
                    cat = ElementCategory.MENU

                detections.append(
                    VisualElementDetection(
                        frame_id=metadata.frame_id,
                        category=cat,
                        label=line.text,
                        bounding_box=box,
                        normalized_box=norm_box,
                        confidence=0.92,
                        source="ocr_engine",
                    )
                )

        return detections

    async def ground_query(
        self,
        image: Image.Image,
        metadata: FrameMetadata,
        query: str,
    ) -> VisualGroundingResult:
        """Locates the specific UI element matching query in screenshot frame."""
        candidates: list[VisualElementDetection] = []
        w, h = image.size
        q_lower = query.lower()

        # Step 1: Query OCR engine for direct text match
        if self._ocr.is_available:
            ocr_res = await self._ocr.extract_text_from_image(image)
            matches = self._ocr.find_text_targets(ocr_res, query, exact=False, min_similarity=0.7)
            for matched_text, box, score in matches:
                norm_box = box_geometry.normalize_box(box, w, h)
                candidates.append(
                    VisualElementDetection(
                        frame_id=metadata.frame_id,
                        category=ElementCategory.BUTTON if "button" in q_lower else ElementCategory.TEXT,
                        label=matched_text,
                        bounding_box=box,
                        normalized_box=norm_box,
                        confidence=score,
                        source="ocr_match",
                    )
                )

        # Step 2: Fallback to all detected elements if no direct OCR match
        if not candidates:
            all_elements = await self.detect_elements(image, metadata)
            for el in all_elements:
                if el.label and (q_lower in el.label.lower() or el.label.lower() in q_lower):
                    candidates.append(el)

        return target_validator.resolve_target(query, candidates, metadata)

    async def ground(
        self,
        frame: Any = None,
        query: str = "",
        target_type: Any = None,
        target_hwnd: Any = None,
        display_index: Any = None,
        image: Any = None,
        metadata: Any = None,
        **kwargs: Any,
    ) -> VisualGroundingResult:
        """Grounds query against a frame or image/metadata pair."""
        if frame is not None:
            img = getattr(frame, "image", None) or frame
            meta = getattr(frame, "metadata", None)
        else:
            img = image
            meta = metadata

        if meta is None and hasattr(img, "size"):
            meta = FrameMetadata(width=img.size[0], height=img.size[1])

        return await self.ground_query(img, meta, query)


visual_grounding_service = VisualGroundingService()

