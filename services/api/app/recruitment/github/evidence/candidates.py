"""Skill and Project Candidate Generation with Human Review Queue (Stage 22)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.recruitment.github.contracts import (
    CandidateProject,
    CandidateSkill,
    CandidateStatus,
    RepositoryArchitecture,
    RepositoryMetadata,
    TechnologyFinding,
)
from app.recruitment.github.errors import CandidateNotFoundError
from app.recruitment.profile.contracts import (
    ClaimCategory,
    ProficiencyLevel,
    ProjectCategory,
    ProjectRecord,
    SkillCategory,
    SkillItem,
    VerificationStatus,
)
from app.recruitment.profile.service import get_profile_service

logger = logging.getLogger("autonom.recruitment.github.evidence.candidates")


class CandidateGenerator:
    """Generates candidate skills and projects from verified repository findings."""

    @classmethod
    def generate_skill_candidates(
        cls,
        repo: RepositoryMetadata,
        technologies: list[TechnologyFinding],
    ) -> list[CandidateSkill]:
        candidates: list[CandidateSkill] = []
        seen = set()

        for tech in technologies:
            c_name = tech.canonical_name.lower().strip()
            if c_name in seen:
                continue
            seen.add(c_name)

            candidate = CandidateSkill(
                repo_id=repo.id,
                repo_name=repo.name,
                name=tech.technology_name,
                canonical_name=c_name,
                category=tech.category.value,
                proficiency_estimate="intermediate",
                evidence_refs=[f"repo:{repo.full_name}", f"file:{tech.source_file}"],
                source_files=[tech.source_file],
                status=CandidateStatus.AWAITING_REVIEW,
            )
            candidates.append(candidate)

        return candidates

    @classmethod
    def generate_project_candidate(
        cls,
        repo: RepositoryMetadata,
        technologies: list[TechnologyFinding],
        architecture: Optional[RepositoryArchitecture] = None,
    ) -> CandidateProject:
        tech_names = sorted(list({t.technology_name for t in technologies}))[:8]
        desc = repo.description or (architecture.structure_summary if architecture else f"Software repository {repo.full_name}")

        return CandidateProject(
            repo_id=repo.id,
            title=repo.name.replace("-", " ").replace("_", " ").title(),
            description=desc,
            technologies=tech_names,
            suggested_contribution=f"Contributed to {repo.name} ({architecture.structure_summary if architecture else 'development'})",
            repo_url=repo.url,
            visibility=repo.visibility,
            evidence_refs=[f"repo:{repo.full_name}"],
            status=CandidateStatus.AWAITING_REVIEW,
        )


class CandidateReviewManager:
    """Manages the human-in-the-loop candidate review queue and promotion into Stage 21."""

    def __init__(self) -> None:
        self._skill_candidates: dict[str, CandidateSkill] = {}
        self._project_candidates: dict[str, CandidateProject] = {}

    def register_skills(self, skills: list[CandidateSkill]) -> None:
        for s in skills:
            self._skill_candidates[s.id] = s

    def register_project(self, project: CandidateProject) -> None:
        self._project_candidates[project.id] = project

    def list_skill_candidates(self, repo_id: Optional[str] = None) -> list[CandidateSkill]:
        skills = list(self._skill_candidates.values())
        if repo_id:
            skills = [s for s in skills if s.repo_id == repo_id]
        return skills

    def list_project_candidates(self, repo_id: Optional[str] = None) -> list[CandidateProject]:
        projects = list(self._project_candidates.values())
        if repo_id:
            projects = [p for p in projects if p.repo_id == repo_id]
        return projects

    def confirm_skill(
        self,
        candidate_id: str,
        profile_id: str = "prof_primary_applicant",
        modified_data: Optional[dict[str, Any]] = None,
    ) -> CandidateSkill:
        cand = self._skill_candidates.get(candidate_id)
        if not cand:
            raise CandidateNotFoundError(f"Skill candidate '{candidate_id}' not found.")

        # Apply any user modifications
        name = modified_data.get("name", cand.name) if modified_data else cand.name
        canonical = modified_data.get("canonical_name", cand.canonical_name) if modified_data else cand.canonical_name
        prof_str = modified_data.get("proficiency", "intermediate") if modified_data else "intermediate"

        # Promote to canonical Stage 21 profile
        profile_service = get_profile_service()
        skill_item = SkillItem(
            name=name,
            canonical_name=canonical,
            category=SkillCategory(cand.category) if cand.category in SkillCategory._value2member_map_ else SkillCategory.PROGRAMMING_LANGUAGES,
            proficiency=ProficiencyLevel(prof_str) if prof_str in ProficiencyLevel._value2member_map_ else ProficiencyLevel.INTERMEDIATE,
            evidence_refs=cand.evidence_refs,
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
        profile_service.add_or_update_skill(profile_id, skill_item)

        cand.status = CandidateStatus.CONFIRMED
        cand.confirmed_skill_id = skill_item.id
        logger.info(f"Confirmed skill '{cand.name}' promoted to profile '{profile_id}'.")
        return cand

    def confirm_project(
        self,
        candidate_id: str,
        profile_id: str = "prof_primary_applicant",
        modified_data: Optional[dict[str, Any]] = None,
    ) -> CandidateProject:
        cand = self._project_candidates.get(candidate_id)
        if not cand:
            raise CandidateNotFoundError(f"Project candidate '{candidate_id}' not found.")

        title = modified_data.get("title", cand.title) if modified_data else cand.title
        desc = modified_data.get("description", cand.description) if modified_data else cand.description
        techs = modified_data.get("technologies", cand.technologies) if modified_data else cand.technologies
        contrib = modified_data.get("suggested_contribution", cand.suggested_contribution) if modified_data else cand.suggested_contribution

        profile_service = get_profile_service()
        proj_item = ProjectRecord(
            title=title,
            description=desc,
            category=ProjectCategory.PERSONAL,
            technologies=techs,
            applicant_contribution=contrib,
            repo_url=cand.repo_url,
            evidence_refs=cand.evidence_refs,
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
        profile_service.add_project(profile_id, proj_data=proj_item)

        cand.status = CandidateStatus.CONFIRMED
        cand.confirmed_project_id = proj_item.id
        logger.info(f"Confirmed project '{cand.title}' promoted to profile '{profile_id}'.")
        return cand

    def reject_candidate(self, candidate_id: str) -> None:
        if candidate_id in self._skill_candidates:
            self._skill_candidates[candidate_id].status = CandidateStatus.REJECTED
        elif candidate_id in self._project_candidates:
            self._project_candidates[candidate_id].status = CandidateStatus.REJECTED
        else:
            raise CandidateNotFoundError(f"Candidate '{candidate_id}' not found.")
        logger.info(f"Candidate '{candidate_id}' rejected.")
