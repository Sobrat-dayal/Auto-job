"""Target validation, ambiguity detection, and candidate resolution (Stage 18)."""

import logging
from app.visual.contracts import (
    BoundingBox,
    FrameMetadata,
    Point2D,
    VisualElementDetection,
    VisualGroundingResult,
)
from app.visual.grounding.boxes import box_geometry
from app.visual.grounding.coordinates import coordinate_transformer

logger = logging.getLogger("autonom.visual.grounding.validation")


class TargetValidator:
    """Validates visual candidates against safety boundaries and disambiguates targets."""

    @staticmethod
    def validate_grounding_candidate(
        candidate: VisualElementDetection,
        metadata: FrameMetadata,
        min_width: int = 5,
        min_height: int = 5,
    ) -> tuple[bool, str | None]:
        """Validates that candidate detection is geometrically valid and inside authorized frame."""
        box = candidate.bounding_box

        if not box_geometry.validate_box(box, metadata.width, metadata.height):
            return False, f"Bounding box {box} is out of frame bounds ({metadata.width}x{metadata.height})"

        if box.width < min_width or box.height < min_height:
            return False, f"Target control is too small ({box.width}x{box.height}px; min {min_width}x{min_height}px)"

        return True, None

    @staticmethod
    def resolve_target(
        query: str,
        candidates: list[VisualElementDetection],
        metadata: FrameMetadata,
    ) -> VisualGroundingResult:
        """Resolves the best target candidate, detects ambiguities, and computes physical coordinates."""
        grounding = VisualGroundingResult(
            frame_id=metadata.frame_id,
            query=query,
            candidates=candidates,
        )

        if not candidates:
            grounding.ambiguity_status = "none"
            grounding.confidence = 0.0
            grounding.reasoning = f"No visual controls matching '{query}' detected in frame"
            return grounding

        # Filter valid candidates
        valid_candidates: list[VisualElementDetection] = []
        for c in candidates:
            is_valid, _ = TargetValidator.validate_grounding_candidate(c, metadata)
            if is_valid:
                valid_candidates.append(c)

        if not valid_candidates:
            grounding.ambiguity_status = "none"
            grounding.confidence = 0.0
            grounding.reasoning = f"All {len(candidates)} candidates failed boundary and size validation"
            return grounding

        # Sort by confidence descending
        valid_candidates.sort(key=lambda c: c.confidence, reverse=True)

        # Ambiguity check: if multiple candidates have nearly identical high confidence
        if len(valid_candidates) > 1:
            top_conf = valid_candidates[0].confidence
            second_conf = valid_candidates[1].confidence
            if abs(top_conf - second_conf) < 0.05 and top_conf > 0.8:
                grounding.ambiguity_status = "ambiguous"
                grounding.confidence = round(top_conf * 0.7, 2)
                grounding.reasoning = (
                    f"Ambiguous target: {len(valid_candidates)} matching controls detected with similar confidence. "
                    "Disambiguation required."
                )
                grounding.selected_target = valid_candidates[0]
                target_pt = box_geometry.get_safe_target_point(valid_candidates[0].bounding_box)
                grounding.target_point = target_pt
                grounding.desktop_point = coordinate_transformer.raw_frame_to_desktop(target_pt, metadata)
                return grounding

        # Unique confident selection
        selected = valid_candidates[0]
        target_pt = box_geometry.get_safe_target_point(selected.bounding_box)
        desktop_pt = coordinate_transformer.raw_frame_to_desktop(target_pt, metadata)

        grounding.selected_target = selected
        grounding.target_point = target_pt
        grounding.desktop_point = desktop_pt
        grounding.ambiguity_status = "unique"
        grounding.confidence = selected.confidence
        grounding.reasoning = f"Target '{selected.label or query}' successfully resolved at {target_pt}"
        return grounding


target_validator = TargetValidator()

