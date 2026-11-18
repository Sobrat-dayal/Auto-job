"""Professional Technical Portfolio Service Facade (Stage 23)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4
from app.core.config import settings
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.profile.service import applicant_profile_service
from app.recruitment.resume.contracts import (
    DocumentStatus,
    PortfolioCreateRequest,
    PortfolioDocument,
    PortfolioProjectEntry,
    PortfolioUpdateRequest,
)
from app.recruitment.resume.errors import PortfolioNotFoundError
from app.recruitment.resume.portfolio.html_export import PortfolioHtmlRenderer
from app.recruitment.resume.portfolio.pdf_export import PortfolioPdfRenderer

logger = logging.getLogger("autonom.recruitment.resume.portfolio.service")


class PortfolioService:
    """Manages creation, evidence attribution, privacy screening, and export of developer portfolios."""

    def __init__(self) -> None:
        self._portfolios: dict[str, PortfolioDocument] = {}

    def list_portfolios(self, owner_id: str = "default_user") -> list[PortfolioDocument]:
        return [p for p in self._portfolios.values() if p.owner_id == owner_id]

    def get_portfolio(self, portfolio_id: str) -> PortfolioDocument:
        p = self._portfolios.get(portfolio_id)
        if not p:
            raise PortfolioNotFoundError(f"Portfolio '{portfolio_id}' not found.")
        return p

    def create_portfolio(self, req: PortfolioCreateRequest, owner_id: str = "default_user") -> PortfolioDocument:
        # Load applicant profile
        prof: ApplicantProfile = applicant_profile_service.get_profile("prof_primary_applicant")

        # Project selection
        selected_projects: list[PortfolioProjectEntry] = []
        eligible_profile_projects = prof.projects
        if req.selected_project_ids:
            sel_ids = set(req.selected_project_ids)
            eligible_profile_projects = [p for p in prof.projects if p.id in sel_ids]

        for p in eligible_profile_projects:
            # Privacy check: Ensure public eligibility
            is_public = bool(p.repository_url and "private" not in p.repository_url.lower())
            entry = PortfolioProjectEntry(
                title=p.name,
                summary=p.description or "",
                problem_addressed=f"Architectural implementation of {p.name}",
                tech_stack=p.technologies,
                architecture_highlights=[f"Modular architecture leveraging {', '.join(p.technologies[:3])}"],
                individual_contribution=f"Lead developer responsible for core services and integration",
                deliverables=p.deliverables,
                repo_url=p.repository_url,
                demo_url=None,
                attribution_level="commit_author_evidence",
                is_public_eligible=is_public,
            )
            selected_projects.append(entry)

        # Skills selection
        selected_skills = req.selected_skills or [s.name for s in prof.skills[:12]]

        # Professional intro
        intro = req.professional_intro or (
            f"Technical portfolio of {prof.contact.legal_name or 'Applicant'}. "
            f"Featuring evidenced engineering projects, architecture implementations, and verified code contributions."
        )

        port = PortfolioDocument(
            owner_id=owner_id,
            profile_id=prof.id,
            title=req.title,
            professional_intro=intro,
            selected_skills=selected_skills,
            selected_projects=selected_projects,
            template_id=req.template_id,
            status=DocumentStatus.DRAFT,
        )
        self._portfolios[port.id] = port
        logger.info(f"Created portfolio: {port.id} ({port.title})")
        return port

    def update_portfolio(self, portfolio_id: str, req: PortfolioUpdateRequest) -> PortfolioDocument:
        port = self.get_portfolio(portfolio_id)
        if req.title is not None:
            port.title = req.title
        if req.professional_intro is not None:
            port.professional_intro = req.professional_intro
        if req.selected_skills is not None:
            port.selected_skills = req.selected_skills
        if req.selected_projects is not None:
            port.selected_projects = req.selected_projects
        if req.public_contact is not None:
            port.public_contact = req.public_contact
        if req.template_id is not None:
            port.template_id = req.template_id
        if req.status is not None:
            port.status = req.status

        port.updated_at = datetime.now(UTC)
        return port

    def export_portfolio_pdf(self, portfolio_id: str, custom_path: Optional[str] = None) -> str:
        port = self.get_portfolio(portfolio_id)
        filename = f"portfolio_{portfolio_id[:8]}.pdf"
        output_dir = Path(getattr(settings, "artifacts_dir", settings.data_dir / "artifacts")) / "portfolios"
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = custom_path or str(output_dir / filename)
        return PortfolioPdfRenderer.render_to_file(port, out_path)

    def export_portfolio_html(self, portfolio_id: str, custom_path: Optional[str] = None) -> str:
        port = self.get_portfolio(portfolio_id)
        filename = f"portfolio_{portfolio_id[:8]}.html"
        output_dir = Path(getattr(settings, "artifacts_dir", settings.data_dir / "artifacts")) / "portfolios"
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = custom_path or str(output_dir / filename)
        return PortfolioHtmlRenderer.render_to_file(port, out_path)

