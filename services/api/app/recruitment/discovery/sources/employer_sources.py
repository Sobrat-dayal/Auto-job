"""Employer Career Source Registry (Stage 26).

Maintains verified employer career portals, associating employer identities with
their official career site origins, ATS board tokens, and connectivity state.
"""

from datetime import UTC, datetime
from typing import Optional
from urllib.parse import urlparse

from app.recruitment.discovery.contracts import (
    ConnectorId,
    EmployerCareerPageCreateRequest,
    EmployerCareerSource,
    SourceAccessStatus,
)
from app.recruitment.discovery.sources.ats_detection import detect_ats_from_url


class EmployerSourceManager:
    """In-memory and persistent manager for employer career sources."""

    def __init__(self) -> None:
        self._employers: dict[str, EmployerCareerSource] = {}
        self._seed_default_employers()

    def _seed_default_employers(self) -> None:
        default_seeds = [
            EmployerCareerSource(
                id="emp_stripe",
                employer_name="Stripe",
                career_url="https://boards.greenhouse.io/stripe",
                provider_type=ConnectorId.GREENHOUSE,
                board_token="stripe",
                approved_origin="boards.greenhouse.io",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
            ),
            EmployerCareerSource(
                id="emp_github",
                employer_name="GitHub",
                career_url="https://boards.greenhouse.io/github",
                provider_type=ConnectorId.GREENHOUSE,
                board_token="github",
                approved_origin="boards.greenhouse.io",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
            ),
            EmployerCareerSource(
                id="emp_netflix",
                employer_name="Netflix",
                career_url="https://jobs.lever.co/netflix",
                provider_type=ConnectorId.LEVER,
                board_token="netflix",
                approved_origin="jobs.lever.co",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
            ),
            EmployerCareerSource(
                id="emp_openai",
                employer_name="OpenAI",
                career_url="https://jobs.ashbyhq.com/openai",
                provider_type=ConnectorId.ASHBY,
                board_token="openai",
                approved_origin="jobs.ashbyhq.com",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
            ),
            EmployerCareerSource(
                id="emp_cloudflare",
                employer_name="Cloudflare",
                career_url="https://boards.greenhouse.io/cloudflare",
                provider_type=ConnectorId.GREENHOUSE,
                board_token="cloudflare",
                approved_origin="boards.greenhouse.io",
                access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
                is_enabled=True,
            ),
        ]
        for emp in default_seeds:
            self._employers[emp.id] = emp

    def list_employers(self, enabled_only: bool = False) -> list[EmployerCareerSource]:
        items = list(self._employers.values())
        if enabled_only:
            items = [e for e in items if e.is_enabled]
        return sorted(items, key=lambda x: x.employer_name.lower())

    def get_employer(self, employer_id: str) -> Optional[EmployerCareerSource]:
        return self._employers.get(employer_id)

    def find_by_name(self, employer_name: str) -> Optional[EmployerCareerSource]:
        clean_target = employer_name.strip().lower()
        for emp in self._employers.values():
            if emp.employer_name.strip().lower() == clean_target:
                return emp
        return None

    def add_employer(self, req: EmployerCareerPageCreateRequest) -> EmployerCareerSource:
        # Check existing
        existing = self.find_by_name(req.employer_name)
        if existing:
            return existing

        parsed = urlparse(req.career_url)
        origin = parsed.netloc.lower()
        detection = detect_ats_from_url(req.career_url)

        emp = EmployerCareerSource(
            employer_name=req.employer_name,
            career_url=req.career_url,
            provider_type=detection.detected_connector,
            board_token=detection.board_token,
            approved_origin=origin,
            access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
            is_enabled=True,
        )
        self._employers[emp.id] = emp
        return emp

    def delete_employer(self, employer_id: str) -> bool:
        if employer_id in self._employers:
            del self._employers[employer_id]
            return True
        return False


# Singleton instance
employer_source_manager = EmployerSourceManager()
