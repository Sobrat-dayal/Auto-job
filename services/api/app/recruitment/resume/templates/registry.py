"""Resume Template Registry & Layout Parameters (Stage 23)."""

from __future__ import annotations

import logging
from typing import Optional
from app.recruitment.resume.contracts import PageFormat, ResumeTemplateDefinition
from app.recruitment.resume.errors import TemplateNotFoundError
from app.recruitment.resume.templates.definitions import CORE_TEMPLATES

logger = logging.getLogger("autonom.recruitment.resume.templates.registry")


class ResumeTemplateRegistry:
    """Versioned registry for document templates."""

    _templates: dict[str, ResumeTemplateDefinition] = dict(CORE_TEMPLATES)

    @classmethod
    def list_templates(cls) -> list[ResumeTemplateDefinition]:
        return list(cls._templates.values())

    @classmethod
    def get_template(cls, template_id: str) -> ResumeTemplateDefinition:
        t = cls._templates.get(template_id)
        if not t:
            raise TemplateNotFoundError(f"Resume template '{template_id}' is not registered.")
        return t

    @classmethod
    def register_template(cls, template: ResumeTemplateDefinition) -> None:
        cls._templates[template.id] = template
        logger.info(f"Registered resume template: {template.id} v{template.version}")

    @classmethod
    def get_page_dimensions_pt(cls, page_format: PageFormat) -> tuple[float, float]:
        """Returns (width_pt, height_pt) for standard page formats (72 points per inch)."""
        if page_format == PageFormat.A4:
            return (595.28, 841.89)  # 210mm x 297mm
        return (612.0, 792.0)  # US Letter: 8.5in x 11.0in
