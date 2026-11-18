"""Autonomy Modes, Standing Grants Integration, and Review Queue Controller (Stage 25)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4
from app.recruitment.policy.contracts import (
    AutonomyMode,
    ReviewQueueItem,
    ReviewTrigger,
    StandingGrantRecord,
)
from app.recruitment.policy.errors import StandingGrantRevokedError


class AutonomyController:
    """Manages autonomy modes, Stage 14 standing grants integration, and human review queue."""

    def __init__(self) -> None:
        self._grants: dict[str, StandingGrantRecord] = {}
        self._review_queue: dict[str, ReviewQueueItem] = {}

    def get_grants(self) -> list[StandingGrantRecord]:
        return list(self._grants.values())

    def get_grant(self, grant_id: str) -> Optional[StandingGrantRecord]:
        return self._grants.get(grant_id)

    def create_grant(
        self,
        grantee_agent: str,
        action_type: str = "recruitment.application.prepare",
        target_employers: Optional[list[str]] = None,
        target_platforms: Optional[list[str]] = None,
        max_operations: int = 50,
        validity_days: int = 30,
    ) -> StandingGrantRecord:
        grant_id = f"grant_{uuid4().hex[:8]}"
        expires_at = datetime.now(UTC).replace(microsecond=0)
        from datetime import timedelta
        expires_at += timedelta(days=validity_days)

        rec = StandingGrantRecord(
            id=grant_id,
            grantee_agent=grantee_agent,
            action_type=action_type,
            target_employers=target_employers or [],
            target_platforms=target_platforms or [],
            max_operations=max_operations,
            operations_used=0,
            is_revoked=False,
            expires_at=expires_at,
        )
        self._grants[grant_id] = rec
        return rec

    def revoke_grant(self, grant_id: str) -> bool:
        grant = self._grants.get(grant_id)
        if not grant:
            return False
        grant.is_revoked = True
        return True

    def validate_action_authorization(
        self,
        mode: AutonomyMode,
        action: str,
        grant_id: Optional[str] = None,
        employer: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Evaluates whether an action is authorized under the active autonomy mode and grant.

        Returns:
            (is_authorized, reason)
        """
        # Mode 1: Research Only
        if mode == AutonomyMode.RESEARCH_ONLY:
            if action in ("discover", "read_job_description", "analyze_requirements"):
                return True, "Research actions permitted under Research Only mode."
            return False, f"Action '{action}' is prohibited under Research Only mode."

        # Mode 2: Prepare and Review
        if mode == AutonomyMode.PREPARE_AND_REVIEW:
            if action in ("discover", "read_job_description", "analyze_requirements", "prepare_resume_draft", "prepare_answer_draft"):
                return True, "Draft preparation permitted; human approval required prior to external action."
            if action == "submit_application":
                return False, "Direct autonomous submission prohibited under Prepare and Review mode."

        # Mode 3: Preauthorized Preparation
        if mode == AutonomyMode.PREAUTHORIZED_PREPARATION:
            if action.startswith("prepare_"):
                return True, "Preauthorized material preparation permitted."
            if action == "submit_application":
                return False, "Submission requires explicit human review and approval."

        # Mode 4: Bounded Autonomous Applications (Future Stage Contract Check)
        if mode == AutonomyMode.BOUNDED_AUTONOMOUS_APPLICATIONS:
            if not grant_id:
                return False, "Autonomous application action requires a valid standing grant reference."

            grant = self._grants.get(grant_id)
            if not grant:
                return False, f"Standing grant '{grant_id}' does not exist."
            if grant.is_revoked:
                return False, f"Standing grant '{grant_id}' has been revoked."
            if datetime.now(UTC) > grant.expires_at:
                return False, f"Standing grant '{grant_id}' has expired."
            if grant.operations_used >= grant.max_operations:
                return False, f"Standing grant '{grant_id}' usage limit exhausted ({grant.operations_used}/{grant.max_operations})."

            # Check employer scope if restricted in grant
            if grant.target_employers and employer:
                if employer.lower() not in [e.lower() for e in grant.target_employers]:
                    return False, f"Employer '{employer}' is outside the authorized scope of grant '{grant_id}'."

            # Check platform scope if restricted in grant
            if grant.target_platforms and platform:
                if platform.lower() not in [p.lower() for p in grant.target_platforms]:
                    return False, f"Platform '{platform}' is outside the authorized scope of grant '{grant_id}'."

            # Note: In Stage 25, no actual submission execution occurs; this provides the verified policy contract!
            return True, f"Action authorized under standing grant '{grant_id}' (Mode: Bounded Autonomous Applications)."

        return False, f"Action '{action}' not recognized or authorized."

    # Review Queue Operations
    def add_to_review_queue(
        self,
        job_id: str,
        job_title: str,
        employer: str,
        trigger: ReviewTrigger,
        reason: str,
        is_mandatory: bool = True,
    ) -> ReviewQueueItem:
        item_id = f"rev_{uuid4().hex[:8]}"
        item = ReviewQueueItem(
            id=item_id,
            job_id=job_id,
            job_title=job_title,
            employer=employer,
            trigger=trigger,
            reason=reason,
            is_mandatory=is_mandatory,
            status="pending",
        )
        self._review_queue[item_id] = item
        return item

    def get_review_queue(self, status: Optional[str] = None) -> list[ReviewQueueItem]:
        if status:
            return [i for i in self._review_queue.values() if i.status == status]
        return list(self._review_queue.values())

    def resolve_review_item(self, item_id: str, status: str, notes: Optional[str] = None) -> Optional[ReviewQueueItem]:
        item = self._review_queue.get(item_id)
        if not item:
            return None
        item.status = status
        item.resolved_at = datetime.now(UTC)
        item.resolution_notes = notes
        return item
