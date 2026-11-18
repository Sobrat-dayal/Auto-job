"""FastAPI REST API Endpoints for Resume Intelligence & Portfolios (Stage 23)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.api.dependencies import AuthDep
from app.recruitment.resume.contracts import (
    ATSReadabilityReport,
    ExportArtifact,
    JobDescriptionParseRequest,
    JobDescriptionSnapshot,
    PortfolioCreateRequest,
    PortfolioDocument,
    PortfolioUpdateRequest,
    RequirementEvidenceMapping,
    ResumeCreateRequest,
    ResumeDocument,
    ResumeExportRequest,
    ResumeTailorRequest,
    ResumeTemplateDefinition,
    ResumeUpdateRequest,
    ResumeVersionRecord,
)
from app.recruitment.resume.errors import (
    JobDescriptionNotFoundError,
    PortfolioNotFoundError,
    ResumeNotFoundError,
    ResumeValidationError,
    ResumeVersionNotFoundError,
    TemplateNotFoundError,
)
from app.recruitment.resume.service import get_resume_service
from app.recruitment.resume.templates.registry import ResumeTemplateRegistry

logger = logging.getLogger("autonom.api.resumes")

router = APIRouter(tags=["resumes"])


# =============================================================================
# 1. Resume Document Endpoints
# =============================================================================

@router.get("/resumes", response_model=list[ResumeDocument])
async def list_resumes(
    auth: AuthDep,
    resume_type: Optional[str] = Query(None, description="Filter by resume type"),
) -> list[ResumeDocument]:
    svc = get_resume_service()
    resumes = svc.list_resumes(owner_id=auth.client_id)
    if resume_type:
        resumes = [r for r in resumes if r.resume_type.value == resume_type]
    return resumes


@router.post("/resumes", response_model=ResumeDocument, status_code=status.HTTP_201_CREATED)
async def create_resume(
    auth: AuthDep,
    req: ResumeCreateRequest,
) -> ResumeDocument:
    svc = get_resume_service()
    try:
        return await svc.create_resume(req, auth=auth)
    except Exception as exc:
        logger.error(f"Failed to create resume: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/resumes/overview")
async def get_resumes_overview(auth: AuthDep) -> dict[str, Any]:
    svc = get_resume_service()
    all_resumes = svc.list_resumes(owner_id=auth.client_id)
    master = next((r for r in all_resumes if r.resume_type.value == "master"), None)
    return {
        "total_resumes": len(all_resumes),
        "draft_count": sum(1 for r in all_resumes if r.status.value == "draft"),
        "approved_count": sum(1 for r in all_resumes if r.status.value == "approved"),
        "master_resume_id": master.id if master else None,
        "master_resume_title": master.title if master else None,
        "recent_resumes": [
            {"id": r.id, "title": r.title, "type": r.resume_type.value, "status": r.status.value, "updated_at": r.updated_at.isoformat()}
            for r in sorted(all_resumes, key=lambda x: x.updated_at, reverse=True)[:5]
        ],
    }


@router.get("/resumes/{resume_id}", response_model=ResumeDocument)
async def get_resume(
    resume_id: str,
    auth: AuthDep,
) -> ResumeDocument:
    svc = get_resume_service()
    try:
        return svc.get_resume(resume_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/resumes/{resume_id}", response_model=ResumeDocument)
async def update_resume(
    resume_id: str,
    auth: AuthDep,
    req: ResumeUpdateRequest,
) -> ResumeDocument:
    svc = get_resume_service()
    try:
        return svc.update_resume(resume_id, req)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: str,
    auth: AuthDep,
) -> dict[str, bool]:
    svc = get_resume_service()
    try:
        success = svc.delete_resume(resume_id)
        return {"deleted": success}
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/resumes/{resume_id}/duplicate", response_model=ResumeDocument)
async def duplicate_resume(
    resume_id: str,
    auth: AuthDep,
    new_title: Optional[str] = Query(None),
) -> ResumeDocument:
    svc = get_resume_service()
    try:
        return svc.duplicate_resume(resume_id, new_title=new_title)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 2. Tailoring & Requirements
# =============================================================================

@router.post("/resumes/{resume_id}/tailor")
async def tailor_resume(
    resume_id: str,
    auth: AuthDep,
    req: ResumeTailorRequest,
) -> dict[str, Any]:
    svc = get_resume_service()
    try:
        doc, mappings = await svc.tailor_resume(req)
        return {
            "resume": doc,
            "evidence_mappings": mappings,
            "matched_count": sum(1 for m in mappings if m.match_category.value in ("directly_supported", "partially_supported")),
            "missing_count": sum(1 for m in mappings if m.match_category.value == "not_evidenced"),
        }
    except (ResumeNotFoundError, JobDescriptionNotFoundError, ResumeValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


# =============================================================================
# 3. Validation & ATS Audit
# =============================================================================

@router.get("/resumes/{resume_id}/validation")
async def get_validation_report(
    resume_id: str,
    auth: AuthDep,
) -> dict[str, Any]:
    svc = get_resume_service()
    try:
        issues = svc.validate_factual_claims(resume_id)
        return {
            "resume_id": resume_id,
            "issue_count": len(issues),
            "issues": issues,
            "is_valid": len([i for i in issues if i["severity"] == "error"]) == 0,
        }
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/resumes/{resume_id}/ats-report", response_model=ATSReadabilityReport)
async def get_ats_report(
    resume_id: str,
    auth: AuthDep,
) -> ATSReadabilityReport:
    svc = get_resume_service()
    try:
        return svc.evaluate_ats_readability(resume_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 4. Preview & Approval
# =============================================================================

@router.get("/resumes/{resume_id}/preview")
async def get_resume_preview(
    resume_id: str,
    auth: AuthDep,
) -> dict[str, str]:
    svc = get_resume_service()
    try:
        html = svc.generate_preview(resume_id)
        return {"resume_id": resume_id, "html": html}
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/resumes/{resume_id}/approve", response_model=ResumeVersionRecord)
async def approve_resume(
    resume_id: str,
    auth: AuthDep,
) -> ResumeVersionRecord:
    svc = get_resume_service()
    try:
        return svc.approve_resume(resume_id, actor_id=auth.client_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 5. Versions
# =============================================================================

@router.get("/resumes/{resume_id}/versions", response_model=list[ResumeVersionRecord])
async def list_resume_versions(
    resume_id: str,
    auth: AuthDep,
) -> list[ResumeVersionRecord]:
    svc = get_resume_service()
    svc.get_resume(resume_id)
    return svc.version_mgr.list_versions(resume_id)


@router.get("/resumes/{resume_id}/versions/{version_id}", response_model=ResumeVersionRecord)
async def get_resume_version(
    resume_id: str,
    version_id: str,
    auth: AuthDep,
) -> ResumeVersionRecord:
    svc = get_resume_service()
    svc.get_resume(resume_id)
    try:
        return svc.version_mgr.get_version(resume_id, version_id)
    except ResumeVersionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 6. Export Manager
# =============================================================================

@router.post("/resumes/{resume_id}/export", response_model=ExportArtifact)
async def export_resume(
    resume_id: str,
    auth: AuthDep,
    req: ResumeExportRequest,
) -> ExportArtifact:
    svc = get_resume_service()
    try:
        return svc.export_resume(resume_id, req)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Failed to export resume {resume_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/resumes/{resume_id}/exports", response_model=list[ExportArtifact])
async def list_resume_exports(
    resume_id: str,
    auth: AuthDep,
) -> list[ExportArtifact]:
    svc = get_resume_service()
    svc.get_resume(resume_id)
    return svc.export_mgr.list_exports(resume_id)


# =============================================================================
# 7. Resume Templates
# =============================================================================

@router.get("/resume-templates", response_model=list[ResumeTemplateDefinition])
async def list_templates(auth: AuthDep) -> list[ResumeTemplateDefinition]:
    return ResumeTemplateRegistry.list_templates()


@router.get("/resume-templates/{template_id}", response_model=ResumeTemplateDefinition)
async def get_template(
    template_id: str,
    auth: AuthDep,
) -> ResumeTemplateDefinition:
    try:
        return ResumeTemplateRegistry.get_template(template_id)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 8. Job Descriptions
# =============================================================================

@router.post("/job-descriptions/analyze", response_model=JobDescriptionSnapshot)
async def analyze_job_description(
    auth: AuthDep,
    req: JobDescriptionParseRequest,
) -> JobDescriptionSnapshot:
    svc = get_resume_service()
    return svc.parse_job_description(req)


@router.get("/job-descriptions/{job_id}", response_model=JobDescriptionSnapshot)
async def get_job_description(
    job_id: str,
    auth: AuthDep,
) -> JobDescriptionSnapshot:
    svc = get_resume_service()
    try:
        return svc.get_job_snapshot(job_id)
    except JobDescriptionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# =============================================================================
# 9. Portfolio Endpoints
# =============================================================================

@router.get("/portfolios", response_model=list[PortfolioDocument])
async def list_portfolios(auth: AuthDep) -> list[PortfolioDocument]:
    svc = get_resume_service()
    return svc.portfolio_svc.list_portfolios(owner_id=auth.client_id)


@router.post("/portfolios", response_model=PortfolioDocument, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    auth: AuthDep,
    req: PortfolioCreateRequest,
) -> PortfolioDocument:
    svc = get_resume_service()
    return svc.portfolio_svc.create_portfolio(req, owner_id=auth.client_id)


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioDocument)
async def get_portfolio(
    portfolio_id: str,
    auth: AuthDep,
) -> PortfolioDocument:
    svc = get_resume_service()
    try:
        return svc.portfolio_svc.get_portfolio(portfolio_id)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/portfolios/{portfolio_id}", response_model=PortfolioDocument)
async def update_portfolio(
    portfolio_id: str,
    auth: AuthDep,
    req: PortfolioUpdateRequest,
) -> PortfolioDocument:
    svc = get_resume_service()
    try:
        return svc.portfolio_svc.update_portfolio(portfolio_id, req)
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/portfolios/{portfolio_id}/export/pdf")
async def export_portfolio_pdf(
    portfolio_id: str,
    auth: AuthDep,
) -> dict[str, str]:
    svc = get_resume_service()
    try:
        path = svc.portfolio_svc.export_portfolio_pdf(portfolio_id)
        return {"portfolio_id": portfolio_id, "file_path": path, "format": "pdf"}
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Failed to export portfolio PDF {portfolio_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/portfolios/{portfolio_id}/export/html")
async def export_portfolio_html(
    portfolio_id: str,
    auth: AuthDep,
) -> dict[str, str]:
    svc = get_resume_service()
    try:
        path = svc.portfolio_svc.export_portfolio_html(portfolio_id)
        return {"portfolio_id": portfolio_id, "file_path": path, "format": "html"}
    except PortfolioNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Failed to export portfolio HTML {portfolio_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
