"""Visual Document Preview Engine for Desktop React Client (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.resume.contracts import ResumeDocument, ResumeTemplateDefinition, SectionType

logger = logging.getLogger("autonom.recruitment.resume.renderers.preview")


class DocumentPreviewEngine:
    """Generates structured HTML & styling data for real-time document preview in the desktop client."""

    @classmethod
    def generate_html_preview(
        cls,
        doc: ResumeDocument,
        template: ResumeTemplateDefinition,
    ) -> str:
        name = doc.header_contact.get("legal_name") or doc.title
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

        contact_html = " &bull; ".join(contact_parts)

        sections_html = []
        for sec in doc.sections:
            if not sec.is_visible or not sec.entries:
                continue

            sec_entries_html = []
            if sec.section_type == SectionType.SUMMARY:
                for entry in sec.entries:
                    sec_entries_html.append(f'<p class="resume-summary">{entry.description or entry.title}</p>')

            elif sec.section_type == SectionType.SKILLS:
                for entry in sec.entries:
                    tags_str = entry.description or ", ".join(entry.tags)
                    sec_entries_html.append(f'<p class="resume-skill-line"><strong>{entry.title}:</strong> {tags_str}</p>')

            else:
                for entry in sec.entries:
                    org_str = f" &mdash; <em>{entry.subtitle or entry.organization}</em>" if (entry.subtitle or entry.organization) else ""
                    date_str = f'<span class="resume-date">{entry.start_date} - {entry.end_date or "Present"}</span>' if entry.start_date else ""
                    loc_str = f'<span class="resume-location">({entry.location})</span>' if entry.location else ""

                    bullets_html = ""
                    if entry.bullet_points:
                        bullets_li = "".join(f"<li>{b}</li>" for b in entry.bullet_points)
                        bullets_html = f'<ul class="resume-bullets">{bullets_li}</ul>'
                    elif entry.description:
                        bullets_html = f'<p class="resume-desc">{entry.description}</p>'

                    entry_html = f"""
                    <div class="resume-entry">
                        <div class="resume-entry-header">
                            <span class="resume-entry-title"><strong>{entry.title}</strong>{org_str}</span>
                            <div class="resume-entry-meta">{loc_str} {date_str}</div>
                        </div>
                        {bullets_html}
                    </div>
                    """
                    sec_entries_html.append(entry_html)

            divider = f'<hr class="resume-divider" style="border-top: 1px solid {template.accent_color};" />' if template.has_header_border else '<hr class="resume-divider" />'
            section_block = f"""
            <section class="resume-section">
                <h3 class="resume-section-title" style="color: {template.primary_color};">{sec.display_title.upper()}</h3>
                {divider}
                <div class="resume-section-content">
                    {"".join(sec_entries_html)}
                </div>
            </section>
            """
            sections_html.append(section_block)

        return f"""
        <div class="resume-sheet font-{template.primary_font.lower()}" style="--primary-color: {template.primary_color}; --accent-color: {template.accent_color};">
            <header class="resume-header">
                <h1 class="resume-name" style="color: {template.primary_color};">{name}</h1>
                <div class="resume-contact">{contact_html}</div>
            </header>
            <main class="resume-body">
                {"".join(sections_html)}
            </main>
        </div>
        """
