"""Cover Letter Template Registry & Styling Definitions (Stage 24)."""

from __future__ import annotations

import logging
from typing import Optional
from app.recruitment.writing.contracts import CoverLetterTemplateDefinition
from app.recruitment.writing.errors import WritingDomainError

logger = logging.getLogger("autonom.recruitment.writing.cover_letters.templates")


class CoverLetterTemplateRegistry:
    """Registry of professional, ATS-compatible cover letter templates."""

    _TEMPLATES: dict[str, CoverLetterTemplateDefinition] = {}

    @classmethod
    def initialize(cls) -> None:
        if cls._TEMPLATES:
            return

        templates = [
            CoverLetterTemplateDefinition(
                id="classic_professional",
                name="Classic Professional",
                description="Timeless standard business letter format with balanced margins and traditional serif/sans typography.",
                category="professional",
                version="1.0.0",
                primary_font="Helvetica",
                heading_font="Helvetica-Bold",
                base_font_size_pt=10.5,
                heading_font_size_pt=13.0,
                margin_top_in=0.8,
                margin_bottom_in=0.8,
                margin_left_in=0.8,
                margin_right_in=0.8,
                primary_color="#1e293b",
                accent_color="#0284c7",
                text_color="#0f172a",
                line_spacing=1.15,
                layout_style="classic",
            ),
            CoverLetterTemplateDefinition(
                id="modern_minimalist",
                name="Modern Minimalist",
                description="Clean, contemporary aesthetic with ample whitespace, subtle section dividers, and clean geometry.",
                category="modern",
                version="1.0.0",
                primary_font="Helvetica",
                heading_font="Helvetica-Bold",
                base_font_size_pt=10.0,
                heading_font_size_pt=12.5,
                margin_top_in=0.75,
                margin_bottom_in=0.75,
                margin_left_in=0.75,
                margin_right_in=0.75,
                primary_color="#0f172a",
                accent_color="#3b82f6",
                text_color="#1e293b",
                line_spacing=1.2,
                layout_style="modern",
            ),
            CoverLetterTemplateDefinition(
                id="technical_engineering",
                name="Technical Engineering",
                description="Optimized for software engineering and systems roles with dense skill callouts and project evidence.",
                category="technical",
                version="1.0.0",
                primary_font="Helvetica",
                heading_font="Helvetica-Bold",
                base_font_size_pt=10.0,
                heading_font_size_pt=12.0,
                margin_top_in=0.7,
                margin_bottom_in=0.7,
                margin_left_in=0.7,
                margin_right_in=0.7,
                primary_color="#0f172a",
                accent_color="#0ea5e9",
                text_color="#1e293b",
                line_spacing=1.15,
                layout_style="technical",
            ),
            CoverLetterTemplateDefinition(
                id="internship_graduate",
                name="Internship / Graduate",
                description="Tailored for university students and new graduates emphasizing academic foundations and hands-on projects.",
                category="early_career",
                version="1.0.0",
                primary_font="Helvetica",
                heading_font="Helvetica-Bold",
                base_font_size_pt=10.5,
                heading_font_size_pt=13.0,
                margin_top_in=0.8,
                margin_bottom_in=0.8,
                margin_left_in=0.8,
                margin_right_in=0.8,
                primary_color="#1e293b",
                accent_color="#10b981",
                text_color="#0f172a",
                line_spacing=1.2,
                layout_style="compact",
            ),
            CoverLetterTemplateDefinition(
                id="academic_research",
                name="Academic / Research",
                description="Formal layout structured for academic posts, lab fellowships, and scientific research opportunities.",
                category="academic",
                version="1.0.0",
                primary_font="Times-Roman",
                heading_font="Times-Bold",
                base_font_size_pt=11.0,
                heading_font_size_pt=14.0,
                margin_top_in=1.0,
                margin_bottom_in=1.0,
                margin_left_in=1.0,
                margin_right_in=1.0,
                primary_color="#1e1e1e",
                accent_color="#475569",
                text_color="#1e1e1e",
                line_spacing=1.25,
                layout_style="academic",
            ),
            CoverLetterTemplateDefinition(
                id="compact_application",
                name="Compact Application Letter",
                description="Concise 1-page condensed layout for portals with tight word count or spatial constraints.",
                category="compact",
                version="1.0.0",
                primary_font="Helvetica",
                heading_font="Helvetica-Bold",
                base_font_size_pt=9.5,
                heading_font_size_pt=11.5,
                margin_top_in=0.6,
                margin_bottom_in=0.6,
                margin_left_in=0.6,
                margin_right_in=0.6,
                primary_color="#1e293b",
                accent_color="#6366f1",
                text_color="#0f172a",
                line_spacing=1.1,
                layout_style="compact",
            ),
        ]

        for t in templates:
            cls._TEMPLATES[t.id] = t
        logger.info(f"Registered {len(cls._TEMPLATES)} Cover Letter Templates")

    @classmethod
    def list_templates(cls) -> list[CoverLetterTemplateDefinition]:
        cls.initialize()
        return list(cls._TEMPLATES.values())

    @classmethod
    def get_template(cls, template_id: str) -> CoverLetterTemplateDefinition:
        cls.initialize()
        tpl = cls._TEMPLATES.get(template_id)
        if not tpl:
            return cls._TEMPLATES["classic_professional"]
        return tpl


CoverLetterTemplateRegistry.initialize()
