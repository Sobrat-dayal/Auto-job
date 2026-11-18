"""Multi-monitor and DPI-aware coordinate transformations (Stage 18)."""

import logging
from app.visual.contracts import BoundingBox, FrameMetadata, Point2D

logger = logging.getLogger("autonom.visual.grounding.coordinates")


class CoordinateTransformer:
    """Performs deterministic coordinate transformations across image, window, and desktop spaces."""

    @staticmethod
    def model_to_raw_frame(point: Point2D, metadata: FrameMetadata) -> Point2D:
        """Converts coordinates from scaled model-input space back to raw frame pixels."""
        if metadata.scale_factor <= 0 or metadata.scale_factor == 1.0:
            return point

        inv_scale = 1.0 / metadata.scale_factor
        raw_x = int(point.x * inv_scale)
        raw_y = int(point.y * inv_scale)

        # Clamp within original frame boundaries
        raw_x = max(0, min(metadata.width - 1, raw_x))
        raw_y = max(0, min(metadata.height - 1, raw_y))
        return Point2D(x=raw_x, y=raw_y)

    @staticmethod
    def raw_frame_to_desktop(point: Point2D, metadata: FrameMetadata) -> Point2D:
        """Converts raw frame coordinates to physical desktop pixels accounting for window or monitor offsets."""
        desktop_x = point.x
        desktop_y = point.y

        # If this was a window-specific capture, add the window's top-left offset
        if metadata.crop_box:
            desktop_x += metadata.crop_box.left
            desktop_y += metadata.crop_box.top

        return Point2D(x=desktop_x, y=desktop_y)

    @staticmethod
    def model_to_desktop(point: Point2D, metadata: FrameMetadata) -> Point2D:
        """Complete transformation pipeline: model input -> raw frame -> physical desktop."""
        raw_point = CoordinateTransformer.model_to_raw_frame(point, metadata)
        return CoordinateTransformer.raw_frame_to_desktop(raw_point, metadata)

    @staticmethod
    def desktop_to_normalized_input(point: Point2D, virtual_bounds: BoundingBox) -> tuple[int, int]:
        """Converts physical desktop coordinates into Windows SendInput normalized absolute range (0..65535).
        Windows SendInput with MOUSEEVENTF_ABSOLUTE expects:
        normalized_x = (x - virtual_left) * 65535 / virtual_width
        normalized_y = (y - virtual_top) * 65535 / virtual_height
        """
        vw = max(1, virtual_bounds.width)
        vh = max(1, virtual_bounds.height)

        norm_x = int((point.x - virtual_bounds.left) * 65535.0 / float(vw))
        norm_y = int((point.y - virtual_bounds.top) * 65535.0 / float(vh))

        norm_x = max(0, min(65535, norm_x))
        norm_y = max(0, min(65535, norm_y))
        return norm_x, norm_y

    @staticmethod
    def transform_frame_to_desktop(
        point: Point2D,
        frame_width: int,
        frame_height: int,
        desktop_origin_x: int = 0,
        desktop_origin_y: int = 0,
    ) -> Point2D:
        """Transforms frame coordinates to physical desktop using monitor origin."""
        return Point2D(x=point.x + desktop_origin_x, y=point.y + desktop_origin_y)

    @staticmethod
    def to_sendinput_normalized_coords(
        point: Point2D,
        virtual_screen_rect: dict[str, int] | BoundingBox,
    ) -> tuple[int, int]:
        """Converts desktop coordinates to SendInput 0..65535 space using virtual screen bounds."""
        if isinstance(virtual_screen_rect, dict):
            bounds = BoundingBox(
                left=virtual_screen_rect.get("left", 0),
                top=virtual_screen_rect.get("top", 0),
                width=virtual_screen_rect.get("width", 1920),
                height=virtual_screen_rect.get("height", 1080),
            )
        else:
            bounds = virtual_screen_rect
        return CoordinateTransformer.desktop_to_normalized_input(point, bounds)

    @staticmethod
    def is_point_within_bounds(point: Point2D, bounds: BoundingBox) -> bool:
        """Asserts whether a point lies strictly inside a designated bounding box."""
        return bounds.contains(point)


coordinate_transformer = CoordinateTransformer()

