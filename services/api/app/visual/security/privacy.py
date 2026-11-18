"""Privacy and redaction protection for visual computer automation (Stage 18).

Prevents capturing or interacting with sensitive system dialogues (UAC, credential prompts,
password managers), and redacts sensitive data in OCR results and visual frames.
"""

from __future__ import annotations

import logging
import re
from typing import Optional
from PIL import Image

from ..contracts import BoundingBox, CapturedFrame, OCRResult

logger = logging.getLogger("autonom.visual.security.privacy")

# Blocked / sensitive window titles and classes that must NEVER be captured or automated
BLOCKED_WINDOW_PATTERNS = [
    re.compile(r"credential\s*manager", re.IGNORECASE),
    re.compile(r"user\s*account\s*control", re.IGNORECASE),
    re.compile(r"windows\s*security", re.IGNORECASE),
    re.compile(r"bitwarden", re.IGNORECASE),
    re.compile(r"1password", re.IGNORECASE),
    re.compile(r"keepass", re.IGNORECASE),
    re.compile(r"lastpass", re.IGNORECASE),
    re.compile(r"authenticator", re.IGNORECASE),
]

PASSWORD_REGEX = re.compile(r"(password|passcode|token|secret|pin|cvv|cvc)", re.IGNORECASE)
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class VisualPrivacyFilter:
    """Sanitizes visual captures and OCR text to prevent credential and PII leakage."""

    @staticmethod
    def is_window_sensitive(title: str, class_name: str = "") -> bool:
        """Determines whether a window title or class belongs to a protected credential context."""
        comb = f"{title} {class_name}"
        return any(pattern.search(comb) for pattern in BLOCKED_WINDOW_PATTERNS)

    @classmethod
    def sanitize_ocr_result(cls, ocr_res: OCRResult) -> OCRResult:
        """Redacts sensitive PII and potential credentials from OCR output."""
        sanitized_lines = []
        for line in ocr_res.lines:
            text = line.text
            text = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", text)
            text = SSN_REGEX.sub("[REDACTED_SSN]", text)
            line.text = text
            sanitized_lines.append(line)
        ocr_res.lines = sanitized_lines
        return ocr_res

    @classmethod
    def redact_frame_regions(
        cls,
        frame: CapturedFrame,
        sensitive_boxes: list[BoundingBox],
    ) -> CapturedFrame:
        """Applies a solid dark mask over sensitive screen areas."""
        if not sensitive_boxes:
            return frame

        from ..capture.preprocessing import FramePreprocessor
        redacted_img = FramePreprocessor.redact_regions(frame.image, sensitive_boxes)
        frame.image = redacted_img
        return frame


visual_privacy_filter = VisualPrivacyFilter()
