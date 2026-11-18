"""Authoritative Applicant Profile REST API endpoints for Stage 21."""

from __future__ import annotations

import base64
import logging
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.core.security import AuthContext
from app.recruitment.profile.contracts import (
    ApplicantClaim,
    ApplicantProfile,
    CertificationRecord,
    ContactInfo,
    DataQualityReport,
    EducationRecord,
    EmploymentEligibility,
    EmploymentRecord,
    EvidenceMetadata,
    ImportJob,
    LocationInfo,
    ProfileConflict,
    ProfileSnapshot,
    ProfileVersionRecord,
    ProjectRecord,
    SkillItem,
)
from app.recruitment.profile.errors import (
    ClaimNotFoundError,
    ConcurrencyConflictError,
    ConflictResolutionError,
    EvidenceNotFoundError,
    ExtractionFailedError,
    ImportJobNotFoundError,
    InvalidDocumentError,
    ProfileNotFoundError,
    ProfilePermissionDeniedError,
)
from app.recruitment.profile.service import (
    ApplicantProfileService,
    get_profile_service,
)

logger = logging.getLogger("autonom.api.applicants")

router = APIRouter(prefix="/applicants", tags=["applicants"])


def _handle_domain_errors(func):
    """Decorator or helper pattern for consistent error handling."""
    pass


def _map_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, ProfileNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ProfilePermissionDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, (ClaimNotFoundError, EvidenceNotFoundError, ImportJobNotFoundError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConcurrencyConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, (InvalidDocumentError, ConflictResolutionError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, ExtractionFailedError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# Request Schemas
class CreateProfileRequest(BaseModel):
    display_label: str = Field(default="Primary Career Profile", description="Human-readable profile title")
    owner_id: Optional[str] = Field(default=None, description="Optional owner ID")


class UpdateProfileMetaRequest(BaseModel):
    display_label: str = Field(..., description="New display label for profile")
    expected_version: Optional[int] = Field(default=None, description="Optimistic locking version")


class UpdateIdentityRequest(BaseModel):
    contact: Optional[ContactInfo] = None
    location: Optional[LocationInfo] = None
    eligibility: Optional[EmploymentEligibility] = None
    expected_version: Optional[int] = None


class ClaimConfirmRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Optional user review notes")


class ClaimRejectRequest(BaseModel):
    reason: Optional[str] = Field(default=None, description="Reason for rejection")


class ConflictResolveRequest(BaseModel):
    resolution_choice: str = Field(..., description="Resolution strategy: keep_a, keep_b, manual, dismiss")
    chosen_claim_id: Optional[str] = Field(default=None, description="Chosen claim id if keep_a/keep_b")
    manual_value: Optional[Any] = Field(default=None, description="Explicit value if manual")
    rationale: Optional[str] = Field(default=None, description="Rationale for resolution")


class CandidateReviewRequest(BaseModel):
    action: str = Field(..., description="Review action: accept, reject, modify")
    modified_data: Optional[dict[str, Any]] = Field(default=None, description="Modified candidate payload if modify")
    notes: Optional[str] = Field(default=None, description="Optional reviewer notes")


class AgentSnapshotRequest(BaseModel):
    target_agent: str = Field(..., description="Downstream agent (e.g. JobMatchingAgent, ResumeAgent)")
    authorized_scopes: Optional[list[str]] = Field(default=None, description="Explicit scopes granted for snapshot")


class ImportUploadJsonRequest(BaseModel):
    filename: str = Field(..., description="File name of the resume/document")
    content_base64: Optional[str] = Field(default=None, description="Base64 encoded file content")
    raw_text: Optional[str] = Field(default=None, description="Direct text input if not base64")


# 1. Profile CRUD Endpoints
@router.get("", response_model=list[ApplicantProfile])
async def list_profiles(
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[ApplicantProfile]:
    """Lists applicant profiles owned by the authenticated context."""
    try:
        return service.list_profiles(auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("", response_model=ApplicantProfile, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: CreateProfileRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Creates a new applicant profile container."""
    try:
        return service.create_profile(
            display_label=body.display_label,
            owner_id=body.owner_id,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/{profile_id}", response_model=ApplicantProfile)
async def get_profile(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Retrieves full authoritative applicant profile."""
    try:
        return service.get_profile(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.patch("/{profile_id}", response_model=ApplicantProfile)
async def update_profile_meta(
    profile_id: str,
    body: UpdateProfileMetaRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Updates metadata/label of an applicant profile."""
    try:
        return service.update_profile_meta(
            profile_id=profile_id,
            display_label=body.display_label,
            expected_version=body.expected_version,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> dict[str, Any]:
    """Deletes an applicant profile and associated local records."""
    try:
        service.delete_profile(profile_id=profile_id, auth=auth)
        return {"status": "deleted", "profile_id": profile_id}
    except Exception as exc:
        raise _map_exception(exc) from exc


# 2. Identity & Contact
@router.get("/{profile_id}/identity")
async def get_identity(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> dict[str, Any]:
    """Retrieves contact, location, and employment eligibility."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return {
            "profile_id": prof.id,
            "version": prof.version,
            "contact": prof.contact.model_dump() if prof.contact else None,
            "location": prof.location.model_dump() if prof.location else None,
            "eligibility": prof.eligibility.model_dump() if prof.eligibility else None,
        }
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.patch("/{profile_id}/identity", response_model=ApplicantProfile)
async def update_identity(
    profile_id: str,
    body: UpdateIdentityRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Updates contact info, address/location, and work authorization."""
    try:
        return service.update_identity(
            profile_id=profile_id,
            contact=body.contact,
            location=body.location,
            eligibility=body.eligibility,
            expected_version=body.expected_version,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


# 3. Education
@router.get("/{profile_id}/education", response_model=list[EducationRecord])
async def list_education(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[EducationRecord]:
    """Lists all education records for profile."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return prof.education
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/education", response_model=ApplicantProfile, status_code=status.HTTP_201_CREATED)
async def add_education(
    profile_id: str,
    body: EducationRecord,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Adds a verified education record to the applicant profile."""
    try:
        return service.add_education(profile_id=profile_id, edu_data=body, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.patch("/{profile_id}/education/{education_id}", response_model=ApplicantProfile)
async def update_education(
    profile_id: str,
    education_id: str,
    body: EducationRecord,
    auth: AuthDep,
    expected_version: Optional[int] = Query(default=None),
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Updates an existing education record."""
    try:
        return service.update_education(
            profile_id=profile_id,
            education_id=education_id,
            edu_data=body,
            expected_version=expected_version,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/education/{education_id}", response_model=ApplicantProfile)
async def delete_education(
    profile_id: str,
    education_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Removes an education record from the profile."""
    try:
        return service.delete_education(profile_id=profile_id, education_id=education_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


# 4. Employment Experience
@router.get("/{profile_id}/experience", response_model=list[EmploymentRecord])
async def list_experience(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[EmploymentRecord]:
    """Lists all employment experience records."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return prof.employment
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/experience", response_model=ApplicantProfile, status_code=status.HTTP_201_CREATED)
async def add_experience(
    profile_id: str,
    body: EmploymentRecord,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Adds a new employment record."""
    try:
        return service.add_employment(profile_id=profile_id, emp_data=body, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.patch("/{profile_id}/experience/{experience_id}", response_model=ApplicantProfile)
async def update_experience(
    profile_id: str,
    experience_id: str,
    body: EmploymentRecord,
    auth: AuthDep,
    expected_version: Optional[int] = Query(default=None),
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Updates an existing employment record."""
    try:
        return service.update_employment(
            profile_id=profile_id,
            employment_id=experience_id,
            emp_data=body,
            expected_version=expected_version,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/experience/{experience_id}", response_model=ApplicantProfile)
async def delete_experience(
    profile_id: str,
    experience_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Removes an employment record."""
    try:
        return service.delete_employment(profile_id=profile_id, employment_id=experience_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


# 5. Skills
@router.get("/{profile_id}/skills", response_model=list[SkillItem])
async def list_skills(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[SkillItem]:
    """Lists all skills associated with the applicant profile."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return prof.skills
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/skills", response_model=ApplicantProfile)
async def add_or_update_skill(
    profile_id: str,
    body: SkillItem,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Adds or updates a skill in the profile."""
    try:
        return service.add_or_update_skill(profile_id=profile_id, skill_data=body, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/skills/{skill_id}", response_model=ApplicantProfile)
async def delete_skill(
    profile_id: str,
    skill_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Removes a skill from the profile."""
    try:
        return service.delete_skill(profile_id=profile_id, skill_id=skill_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


# 6. Projects
@router.get("/{profile_id}/projects", response_model=list[ProjectRecord])
async def list_projects(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[ProjectRecord]:
    """Lists all technical and professional projects."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return prof.projects
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/projects", response_model=ApplicantProfile, status_code=status.HTTP_201_CREATED)
async def add_project(
    profile_id: str,
    body: ProjectRecord,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Adds a project record."""
    try:
        return service.add_project(profile_id=profile_id, proj_data=body, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/projects/{project_id}", response_model=ApplicantProfile)
async def delete_project(
    profile_id: str,
    project_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Removes a project record."""
    try:
        return service.delete_project(profile_id=profile_id, project_id=project_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


# 7. Certifications
@router.get("/{profile_id}/certifications", response_model=list[CertificationRecord])
async def list_certifications(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[CertificationRecord]:
    """Lists professional certifications."""
    try:
        prof = service.get_profile(profile_id=profile_id, auth=auth)
        return prof.certifications
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/certifications", response_model=ApplicantProfile, status_code=status.HTTP_201_CREATED)
async def add_certification(
    profile_id: str,
    body: CertificationRecord,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Adds a certification record."""
    try:
        return service.add_certification(profile_id=profile_id, cert_data=body, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/certifications/{cert_id}", response_model=ApplicantProfile)
async def delete_certification(
    profile_id: str,
    cert_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantProfile:
    """Removes a certification record."""
    try:
        return service.delete_certification(profile_id=profile_id, cert_id=cert_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


# 8. Claims & Verification
@router.get("/{profile_id}/claims", response_model=list[ApplicantClaim])
async def list_claims(
    profile_id: str,
    auth: AuthDep,
    category: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[ApplicantClaim]:
    """Lists granular provenance claims for the profile."""
    try:
        return service.list_claims(
            profile_id=profile_id,
            category=category,
            status=status_filter,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/claims/{claim_id}/confirm", response_model=ApplicantClaim)
async def confirm_claim(
    profile_id: str,
    claim_id: str,
    body: ClaimConfirmRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantClaim:
    """Explicitly confirms an unverified claim, transitioning to UserConfirmed."""
    try:
        return service.confirm_claim(
            profile_id=profile_id,
            claim_id=claim_id,
            notes=body.notes,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/claims/{claim_id}/reject", response_model=ApplicantClaim)
async def reject_claim(
    profile_id: str,
    claim_id: str,
    body: ClaimRejectRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ApplicantClaim:
    """Rejects an unverified claim, transitioning to Rejected."""
    try:
        return service.reject_claim(
            profile_id=profile_id,
            claim_id=claim_id,
            reason=body.reason,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


# 9. Conflicts
@router.get("/{profile_id}/conflicts", response_model=list[ProfileConflict])
async def list_conflicts(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[ProfileConflict]:
    """Lists detected data conflicts across evidence and user inputs."""
    try:
        return service.list_conflicts(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/conflicts/{conflict_id}/resolve", response_model=ProfileConflict)
async def resolve_conflict(
    profile_id: str,
    conflict_id: str,
    body: ConflictResolveRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ProfileConflict:
    """Resolves a detected conflict using user-authorized resolution policy."""
    try:
        return service.resolve_conflict(
            profile_id=profile_id,
            conflict_id=conflict_id,
            resolution_choice=body.resolution_choice,
            chosen_claim_id=body.chosen_claim_id,
            manual_value=body.manual_value,
            rationale=body.rationale,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


# 10. Evidence Library
@router.get("/{profile_id}/evidence", response_model=list[EvidenceMetadata])
async def list_evidence(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[EvidenceMetadata]:
    """Lists uploaded evidence files supporting profile claims."""
    try:
        return service.list_evidence(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/evidence", response_model=EvidenceMetadata, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    profile_id: str,
    auth: AuthDep,
    file: UploadFile = File(...),
    document_type: str = Form(default="resume"),
    tags: str = Form(default=""),
    service: ApplicantProfileService = Depends(get_profile_service),
) -> EvidenceMetadata:
    """Uploads and digests an evidence document, computing SHA-256 and indexing metadata."""
    try:
        content = await file.read()
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        return service.store_evidence(
            profile_id=profile_id,
            filename=file.filename or "evidence.pdf",
            file_bytes=content,
            document_type=document_type,
            tags=tag_list,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.delete("/{profile_id}/evidence/{evidence_id}", status_code=status.HTTP_200_OK)
async def delete_evidence(
    profile_id: str,
    evidence_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> dict[str, Any]:
    """Deletes an evidence file and disassociates linked claims."""
    try:
        service.delete_evidence(profile_id=profile_id, evidence_id=evidence_id, auth=auth)
        return {"status": "deleted", "evidence_id": evidence_id}
    except Exception as exc:
        raise _map_exception(exc) from exc


# 11. Import Pipeline & Review Queue
@router.post("/{profile_id}/imports", response_model=ImportJob, status_code=status.HTTP_202_ACCEPTED)
async def create_import(
    profile_id: str,
    auth: AuthDep,
    file: Optional[UploadFile] = File(default=None),
    json_req: Optional[ImportUploadJsonRequest] = None,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ImportJob:
    """Initiates an asynchronous/staged document parse and candidate extraction job."""
    try:
        filename = "document.txt"
        file_bytes = b""
        if file is not None:
            filename = file.filename or "document.txt"
            file_bytes = await file.read()
        elif json_req is not None:
            filename = json_req.filename
            if json_req.content_base64:
                file_bytes = base64.b64decode(json_req.content_base64)
            elif json_req.raw_text:
                file_bytes = json_req.raw_text.encode("utf-8")
        else:
            raise InvalidDocumentError("Either a multipart file or JSON import payload must be provided.")

        return service.create_import_job(
            profile_id=profile_id,
            filename=filename,
            file_bytes=file_bytes,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/{profile_id}/imports/{import_id}", response_model=ImportJob)
async def get_import_job(
    profile_id: str,
    import_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ImportJob:
    """Retrieves import job extraction candidates and progress status."""
    try:
        return service.get_import_job(profile_id=profile_id, import_id=import_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/imports/{import_id}/candidates/{candidate_id}/review")
async def review_candidate(
    profile_id: str,
    import_id: str,
    candidate_id: str,
    body: CandidateReviewRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> dict[str, Any]:
    """Human-in-the-loop review of an extracted claim candidate: accept, reject, or modify."""
    try:
        cand, claim = service.review_candidate(
            profile_id=profile_id,
            import_id=import_id,
            candidate_id=candidate_id,
            action=body.action,
            modified_data=body.modified_data,
            notes=body.notes,
            auth=auth,
        )
        return {
            "status": "reviewed",
            "action": body.action,
            "candidate": cand.model_dump(),
            "claim": claim.model_dump() if claim else None,
        }
    except Exception as exc:
        raise _map_exception(exc) from exc


# 12. Quality, Snapshots, Versions, and Export
@router.get("/{profile_id}/quality", response_model=DataQualityReport)
async def get_quality(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> DataQualityReport:
    """Runs deterministic data quality, completeness, and recruitment readiness evaluation."""
    try:
        return service.evaluate_quality(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/snapshot", response_model=ProfileSnapshot)
async def generate_agent_snapshot(
    profile_id: str,
    body: AgentSnapshotRequest,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> ProfileSnapshot:
    """Generates a scoped, redaction-safe snapshot of the profile tailored for a downstream agent."""
    try:
        return service.generate_agent_snapshot(
            profile_id=profile_id,
            target_agent=body.target_agent,
            authorized_scopes=body.authorized_scopes,
            auth=auth,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/{profile_id}/export")
async def export_profile(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> dict[str, Any]:
    """Exports full verifiable profile, claim registry, and quality metrics as portable JSON."""
    try:
        return service.export_profile(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/{profile_id}/versions", response_model=list[ProfileVersionRecord])
async def get_version_history(
    profile_id: str,
    auth: AuthDep,
    service: ApplicantProfileService = Depends(get_profile_service),
) -> list[ProfileVersionRecord]:
    """Retrieves immutable audit history and version records."""
    try:
        return service.get_version_history(profile_id=profile_id, auth=auth)
    except Exception as exc:
        raise _map_exception(exc) from exc

