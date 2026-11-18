"""Tests for DPI-aware and multi-monitor visual coordinate transformations (Stage 18)."""

from app.visual.contracts import BoundingBox, NormalizedBox, Point2D
from app.visual.grounding.boxes import box_geometry
from app.visual.grounding.coordinates import coordinate_transformer


def test_normalized_to_pixel_box():
    """Test converting 0..1 normalized coordinates to image pixel bounding boxes."""
    norm = NormalizedBox(ymin=0.1, xmin=0.2, ymax=0.5, xmax=0.6)
    box = box_geometry.denormalize_box(norm, frame_width=1000, frame_height=1000)
    assert box.left == 200
    assert box.top == 100
    assert box.width == 400
    assert box.height == 400


def test_box_inward_target_point():
    """Test computing a safe interior target click point avoiding control edges."""
    box = BoundingBox(left=100, top=100, width=100, height=50)
    center = box_geometry.get_center_point(box)
    assert center.x == 150
    assert center.y == 125

    inward = box_geometry.get_inward_target_point(box, margin_ratio=0.1)
    # Target point must fall comfortably inside the control
    assert 100 < inward.x < 200
    assert 100 < inward.y < 150


def test_model_to_desktop_coordinate_transform():
    """Test transforming model-input coordinates to physical desktop pixels."""
    # Frame size 1920x1080, model scaled to 1000x1000
    pt = coordinate_transformer.transform_frame_to_desktop(
        Point2D(x=500, y=500),
        frame_width=1920,
        frame_height=1080,
        desktop_origin_x=0,
        desktop_origin_y=0,
    )
    assert pt.x == 500
    assert pt.y == 500

    # With desktop origin offset (e.g. secondary monitor at x=1920)
    pt_offset = coordinate_transformer.transform_frame_to_desktop(
        Point2D(x=100, y=100),
        frame_width=1920,
        frame_height=1080,
        desktop_origin_x=1920,
        desktop_origin_y=0,
    )
    assert pt_offset.x == 2020
    assert pt_offset.y == 100


def test_send_input_normalization():
    """Test normalizing absolute desktop coordinates to Windows SendInput 0..65535 space."""
    norm_x, norm_y = coordinate_transformer.to_sendinput_normalized_coords(
        Point2D(x=0, y=0),
        virtual_screen_rect={"left": 0, "top": 0, "width": 1920, "height": 1080},
    )
    assert 0 <= norm_x <= 100
    assert 0 <= norm_y <= 100

    max_x, max_y = coordinate_transformer.to_sendinput_normalized_coords(
        Point2D(x=1920, y=1080),
        virtual_screen_rect={"left": 0, "top": 0, "width": 1920, "height": 1080},
    )
    assert max_x == 65535
    assert max_y == 65535


def test_box_iou_intersection():
    """Test computing Intersection over Union for candidate deduplication."""
    b1 = BoundingBox(left=10, top=10, width=50, height=50)
    b2 = BoundingBox(left=10, top=10, width=50, height=50)
    iou = box_geometry.compute_iou(b1, b2)
    assert abs(iou - 1.0) < 0.001

    b3 = BoundingBox(left=100, top=100, width=50, height=50)
    iou_zero = box_geometry.compute_iou(b1, b3)
    assert iou_zero == 0.0
