"""Professional Multi-Page Portfolio PDF Export Engine (Stage 23)."""

from __future__ import annotations

import logging
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer
from app.recruitment.resume.contracts import PortfolioDocument
from app.recruitment.resume.errors import DocumentExportError
from app.recruitment.resume.renderers.pdf_renderer import NumberedCanvas

logger = logging.getLogger("autonom.recruitment.resume.portfolio.pdf_export")


class PortfolioPdfRenderer:
    """Generates multi-page professional technical portfolio documents in PDF format."""

    @classmethod
    def render_to_file(
        cls,
        portfolio: PortfolioDocument,
        output_path: str,
    ) -> str:
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                leftMargin=0.6 * inch,
                rightMargin=0.6 * inch,
                topMargin=0.6 * inch,
                bottomMargin=0.6 * inch,
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "PortTitle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=HexColor("#0F172A"),
                alignment=TA_CENTER,
                spaceAfter=4,
            )

            intro_style = ParagraphStyle(
                "PortIntro",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10.5,
                leading=15,
                textColor=HexColor("#334155"),
                alignment=TA_CENTER,
                spaceAfter=12,
            )

            section_head_style = ParagraphStyle(
                "PortSecHead",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                textColor=HexColor("#0284C7"),
                spaceBefore=12,
                spaceAfter=4,
                keepWithNext=True,
            )

            proj_title_style = ParagraphStyle(
                "PortProjTitle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=16,
                textColor=HexColor("#0F172A"),
                spaceBefore=6,
                spaceAfter=2,
                keepWithNext=True,
            )

            tech_tag_style = ParagraphStyle(
                "PortTechTags",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                textColor=HexColor("#0369A1"),
                spaceAfter=4,
            )

            body_style = ParagraphStyle(
                "PortBody",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=HexColor("#1E293B"),
                spaceAfter=4,
            )

            story = []

            # 1. Title & Intro
            story.append(Paragraph(portfolio.title, title_style))
            if portfolio.professional_intro:
                story.append(Paragraph(portfolio.professional_intro, intro_style))

            story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#0284C7"), spaceAfter=10))

            # 2. Key Skills Banner
            if portfolio.selected_skills:
                skills_str = " &nbsp;&bull;&nbsp; ".join(portfolio.selected_skills)
                story.append(Paragraph("<b>CORE TECHNICAL EXPERTISE</b>", section_head_style))
                story.append(Paragraph(skills_str, body_style))
                story.append(Spacer(1, 8))

            # 3. Selected Projects
            story.append(Paragraph("<b>FEATURED ENGINEERING PROJECTS</b>", section_head_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))

            for prj in portfolio.selected_projects:
                proj_flowables = []

                # Project Title & Link
                link_str = f" &nbsp;[<font color='#0284C7'>{prj.repo_url}</font>]" if prj.repo_url and prj.is_public_eligible else ""
                proj_flowables.append(Paragraph(f"{prj.title}{link_str}", proj_title_style))

                # Tech Stack
                if prj.tech_stack:
                    proj_flowables.append(Paragraph(f"<b>Tech Stack:</b> {', '.join(prj.tech_stack)}", tech_tag_style))

                # Summary & Problem
                if prj.summary:
                    proj_flowables.append(Paragraph(f"<b>Overview:</b> {prj.summary}", body_style))
                if prj.problem_addressed:
                    proj_flowables.append(Paragraph(f"<b>Problem Solved:</b> {prj.problem_addressed}", body_style))

                # Individual Contribution
                if prj.individual_contribution:
                    proj_flowables.append(Paragraph(f"<b>Individual Contribution:</b> {prj.individual_contribution}", body_style))

                # Deliverables
                if prj.deliverables:
                    deliv_bullets = "".join(f"&bull;&nbsp; {d}<br/>" for d in prj.deliverables)
                    proj_flowables.append(Paragraph(f"<b>Deliverables:</b><br/>{deliv_bullets}", body_style))

                proj_flowables.append(Spacer(1, 10))
                story.append(KeepTogether(proj_flowables))

            pdf_doc.build(story, canvasmaker=NumberedCanvas)
            logger.info(f"Rendered Portfolio PDF successfully to '{output_path}'.")
            return output_path

        except Exception as exc:
            logger.error(f"Error rendering Portfolio PDF to '{output_path}': {exc}")
            raise DocumentExportError(f"Portfolio PDF rendering failed: {exc}") from exc
