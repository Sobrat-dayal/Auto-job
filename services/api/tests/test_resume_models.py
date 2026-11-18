"""Unit tests for Stage 23 Resume Intelligence & Portfolio domain models and contracts."""

import pytest
from app.recruitment.resume.contracts import (
    ResumeDocument,
    ResumeSection,
    ResumeEntry,
    SourceFactReference,
    ResumeType,
    SectionType,
    DocumentStatus,
    PageFormat,
    ExportFormat,
    RequirementMatchCategory,
    ATSCheckStatus,
    ATSCheckResult,
    ATSReadabilityReport,
    ResumeVersionRecord,
    ExportArtifact,
    PortfolioDocument,
    PortfolioProjectEntry,
)


def test_resume_document_instantiation():
    fact = SourceFactReference(
        source_entity_id="exp_01",
        claim_id="clm_01",
        verification_status="verified",
        source_excerpt="Scaled backend services with Python",
    )

    entry = ResumeEntry(
        id="ent_01",
        title="Software Engineer",
        subtitle="Platform Team",
        organization="Acme Corp",
        location="San Francisco, CA",
        start_date="2022-01",
        end_date=None,
        is_current=True,
        description=None,
        bullet_points=[
            "Architected low-latency microservices serving 10k requests/sec",
            "Optimized SQL queries reducing p95 latency by 35%",
        ],
        tags=["Python", "FastAPI", "PostgreSQL"],
        source_refs=[fact],
    )

    section = ResumeSection(
        id="sec_exp",
        section_type=SectionType.EXPERIENCE,
        display_title="Work Experience",
        ordering=0,
        entries=[entry],
        custom_layout=None,
    )

    doc = ResumeDocument(
        id="res_01",
        owner_id="usr_01",
        profile_id="prof_01",
        profile_snapshot_id="snap_01",
        title="Senior Software Engineer Resume",
        resume_type=ResumeType.EXPERIENCED,
        target_role="Senior Software Engineer",
        job_ref=None,
        template_id="ats_classic",
        template_version="1.0.0",
        status=DocumentStatus.DRAFT,
        current_version=1,
        locale="en_US",
        page_format=PageFormat.LETTER,
        max_pages=1,
        header_contact={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1-555-0100",
            "location": "San Francisco, CA",
        },
        sections=[section],
    )

    assert doc.id == "res_01"
    assert doc.sections[0].display_title == "Work Experience"
    assert len(doc.sections[0].entries[0].bullet_points) == 2
    assert doc.sections[0].entries[0].source_refs[0].claim_id == "clm_01"


def test_ats_report_contracts():
    check1 = ATSCheckResult(
        check_name="Machine Readable Text",
        status=ATSCheckStatus.PASS,
        observed_evidence="Unicode selectable text stream found",
        impact_explanation="All text extractable by ATS parsers",
        suggested_remediation=None,
        location=None,
    )

    report = ATSReadabilityReport(
        overall_status=ATSCheckStatus.PASS,
        passed_count=1,
        warning_count=0,
        error_count=0,
        checks=[check1],
        document_id="res_01",
        format="ats_classic",
        notes="All structural properties compliant",
    )

    assert report.overall_status == ATSCheckStatus.PASS
    assert report.checks[0].status == ATSCheckStatus.PASS


def test_portfolio_document_contracts():
    project = PortfolioProjectEntry(
        project_id="proj_01",
        title="Distributed Queue",
        summary="High-availability async queue engine",
        problem_addressed="Throughput saturation on legacy broker",
        tech_stack=["Rust", "Python", "Docker"],
        architecture_highlights=["Zero-copy memory mapped ring buffer"],
        individual_contribution="Designed write-ahead log and snapshot replication",
        deliverables=["Production service", "Client SDK"],
        repo_url="https://github.com/janedoe/queue",
        demo_url=None,
        screenshot_path=None,
        attribution_level="creator",
        is_public_eligible=True,
        ordering=0,
    )

    port = PortfolioDocument(
        id="port_01",
        owner_id="usr_01",
        profile_id="prof_01",
        title="Software Architecture Portfolio",
        professional_intro="Systems engineer with focus on distributed consensus.",
        selected_skills=["Rust", "Python", "Distributed Systems"],
        selected_projects=[project],
        publications=[],
        certifications=[],
        public_contact={"email": "jane@example.com"},
        template_id="portfolio_classic",
        status=DocumentStatus.APPROVED,
    )

    assert port.id == "port_01"
    assert len(port.selected_projects) == 1
    assert port.selected_projects[0].attribution_level == "creator"
