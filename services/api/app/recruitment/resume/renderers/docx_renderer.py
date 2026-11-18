"""Editable Microsoft Word DOCX Generation Engine (Stage 23)."""

from __future__ import annotations

import logging
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from app.recruitment.resume.contracts import (
    PageFormat,
    ResumeDocument,
    ResumeTemplateDefinition,
    SectionType,
)
from app.recruitment.resume.errors import DocumentExportError

logger = logging.getLogger("autonom.recruitment.resume.renderers.docx")


class DocxRenderer:
    """Renders canonical ResumeDocument instances into genuine, editable .docx files."""

    @classmethod
    def render_to_file(
        cls,
        doc: ResumeDocument,
        template: ResumeTemplateDefinition,
        output_path: str,
    ) -> str:
        try:
            document = Document()

            # 1. Page Setup & Margins
            section = document.sections[0]
            if doc.page_format == PageFormat.A4:
                section.page_width = Inches(8.27)
                section.page_height = Inches(11.69)
            else:
                section.page_width = Inches(8.5)
                section.page_height = Inches(11.0)

            section.top_margin = Inches(template.margin_top_in)
            section.bottom_margin = Inches(template.margin_bottom_in)
            section.left_margin = Inches(template.margin_left_in)
            section.right_margin = Inches(template.margin_right_in)

            # 2. Header: Applicant Name & Contact Info
            name = doc.header_contact.get("legal_name") or doc.title
            name_p = document.add_paragraph()
            name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            name_p.paragraph_format.space_after = Pt(2)
            name_run = name_p.add_run(name)
            name_run.font.name = template.heading_font.split("-")[0]
            name_run.font.size = Pt(template.title_font_size_pt)
            name_run.bold = True

            # Contact line
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
                c_p = document.add_paragraph()
                c_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                c_p.paragraph_format.space_after = Pt(8)
                c_run = c_p.add_run(" | ".join(contact_parts))
                c_run.font.name = template.primary_font.split("-")[0]
                c_run.font.size = Pt(template.base_font_size_pt - 0.5)

            # 3. Sections
            for sec in doc.sections:
                if not sec.is_visible or not sec.entries:
                    continue

                # Section Title
                h_p = document.add_paragraph()
                h_p.paragraph_format.space_before = Pt(8)
                h_p.paragraph_format.space_after = Pt(3)
                h_p.paragraph_format.keep_with_next = True
                h_run = h_p.add_run(sec.display_title.upper())
                h_run.font.name = template.heading_font.split("-")[0]
                h_run.font.size = Pt(template.heading_font_size_pt)
                h_run.bold = True

                # Entries
                if sec.section_type == SectionType.SUMMARY:
                    for entry in sec.entries:
                        s_p = document.add_paragraph()
                        s_p.paragraph_format.space_after = Pt(4)
                        s_run = s_p.add_run(entry.description or entry.title)
                        s_run.font.name = template.primary_font.split("-")[0]
                        s_run.font.size = Pt(template.base_font_size_pt)

                elif sec.section_type == SectionType.SKILLS:
                    for entry in sec.entries:
                        sk_p = document.add_paragraph()
                        sk_p.paragraph_format.space_after = Pt(2)
                        sk_title = sk_p.add_run(f"{entry.title}: ")
                        sk_title.font.name = template.primary_font.split("-")[0]
                        sk_title.font.size = Pt(template.base_font_size_pt)
                        sk_title.bold = True
                        sk_desc = sk_p.add_run(entry.description or ", ".join(entry.tags))
                        sk_desc.font.name = template.primary_font.split("-")[0]
                        sk_desc.font.size = Pt(template.base_font_size_pt)

                else:
                    for entry in sec.entries:
                        e_p = document.add_paragraph()
                        e_p.paragraph_format.space_before = Pt(4)
                        e_p.paragraph_format.space_after = Pt(1)
                        e_p.paragraph_format.keep_with_next = True

                        # Title & Organization
                        t_run = e_p.add_run(entry.title)
                        t_run.font.name = template.heading_font.split("-")[0]
                        t_run.font.size = Pt(template.base_font_size_pt + 0.5)
                        t_run.bold = True

                        if entry.subtitle or entry.organization:
                            org_str = f" — {entry.subtitle or entry.organization}"
                            o_run = e_p.add_run(org_str)
                            o_run.font.name = template.primary_font.split("-")[0]
                            o_run.font.size = Pt(template.base_font_size_pt)
                            o_run.italic = True

                        # Dates / Location
                        date_str = ""
                        if entry.start_date:
                            date_str = f" | {entry.start_date} - {entry.end_date or 'Present'}"
                        if entry.location:
                            date_str += f" ({entry.location})"
                        if date_str:
                            d_run = e_p.add_run(date_str)
                            d_run.font.name = template.primary_font.split("-")[0]
                            d_run.font.size = Pt(template.base_font_size_pt - 0.5)

                        # Description / Bullets
                        if entry.description and not entry.bullet_points:
                            desc_p = document.add_paragraph()
                            desc_p.paragraph_format.space_after = Pt(2)
                            desc_run = desc_p.add_run(entry.description)
                            desc_run.font.name = template.primary_font.split("-")[0]
                            desc_run.font.size = Pt(template.base_font_size_pt)

                        for b in entry.bullet_points:
                            b_p = document.add_paragraph(style="List Bullet")
                            b_p.paragraph_format.space_after = Pt(1)
                            b_run = b_p.add_run(b)
                            b_run.font.name = template.primary_font.split("-")[0]
                            b_run.font.size = Pt(template.base_font_size_pt)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            document.save(output_path)
            logger.info(f"Rendered DOCX successfully to '{output_path}'.")
            return output_path

        except Exception as exc:
            logger.error(f"Error rendering DOCX to '{output_path}': {exc}")
            raise DocumentExportError(f"DOCX rendering failed: {exc}") from exc
