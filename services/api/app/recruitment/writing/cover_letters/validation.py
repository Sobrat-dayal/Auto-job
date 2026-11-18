"""Factual Grounding & Anti-Hallucination Validator for Cover Letters (Stage 24)."""

from __future__ import annotations

import logging
import re
from typing import Any
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.writing.contracts import CoverLetterDocument

logger = logging.getLogger("autonom.recruitment.writing.cover_letters.validation")


class CoverLetterValidator:
    """Verifies that cover letter claims are strictly grounded in canonical applicant profile facts."""

    @classmethod
    def validate_cover_letter(
        cls,
        doc: CoverLetterDocument,
        profile: ApplicantProfile,
    ) -> dict[str, Any]:
        issues: list[str] = []
        warnings: list[str] = []

        full_text = "\n".join([b.text for b in doc.blocks])
        text_lower = full_text.lower()

        # 1. Identity Check
        applicant_name = getattr(profile.contact, "legal_name", None) or getattr(profile.contact, "preferred_name", None)
        if applicant_name and applicant_name.lower() not in text_lower:
            warnings.append(f"Applicant legal name '{applicant_name}' is not clearly visible in header or signature.")

        # 2. Target Role Check
        if doc.target_role and doc.target_role.lower() not in text_lower:
            warnings.append(f"Target role '{doc.target_role}' is not referenced in the cover letter text.")

        # 3. Word Count Check
        total_words = len(full_text.split())
        if doc.max_words and total_words > doc.max_words + 50:
            warnings.append(f"Cover letter word count ({total_words}) exceeds specified target limit ({doc.max_words}).")
        elif total_words < 60:
            issues.append(f"Cover letter is too short ({total_words} words); requires substantive content.")

        # 4. Factual Grounding: Degree Check
        if profile.education:
            degrees = [e.degree.lower() for e in profile.education if e.degree]
            has_degree_match = any(deg in text_lower for deg in degrees)
            if not has_degree_match:
                warnings.append("No reference to the applicant's confirmed academic degrees detected.")
        else:
            # If profile has no education, ensure letter doesn't falsely claim a completed degree
            if any(term in text_lower for term in ["graduated with a degree", "bachelor of science", "master of science", "ph.d."]):
                issues.append("Cover letter claims a degree that is not recorded in the candidate's canonical profile.")

        # 5. Factual Grounding: Experience Check
        if not profile.experience:
            if any(term in text_lower for term in ["during my tenure as", "in my previous full-time role", "as a senior engineer at"]):
                issues.append("Cover letter claims full-time engineering employment not evidenced in canonical profile.")

        # 6. Salutation Check
        salutation_block = next((b for b in doc.blocks if b.block_type == "salutation"), None)
        if not salutation_block or not salutation_block.text.strip():
            warnings.append("Missing formal salutation block.")

        # 7. Signature Check
        signature_block = next((b for b in doc.blocks if b.block_type == "signature"), None)
        if not signature_block or not signature_block.text.strip():
            warnings.append("Missing professional signature block.")

        is_valid = len(issues) == 0

        return {
            "is_valid": is_valid,
            "total_words": total_words,
            "issues": issues,
            "warnings": warnings,
            "grounding_status": "grounded" if is_valid else "violations_detected",
        }
