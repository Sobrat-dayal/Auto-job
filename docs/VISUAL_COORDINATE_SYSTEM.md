# Visual Coordinate Systems & Transformations (Stage 18)

## 1. Multi-Coordinate Representation

Desktop visual automation operates across four distinct coordinate reference frames:

```
[Vision Model Space]      [Normalized Space]      [Raw Frame Space]      [Desktop Screen Space]
   (e.g. 1000x1000)   ──►    (0.0 to 1.0)     ──►    (1920x1080)     ──►     (0..65535 SendInput)
```

1. **Normalized Space `[0.0, 1.0]`**:
   Model-agnostic relative coordinates represented by `NormalizedBox`. Supports standard `{x_min, y_min, x_max, y_max}` and common VLM aliases (`xmin`, `ymin`, `xmax`, `ymax`).
2. **Raw Frame Pixel Space**:
   Physical pixel coordinates of the captured screenshot represented by `BoundingBox` and `Point2D`.
3. **Physical Desktop Screen Space**:
   Virtual desktop pixel coordinates covering all monitors, including secondary displays with negative origins (e.g., monitor positioned to the left of primary display at `x = -1920`).
4. **Windows `SendInput` Normalized Absolute Space `[0, 65535]`**:
   Required by Windows `MOUSEEVENTF_ABSOLUTE` mouse events.

---

## 2. Coordinate Transformer Pipelines

`CoordinateTransformer` (`app/visual/grounding/coordinates.py`) guarantees mathematically verified transformations:

### Model Space to Raw Frame
```python
inv_scale = 1.0 / metadata.scale_factor
raw_x = int(model_x * inv_scale)
raw_y = int(model_y * inv_scale)
```

### Raw Frame to Physical Desktop
```python
desktop_x = raw_x + (metadata.crop_box.left if metadata.crop_box else 0)
desktop_y = raw_y + (metadata.crop_box.top if metadata.crop_box else 0)
```

### Physical Desktop to SendInput Absolute Space (0..65535)
```python
norm_x = int((desktop_x - virtual_left) * 65535.0 / virtual_width)
norm_y = int((desktop_y - virtual_top) * 65535.0 / virtual_height)
```

---

## 3. Box Geometry & Inward Target Offsetting

To prevent interaction failures from clicking directly on control borders or drop shadows:
- `box_geometry.get_safe_target_point`: Calculates the exact geometric center of the control with mandatory inward margin bounds (`min 2px`).
- `box_geometry.calculate_iou`: Computes Intersection over Union for candidate deduplication and bounding box suppression.
- `box_geometry.denormalize_box`: Converts normalized bounding boxes into discrete integer pixel bounds using floating-point rounding.
