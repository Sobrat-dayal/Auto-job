"""Genuine Selectable PDF Generation Engine using ReportLab (Stage 23)."""

from __future__ import annotations

import logging
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
from app.recruitment.resume.contracts import (
    PageFormat,
    ResumeDocument,
    ResumeTemplateDefinition,
    SectionType,
)
from app.recruitment.resume.errors import DocumentExportError

logger = logging.getLogger("autonom.recruitment.resume.renderers.pdf")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas providing accurate 'Page X of Y' footer page numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        if page_count > 1:
            self.setFont("Helvetica", 8)
            self.setFillColor(HexColor("#666666"))
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(self._pagesize[0] - 0.5 * inch, 0.35 * inch, page_text)


class PdfRenderer:
    """Renders canonical ResumeDocument instances into genuine PDFs with selectable text."""

    @classmethod
    def render_to_file(
        cls,
        doc: ResumeDocument,
        template: ResumeTemplateDefinition,
        output_path: str,
    ) -> str:
        try:
            pagesize = A4 if doc.page_format == PageFormat.A4 else letter
            margin_top = template.margin_top_in * inch
            margin_bottom = template.margin_bottom_in * inch
            margin_left = template.margin_left_in * inch
            margin_right = template.margin_right_in * inch

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=pagesize,
                leftMargin=margin_left,
                rightMargin=margin_right,
                topMargin=margin_top,
                bottomMargin=margin_bottom,
            )

            styles = getSampleStyleSheet()

            # Custom typography styles
            name_style = ParagraphStyle(
                "ResumeName",
                parent=styles["Normal"],
                fontName=template.heading_font if template.heading_font in ("Helvetica-Bold", "Times-Bold") else "Helvetica-Bold",
                fontSize=template.title_font_size_pt,
                leading=template.title_font_size_pt + 2,
                alignment=TA_CENTER,
                textColor=HexColor(template.primary_color),
                spaceAfter=2,
            )

            contact_style = ParagraphStyle(
                "ResumeContact",
                parent=styles["Normal"],
                fontName=template.primary_font if template.primary_font in ("Helvetica", "Times-Roman") else "Helvetica",
                fontSize=template.base_font_size_pt - 0.5,
                leading=template.base_font_size_pt + 2,
                alignment=TA_CENTER,
                textColor=HexColor("#4A5568"),
                spaceAfter=6,
            )

            heading_style = ParagraphStyle(
                "ResumeHeading",
                parent=styles["Normal"],
                fontName=template.heading_font if template.heading_font in ("Helvetica-Bold", "Times-Bold") else "Helvetica-Bold",
                fontSize=template.heading_font_size_pt,
                leading=template.heading_font_size_pt + 3,
                textColor=HexColor(template.primary_color),
                spaceBefore=6,
                spaceAfter=2,
                keepWithNext=True,
            )

            entry_title_style = ParagraphStyle(
                "ResumeEntryTitle",
                parent=styles["Normal"],
                fontName=template.heading_font if template.heading_font in ("Helvetica-Bold", "Times-Bold") else "Helvetica-Bold",
                fontSize=template.base_font_size_pt + 0.5,
                leading=template.base_font_size_pt + 3,
                textColor=HexColor(template.primary_color),
                spaceBefore=4,
                spaceAfter=1,
                keepWithNext=True,
            )

            body_style = ParagraphStyle(
                "ResumeBody",
                parent=styles["Normal"],
                fontName=template.primary_font if template.primary_font in ("Helvetica", "Times-Roman") else "Helvetica",
                fontSize=template.base_font_size_pt,
                leading=template.base_font_size_pt + 3,
                textColor=HexColor("#1F2937"),
                spaceAfter=2,
            )

            story = []

            # 1. Header: Name & Contact
            name = doc.header_contact.get("legal_name") or doc.title
            story.append(Paragraph(name, name_style))

            contact_parts = []
            if doc.header_contact.get("primary_email"):
                contact_parts.append(doc.header_contact["primary_email"])
            if doc.header_contact.get("phone"):
                contact_parts.append(doc.header_contact["phone"])
            if doc.header_contact.get("location"):
                contact_parts.append(doc.header_contact["location"])
            if doc.header_contact.get("github_url"):
                contact_parts.append(doc.header_contact["github_url"])
            if doc.header_contact.get("linkedin_url"):
                contact_parts.append(doc.header_contact["linkedin_url"])

            if contact_parts:
                story.append(Paragraph(" &nbsp;|&nbsp; ".join(contact_parts), contact_style))

            if template.has_header_border:
                story.append(HRFlowable(width="100%", thickness=0.8, color=HexColor(template.accent_color), spaceAfter=6))

            # 2. Sections
            for sec in doc.sections:
                if not sec.is_visible or not sec.entries:
                    continue

                story.append(Paragraph(sec.display_title.upper(), heading_style))
                story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#CBD5E1"), spaceAfter=3))

                if sec.section_type == SectionType.SUMMARY:
                    for entry in sec.entries:
                        text = entry.description or entry.title
                        story.append(Paragraph(text, body_style))

                elif sec.section_type == SectionType.SKILLS:
                    for entry in sec.entries:
                        skill_line = f"<b>{entry.title}:</b> {entry.description or ', '.join(entry.tags)}"
                        story.append(Paragraph(skill_line, body_style))

                else:
                    for entry in sec.entries:
                        # Entry Header Line (Title, Organization, Dates)
                        org_info = f" &mdash; <i>{entry.subtitle or entry.organization}</i>" if (entry.subtitle or entry.organization) else ""
                        dates_info = ""
                        if entry.start_date:
                            dates_info = f" <font color='#6B7280'>| {entry.start_date} - {entry.end_date or 'Present'}</font>"
                        header_line = f"<b>{entry.title}</b>{org_info}{dates_info}"
                        story.append(Paragraph(header_line, entry_title_style))

                        if entry.description and not entry.bullet_points:
                            story.append(Paragraph(entry.description, body_style))

                        # Bullet points
                        for b in entry.bullet_points:
                            bullet_text = f"&bull;&nbsp; {b}"
                            story.append(Paragraph(bullet_text, body_style))

            pdf_doc.build(story, canvasmaker=NumberedCanvas)
            logger.info(f"Rendered PDF successfully to '{output_path}'.")
            return output_path

        except Exception as exc:
            logger.error(f"Error rendering PDF to '{output_path}': {exc}")
            raise DocumentExportError(f"PDF rendering failed: {exc}") from exc
