"""Tests for DOM inspection, accessibility tree extraction, and form analysis."""

import pytest
from app.browser.contracts import (
    BrowserActionRequest,
    BrowserActionType,
    BrowserSessionCreateRequest,
    DOMInspectionRequest,
    FormFieldInfo,
    FormInspectionResponse,
)
from app.browser.interaction.dom import DOMExtractor
from app.browser.interaction.forms import FormAnalyzer
from app.browser.interaction.actions import ActionExecutor
from app.browser.interaction.verification import ActionVerifier
from app.browser.service import BrowserService
from app.db.engine import get_db_session

SAMPLE_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>AUTONOM Recruitment Portal</title></head>
<body>
    <h1>Job Application Portal</h1>
    <a href="https://example.com/jobs" role="link">View Open Positions</a>
    <form id="applicant-form" action="/submit-job" method="POST">
        <label for="full_name">Full Name</label>
        <input type="text" id="full_name" name="full_name" placeholder="John Doe" required />

        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" placeholder="john@example.com" required />

        <label for="phone">Phone Number</label>
        <input type="tel" id="phone" name="phone" placeholder="+1-555-0199" />

        <label for="linkedin">LinkedIn Profile</label>
        <input type="url" id="linkedin" name="linkedin_url" placeholder="https://linkedin.com/in/..." />

        <button type="submit" id="submit-btn">Submit Application</button>
    </form>
    <button id="cancel-btn">Cancel</button>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_dom_inspection_and_form_extraction():
    service = BrowserService.get_instance()
    async with get_db_session() as db:
        session_resp = await service.create_session(db, BrowserSessionCreateRequest(is_headless=True))
        live = service.session_manager.get_live_session(session_resp.id)
        assert live is not None
        page = live.get_active_page()

        # Load test HTML directly into live page
        await page.set_content(SAMPLE_PAGE_HTML)

        # Run DOM inspection
        dom_resp = await DOMExtractor.inspect(
            page,
            session_id=session_resp.id,
            tab_id=session_resp.tabs[0].id,
            request=DOMInspectionRequest(max_elements=50),
        )

        assert dom_resp.title == "AUTONOM Recruitment Portal"
        assert len(dom_resp.elements) >= 5
        assert len(dom_resp.forms) == 1

        # Check form structure
        form = dom_resp.forms[0]
        assert form.form_id == "applicant-form"
        assert form.method == "POST"
        assert len(form.fields) == 4
        field_names = [f.name for f in form.fields]
        assert "full_name" in field_names
        assert "email" in field_names
        assert "phone" in field_names

        # Clean up session
        await service.close_session(db, session_resp.id)


def test_form_analyzer_field_mapping():
    form = FormInspectionResponse(
        form_id="job_app",
        action_url="https://jobs.example.com/apply",
        method="POST",
        fields=[
            FormFieldInfo(name="full_name", field_type="text", label="Full Name", required=True, selector="#name"),
            FormFieldInfo(name="email", field_type="email", label="Email", required=True, selector="#email"),
            FormFieldInfo(name="phone", field_type="tel", label="Mobile Phone", required=False, selector="#phone"),
            FormFieldInfo(name="linkedin_url", field_type="url", label="LinkedIn", required=False, selector="#linkedin"),
        ],
        submit_button_selector="#submit-btn",
        submit_button_text="Apply Now",
    )

    profile_data = {
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-0100",
        "linkedin_url": "https://linkedin.com/in/janesmith",
    }

    plan = FormAnalyzer.build_form_fill_plan(form, profile_data)
    assert len(plan["fill_steps"]) == 4
    assert plan["unmatched_required_count"] == 0
    assert plan["requires_submission_authorization"] is True
    assert plan["submit_button_selector"] == "#submit-btn"


@pytest.mark.asyncio
async def test_action_executor_and_verifier():
    service = BrowserService.get_instance()
    async with get_db_session() as db:
        session_resp = await service.create_session(db, BrowserSessionCreateRequest(is_headless=True))
        live = service.session_manager.get_live_session(session_resp.id)
        assert live is not None
        page = live.get_active_page()

        await page.set_content(SAMPLE_PAGE_HTML)

        # 1. Fill full_name input
        fill_req = BrowserActionRequest(
            action_type=BrowserActionType.FILL,
            target_locator="#full_name",
            parameters={"value": "Alice Developer"},
        )
        fill_resp = await ActionExecutor.execute(page, session_resp.id, session_resp.tabs[0].id, fill_req)
        assert fill_resp.status.value == "succeeded"

        # Verify fill outcome
        fill_ver = await ActionVerifier.verify(
            page, BrowserActionType.FILL, "#full_name", {"value": "Alice Developer"}
        )
        assert fill_ver["verified"] is True

        # 2. Click cancel button
        click_req = BrowserActionRequest(
            action_type=BrowserActionType.CLICK,
            target_locator="#cancel-btn",
        )
        click_resp = await ActionExecutor.execute(page, session_resp.id, session_resp.tabs[0].id, click_req)
        assert click_resp.status.value == "succeeded"

        # Clean up session
        await service.close_session(db, session_resp.id)
