"""Preprocessing package for text cleaning, segmentation, and span mapping."""

from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import (
    JobSection,
    segment_job_description,
)
from app.recruitment.intelligence.preprocessing.source_offsets import (
    compute_quote_hash,
    create_evidence,
    find_source_span,
)

__all__ = [
    "JobSection",
    "clean_html_description",
    "compute_quote_hash",
    "create_evidence",
    "find_source_span",
    "segment_job_description",
]
