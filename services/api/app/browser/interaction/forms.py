"""Form analysis and safe field mapping for recruitment and desktop automation."""

import logging
import re
from typing import Any
from app.browser.contracts import FormFieldInfo, FormInspectionResponse

logger = logging.getLogger(__name__)

STANDARD_APPLICANT_FIELD_PATTERNS = {
    "first_name": re.compile(r"first[_\s-]?name|given[_\s-]?name|fname", re.I),
    "last_name": re.compile(r"last[_\s-]?name|family[_\s-]?name|lname|surname", re.I),
    "full_name": re.compile(r"full[_\s-]?name|^name$", re.I),
    "email": re.compile(r"e[_\s-]?mail", re.I),
    "phone": re.compile(r"phone|tel|mobile|cell", re.I),
    "linkedin_url": re.compile(r"linkedin", re.I),
    "github_url": re.compile(r"github", re.I),
    "portfolio_url": re.compile(r"portfolio|website|homepage", re.I),
    "location": re.compile(r"location|city|address|postal|zip", re.I),
    "resume": re.compile(r"resume|cv|curriculum", re.I),
    "cover_letter": re.compile(r"cover[_\s-]?letter|message|note", re.I),
}


class FormAnalyzer:
    """Analyzes web forms and maps applicant profile attributes to discovered inputs."""

    @classmethod
    def match_field_to_attribute(cls, field: FormFieldInfo) -> str | None:
        """Determines which applicant attribute matches a form input field."""
        search_target = f"{field.name} {field.label or ''} {field.placeholder or ''}"
        for attr, pattern in STANDARD_APPLICANT_FIELD_PATTERNS.items():
            if pattern.search(search_target):
                return attr
        return None

    @classmethod
    def build_form_fill_plan(
        cls,
        form: FormInspectionResponse,
        applicant_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Constructs a plan mapping applicant profile data to form field selectors."""
        fill_steps: list[dict[str, Any]] = []
        unmatched_fields: list[FormFieldInfo] = []

        for field in form.fields:
            if field.field_type in ("submit", "button", "hidden"):
                continue

            attr = cls.match_field_to_attribute(field)
            if attr and attr in applicant_profile:
                val = applicant_profile[attr]
                if val:
                    fill_steps.append({
                        "field_name": field.name,
                        "attribute": attr,
                        "selector": field.selector,
                        "value": str(val),
                        "field_type": field.field_type,
                        "required": field.required,
                    })
            else:
                unmatched_fields.append(field)

        return {
            "form_id": form.form_id,
            "action_url": form.action_url,
            "fill_steps": fill_steps,
            "unmatched_required_count": sum(1 for f in unmatched_fields if f.required),
            "unmatched_fields": [f.model_dump() for f in unmatched_fields],
            "submit_button_selector": form.submit_button_selector,
            "submit_button_text": form.submit_button_text,
            "requires_submission_authorization": True,
        }
