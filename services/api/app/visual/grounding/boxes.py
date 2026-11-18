"""Bounding box normalization, intersection, and containment checks (Stage 18)."""

from app.visual.contracts import BoundingBox, NormalizedBox, Point2D


class BoxGeometryService:
    """Provides geometry operations for UI element bounding boxes."""

    @staticmethod
    def normalize_box(box: BoundingBox, frame_width: int, frame_height: int) -> NormalizedBox:
        """Converts pixel bounding box to normalized coordinates (0.0 to 1.0)."""
        fw = max(1, frame_width)
        fh = max(1, frame_height)

        x_min = max(0.0, min(1.0, box.left / float(fw)))
        y_min = max(0.0, min(1.0, box.top / float(fh)))
        x_max = max(x_min, min(1.0, box.right / float(fw)))
        y_max = max(y_min, min(1.0, box.bottom / float(fh)))

        return NormalizedBox(x_min=round(x_min, 4), y_min=round(y_min, 4), x_max=round(x_max, 4), y_max=round(y_max, 4))

    @staticmethod
    def denormalize_box(norm: NormalizedBox, frame_width: int, frame_height: int) -> BoundingBox:
        """Converts normalized box to pixel bounding box."""
        left = int(round(norm.x_min * frame_width))
        top = int(round(norm.y_min * frame_height))
        width = int(round((norm.x_max - norm.x_min) * frame_width))
        height = int(round((norm.y_max - norm.y_min) * frame_height))
        return BoundingBox(left=left, top=top, width=width, height=height)

    @staticmethod
    def get_center_point(box: BoundingBox) -> Point2D:
        """Returns exact center point of the box."""
        return Point2D(x=box.left + box.width // 2, y=box.top + box.height // 2)

    @staticmethod
    def get_inward_target_point(box: BoundingBox, margin_ratio: float = 0.1) -> Point2D:
        """Returns interior target click point avoiding control borders."""
        return BoxGeometryService.get_center_point(box)

    @staticmethod
    def calculate_iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
        """Calculates Intersection over Union (IoU) between two bounding boxes."""
        inter_left = max(box_a.left, box_b.left)
        inter_top = max(box_a.top, box_b.top)
        inter_right = min(box_a.right, box_b.right)
        inter_bottom = min(box_a.bottom, box_b.bottom)

        if inter_right <= inter_left or inter_bottom <= inter_top:
            return 0.0

        inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
        area_a = box_a.width * box_a.height
        area_b = box_b.width * box_b.height
        union_area = float(area_a + area_b - inter_area)

        if union_area <= 0:
            return 0.0
        return round(inter_area / union_area, 4)

    @staticmethod
    def compute_iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
        """Alias for calculate_iou."""
        return BoxGeometryService.calculate_iou(box_a, box_b)

    @staticmethod
    def get_safe_target_point(box: BoundingBox) -> Point2D:
        """Returns safe target interaction point within the control (center offset inward from border)."""
        return Point2D(
            x=box.left + max(2, box.width // 2),
            y=box.top + max(2, box.height // 2),
        )

    @staticmethod
    def validate_box(box: BoundingBox, frame_width: int, frame_height: int) -> bool:
        """Validates that a box is non-degenerate and completely inside frame boundaries."""
        if box.width < 2 or box.height < 2:
            return False
        if box.left < 0 or box.top < 0:
            return False
        if box.right > frame_width or box.bottom > frame_height:
            return False
        return True


box_geometry = BoxGeometryService()

