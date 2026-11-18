"""Screenshot image preprocessing, scaling, cropping, and privacy masking (Stage 18)."""

import base64
import hashlib
import io
import logging
from PIL import Image, ImageChops
from app.visual.contracts import BoundingBox

logger = logging.getLogger("autonom.visual.capture.preprocessing")


class FramePreprocessor:
    """Processes, resizes, crops, and sanitizes screenshot frames for vision models and UI."""

    @staticmethod
    def scale_image(
        image: Image.Image,
        max_dimension: int = 1600,
    ) -> tuple[Image.Image, float]:
        """Scales image down if larger than max_dimension, preserving aspect ratio.
        Returns the (scaled_image, scale_factor).
        """
        orig_w, orig_h = image.size
        max_side = max(orig_w, orig_h)
        if max_side <= max_dimension:
            return image.copy(), 1.0

        scale_factor = round(max_dimension / float(max_side), 4)
        new_w = max(1, int(orig_w * scale_factor))
        new_h = max(1, int(orig_h * scale_factor))
        scaled = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return scaled, scale_factor

    @staticmethod
    def resize_preserving_aspect(image: Image.Image, max_dim: int = 1600) -> Image.Image:
        """Alias returning just the resized Pillow Image."""
        scaled, _ = FramePreprocessor.scale_image(image, max_dimension=max_dim)
        return scaled

    @staticmethod
    def crop_region(image: Image.Image, box: BoundingBox) -> Image.Image:
        """Crops specified bounding box region from the image safely within boundaries."""
        w, h = image.size
        left = max(0, min(w - 1, box.left))
        top = max(0, min(h - 1, box.top))
        right = max(left + 1, min(w, box.right))
        bottom = max(top + 1, min(h, box.bottom))
        return image.crop((left, top, right, bottom))

    @staticmethod
    def mask_regions(image: Image.Image, sensitive_regions: list[BoundingBox]) -> Image.Image:
        """Redacts specified sensitive regions by painting solid black rectangles over them."""
        if not sensitive_regions:
            return image

        masked = image.copy()
        from PIL import ImageDraw
        draw = ImageDraw.Draw(masked)

        for region in sensitive_regions:
            draw.rectangle(
                [region.left, region.top, region.right, region.bottom],
                fill=(0, 0, 0),
                outline=(255, 0, 0),
            )
        return masked

    @staticmethod
    def redact_regions(image: Image.Image, sensitive_regions: list[BoundingBox]) -> Image.Image:
        """Alias for mask_regions."""
        return FramePreprocessor.mask_regions(image, sensitive_regions)

    @staticmethod
    def to_base64_png(image: Image.Image) -> str:
        """Encodes Pillow Image into a base64 PNG data string."""
        buf = io.BytesIO()
        image.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    @staticmethod
    def compute_image_hash(image: Image.Image) -> str:
        """Computes a SHA-256 hash of raw pixel bytes for frame deduplication and change detection."""
        return hashlib.sha256(image.tobytes()).hexdigest()

    @staticmethod
    def compute_content_hash(image: Image.Image) -> str:
        """Alias for compute_image_hash."""
        return FramePreprocessor.compute_image_hash(image)

    @staticmethod
    def calculate_frame_diff_percentage(img_a: Image.Image, img_b: Image.Image) -> float:
        """Calculates pixel difference percentage between two frames of the same size."""
        if img_a.size != img_b.size:
            img_b = img_b.resize(img_a.size, Image.Resampling.NEAREST)

        diff = ImageChops.difference(img_a.convert("RGB"), img_b.convert("RGB"))
        bbox = diff.getbbox()
        if not bbox:
            return 0.0

        # Calculate percentage of differing pixels
        gray_diff = diff.convert("L")
        data_iter = gray_diff.get_flattened_data() if hasattr(gray_diff, "get_flattened_data") else gray_diff.getdata()
        non_zero_pixels = sum(1 for pixel in data_iter if pixel > 15)
        total_pixels = img_a.size[0] * img_a.size[1]
        return round((non_zero_pixels / float(total_pixels)) * 100.0, 2)

    @staticmethod
    def compute_frame_difference(img_a: Image.Image, img_b: Image.Image) -> float:
        """Alias for calculate_frame_diff_percentage."""
        return FramePreprocessor.calculate_frame_diff_percentage(img_a, img_b)


frame_preprocessor = FramePreprocessor()

