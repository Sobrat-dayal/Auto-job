"""Changes module for Stage 30 Recruitment Monitoring."""

from app.recruitment.monitoring.changes.detection import DetectedChange, detect_job_changes
from app.recruitment.monitoring.changes.semantic import (
    compute_content_hash,
    is_material_description_change,
    normalize_content,
)

__all__ = [
    "DetectedChange",
    "detect_job_changes",
    "normalize_content",
    "compute_content_hash",
    "is_material_description_change",
]
