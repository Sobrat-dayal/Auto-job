"""Deterministic Years-of-Experience Duration Calculator (Stage 24)."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Optional
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    EmploymentRecord,
    EmploymentType,
)

logger = logging.getLogger("autonom.recruitment.writing.answers.experience_calc")


class ExperienceCalculator:
    """Calculates non-overlapping years of experience across distinct professional categories."""

    @classmethod
    def calculate_experience_breakdown(
        cls,
        profile: ApplicantProfile,
    ) -> dict[str, float]:
        """Calculates years of experience separated into:
        - professional_employment (full-time, part-time, contract)
        - internship
        - freelance
        - total_work_experience
        """
        now_year = datetime.now(UTC).year
        now_month = datetime.now(UTC).month

        prof_intervals: list[tuple[float, float]] = []
        intern_intervals: list[tuple[float, float]] = []
        freelance_intervals: list[tuple[float, float]] = []

        for exp in profile.experience:
            start_f = cls._parse_date_to_float(exp.start_date, default_year=now_year)
            if start_f is None:
                continue

            if exp.is_current or not exp.end_date:
                end_f = now_year + (now_month / 12.0)
            else:
                end_f = cls._parse_date_to_float(exp.end_date, default_year=now_year) or (now_year + now_month / 12.0)

            if end_f < start_f:
                end_f = start_f

            emp_type = getattr(exp, "employment_type", None)
            emp_val = emp_type.value if hasattr(emp_type, "value") else str(emp_type).lower()

            if emp_val in ("internship", "coop", "co-op"):
                intern_intervals.append((start_f, end_f))
            elif emp_val in ("freelance", "contractor", "self_employed"):
                freelance_intervals.append((start_f, end_f))
            else:
                prof_intervals.append((start_f, end_f))

        prof_years = cls._merge_intervals_duration(prof_intervals)
        intern_years = cls._merge_intervals_duration(intern_intervals)
        freelance_years = cls._merge_intervals_duration(freelance_intervals)

        all_intervals = prof_intervals + intern_intervals + freelance_intervals
        total_years = cls._merge_intervals_duration(all_intervals)

        return {
            "professional_employment": round(prof_years, 1),
            "internship": round(intern_years, 1),
            "freelance": round(freelance_years, 1),
            "total_work_experience": round(total_years, 1),
        }

    @classmethod
    def get_technology_experience_years(
        cls,
        profile: ApplicantProfile,
        technology: str,
    ) -> float:
        """Calculates years of verified experience for a specific technology keyword."""
        tech_lower = technology.lower().strip()

        # Check explicit skill entry first
        for s in profile.skills:
            if s.name.lower().strip() == tech_lower or getattr(s, "canonical_name", "").lower() == tech_lower:
                if getattr(s, "years_experience", None) is not None:
                    return float(s.years_experience)

        # Fall back to employment records where technology is listed
        matching_intervals: list[tuple[float, float]] = []
        now_f = datetime.now(UTC).year + (datetime.now(UTC).month / 12.0)

        for exp in profile.experience:
            techs = [t.lower().strip() for t in exp.technologies]
            if tech_lower in techs:
                start_f = cls._parse_date_to_float(exp.start_date, default_year=datetime.now(UTC).year)
                if start_f is not None:
                    end_f = now_f if (exp.is_current or not exp.end_date) else cls._parse_date_to_float(exp.end_date, default_year=datetime.now(UTC).year) or now_f
                    matching_intervals.append((start_f, max(start_f, end_f)))

        years = cls._merge_intervals_duration(matching_intervals)
        return round(years, 1)

    @staticmethod
    def _parse_date_to_float(date_str: Optional[str], default_year: int) -> Optional[float]:
        if not date_str:
            return None
        clean = date_str.strip()
        # YYYY-MM
        m_ym = re.match(r"^(\d{4})-(\d{1,2})", clean)
        if m_ym:
            y = int(m_ym.group(1))
            m = max(1, min(12, int(m_ym.group(2))))
            return y + (m / 12.0)
        # YYYY
        m_y = re.match(r"^(\d{4})", clean)
        if m_y:
            return float(m_y.group(1))
        return None

    @staticmethod
    def _merge_intervals_duration(intervals: list[tuple[float, float]]) -> float:
        """Merges overlapping intervals and returns total non-overlapping duration in years."""
        if not intervals:
            return 0.0

        sorted_intervals = sorted(intervals, key=lambda x: x[0])
        merged: list[tuple[float, float]] = []

        for start, end in sorted_intervals:
            if not merged:
                merged.append((start, end))
            else:
                prev_start, prev_end = merged[-1]
                if start <= prev_end:
                    merged[-1] = (prev_start, max(prev_end, end))
                else:
                    merged.append((start, end))

        total_years = sum(end - start for start, end in merged)
        return max(0.0, total_years)
