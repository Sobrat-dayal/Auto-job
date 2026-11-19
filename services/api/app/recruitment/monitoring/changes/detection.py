"""Change detection engine comparing source observations and canonical listings."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional
from app.recruitment.monitoring.changes.semantic import is_material_description_change
from app.recruitment.monitoring.contracts import JobChangeType


class DetectedChange:
    def __init__(
        self,
        change_type: JobChangeType,
        field_name: str,
        is_material: bool,
        previous_value: Any,
        current_value: Any,
    ) -> None:
        self.change_type = change_type
        self.field_name = field_name
        self.is_material = is_material
        self.previous_value = previous_value
        self.current_value = current_value


def detect_job_changes(
    old_job: Optional[dict[str, Any]],
    new_data: dict[str, Any],
) -> list[DetectedChange]:
    """Compares existing job listing data against newly discovered/refreshed data."""
    changes: list[DetectedChange] = []

    if not old_job:
        # Brand new vacancy
        changes.append(
            DetectedChange(
                change_type=JobChangeType.NEW_VACANCY,
                field_name="id",
                is_material=True,
                previous_value=None,
                current_value=new_data.get("id") or new_data.get("external_id"),
            )
        )
        return changes

    # 1. Status change (Closed / Reopened)
    old_status = (old_job.get("status") or "active").lower()
    new_status = (new_data.get("status") or "active").lower()
    if old_status != new_status:
        if new_status in ("closed", "expired", "removed"):
            changes.append(
                DetectedChange(
                    change_type=JobChangeType.JOB_CLOSED,
                    field_name="status",
                    is_material=True,
                    previous_value=old_status,
                    current_value=new_status,
                )
            )
        elif old_status in ("closed", "expired", "removed") and new_status == "active":
            changes.append(
                DetectedChange(
                    change_type=JobChangeType.JOB_REOPENED,
                    field_name="status",
                    is_material=True,
                    previous_value=old_status,
                    current_value=new_status,
                )
            )

    # 2. Description change
    old_desc = old_job.get("description") or ""
    new_desc = new_data.get("description") or ""
    if old_desc != new_desc:
        material = is_material_description_change(old_desc, new_desc)
        changes.append(
            DetectedChange(
                change_type=JobChangeType.DESCRIPTION_UPDATED,
                field_name="description",
                is_material=material,
                previous_value=old_desc[:100] if old_desc else None,
                current_value=new_desc[:100] if new_desc else None,
            )
        )

    # 3. Salary change
    old_salary = old_job.get("salary_range")
    new_salary = new_data.get("salary_range")
    if old_salary != new_salary:
        changes.append(
            DetectedChange(
                change_type=JobChangeType.SALARY_CHANGED,
                field_name="salary_range",
                is_material=True,
                previous_value=old_salary,
                current_value=new_salary,
            )
        )

    # 4. Location change
    old_loc = old_job.get("location")
    new_loc = new_data.get("location")
    if old_loc != new_loc:
        changes.append(
            DetectedChange(
                change_type=JobChangeType.LOCATION_CHANGED,
                field_name="location",
                is_material=True,
                previous_value=old_loc,
                current_value=new_loc,
            )
        )

    # 5. Remote / Work Arrangement change
    old_remote = old_job.get("work_arrangement")
    new_remote = new_data.get("work_arrangement")
    if old_remote != new_remote:
        changes.append(
            DetectedChange(
                change_type=JobChangeType.REMOTE_CONDITIONS_CHANGED,
                field_name="work_arrangement",
                is_material=True,
                previous_value=old_remote,
                current_value=new_remote,
            )
        )

    # 6. Application URL change
    old_url = old_job.get("application_url")
    new_url = new_data.get("application_url")
    if old_url and new_url and old_url != new_url:
        changes.append(
            DetectedChange(
                change_type=JobChangeType.APPLICATION_URL_CHANGED,
                field_name="application_url",
                is_material=True,
                previous_value=old_url,
                current_value=new_url,
            )
        )

    return changes
