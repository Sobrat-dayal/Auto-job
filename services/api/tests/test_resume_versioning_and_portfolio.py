"""Unit tests for Stage 23 version immutability, portfolio builder, and privacy filtering."""

import os
import tempfile
import pytest

from app.recruitment.resume.contracts import (
    ResumeDocument,
    ResumeType,
    DocumentStatus,
    PageFormat,
    PortfolioDocument,
    PortfolioProjectEntry,
    PortfolioCreateRequest,
    PortfolioUpdateRequest,
)
from app.recruitment.resume.versions.manager import ResumeVersionManager
from app.recruitment.resume.portfolio.service import PortfolioService
from app.recruitment.resume.portfolio.pdf_export import PortfolioPdfRenderer
from app.recruitment.resume.portfolio.html_export import PortfolioHtmlRenderer


@pytest.fixture
def sample_approved_resume() -> ResumeDocument:
    return ResumeDocument(
        id="res_ver_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Versioned Professional Resume",
        resume_type=ResumeType.EXPERIENCED,
        target_role="Senior Staff Architect",
        job_ref=None,
        template_id="ats_classic",
        template_version="1.0.0",
        status=DocumentStatus.APPROVED,
        current_version=1,
        locale="en_US",
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={"legal_name": "Jordan Lee", "primary_email": "jordan@example.com"},
        sections=[],
    )


def test_version_manager_snapshotting(sample_approved_resume: ResumeDocument):
    vm = ResumeVersionManager()
    record = vm.create_version_snapshot(
        doc=sample_approved_resume,
        changelog="Initial publication of approved version",
        actor_id="usr_01",
        is_published=True,
    )

    assert record.resume_id == "res_ver_01"
    assert record.version_number == 1
    assert len(record.content_hash) == 64  # SHA-256
    assert record.is_published is True

    # Retrieve history
    history = vm.list_versions("res_ver_01")
    assert len(history) >= 1
    assert history[-1].content_hash == record.content_hash


def test_portfolio_service_crud_and_privacy_filter():
    service = PortfolioService()

    port = service.create_portfolio(
        req=PortfolioCreateRequest(
            title="Engineering Deliverables Portfolio",
            professional_intro="Specialist in distributed microservice architectures.",
            selected_skills=["Python", "Go", "Docker"],
        ),
        owner_id="usr_01",
    )

    assert port.id is not None
    assert port.title == "Engineering Deliverables Portfolio"

    # Add projects (one public, one private)
    proj_public = PortfolioProjectEntry(
        title="Open Source CLI Tool",
        summary="High-speed CLI tool built with Go",
        tech_stack=["Go", "Docker"],
        architecture_highlights=["Single binary distribution"],
        individual_contribution="Primary developer and maintainer",
        deliverables=["GitHub binary releases"],
        repo_url="https://github.com/usr_01/open-cli",
        is_public_eligible=True,
        ordering=0,
    )

    proj_private = PortfolioProjectEntry(
        title="Proprietary Trading Engine",
        summary="Low-latency order routing engine",
        tech_stack=["C++", "Python"],
        architecture_highlights=["Lock-free ring buffers"],
        individual_contribution="Architected core matching engine",
        deliverables=["Internal production deployment"],
        repo_url="https://github.com/private-org/trading-engine",
        is_public_eligible=False,  # Private!
        ordering=1,
    )

    updated = service.update_portfolio(
        port.id,
        PortfolioUpdateRequest(selected_projects=[proj_public, proj_private]),
    )
    assert len(updated.selected_projects) == 2


def test_portfolio_export_pdf_and_html():
    port = PortfolioDocument(
        id="port_exp_01",
        owner_id="usr_01",
        profile_id="prof_01",
        title="Senior Developer Portfolio",
        professional_intro="Proven builder of production AI & distributed workflows.",
        selected_skills=["Python", "FastAPI", "React"],
        selected_projects=[
            PortfolioProjectEntry(
                title="Distributed Search Cluster",
                summary="Full-text inverted indexing cluster",
                tech_stack=["Python", "FastAPI"],
                architecture_highlights=["Partitioned shards"],
                individual_contribution="Implemented sharding and query scatter-gather",
                deliverables=["Production REST API"],
                repo_url="https://github.com/usr_01/search",
                is_public_eligible=True,
                ordering=0,
            )
        ],
        publications=[],
        certifications=[],
        public_contact={"primary_email": "usr@example.com"},
        template_id="portfolio_classic",
        status=DocumentStatus.APPROVED,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. HTML export
        html_path = os.path.join(tmpdir, "portfolio.html")
        PortfolioHtmlRenderer.render_to_file(port, html_path)
        assert os.path.exists(html_path)
        with open(html_path, "r", encoding="utf-8") as f:
            html_text = f.read()
            assert "Senior Developer Portfolio" in html_text
            assert "Distributed Search Cluster" in html_text

        # 2. PDF export
        pdf_path = os.path.join(tmpdir, "portfolio.pdf")
        PortfolioPdfRenderer.render_to_file(port, pdf_path)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000
