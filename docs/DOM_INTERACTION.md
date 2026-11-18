# DOM Interaction and Form Analysis (Stage 16)

## 1. Overview and Problem Statement

Modern Single-Page Applications (SPAs) and dynamic job application portals (Workday, Greenhouse, Lever, Ashby) feature complex, nested, and deeply mutated Document Object Model (DOM) structures. Sending raw HTML directly to LLM agents incurs prohibitive token costs, introduces noise, and slows down orchestration loops.

AUTONOM Stage 16 introduces:
1. **Interactive Element DOM Extractor** (`services/api/app/browser/interaction/dom.py`): In-page JavaScript extraction that isolates only interactive elements (buttons, inputs, links, forms, selects) into a clean, token-efficient hierarchical tree.
2. **Multi-Strategy Smart Locators** (`services/api/app/browser/interaction/locators.py`): Robust element targeting supporting semantic roles, labels, text content, CSS, and XPath.
3. **Automated Form Analyzer** (`services/api/app/browser/interaction/forms.py`): Discovers and maps application forms to verified applicant profile fields.
4. **Action Verification Engine** (`services/api/app/browser/interaction/verification.py`): Verifies state changes after action dispatch.

---

## 2. In-Page DOM Extraction Algorithm

The DOM extractor injects a lightweight JavaScript function into the target page context. It traverses visible, interactive DOM nodes and extracts structured metadata:

```json
{
  "tag": "button",
  "role": "button",
  "text": "Submit Application",
  "id": "btn-apply-submit",
  "name": "",
  "type": "submit",
  "value": "",
  "placeholder": "",
  "aria_label": "Submit Application",
  "is_visible": true,
  "is_enabled": true,
  "bounding_box": { "x": 450, "y": 720, "width": 180, "height": 44 },
  "suggested_locator": "role=button[name='Submit Application']"
}
```

### Token Reduction Metrics
- Typical raw DOM HTML: ~25,000 to ~150,000 tokens.
- Extracted Interactive Element Tree: ~300 to ~1,500 tokens.
- **Average token savings: 94% - 98%**, allowing fast and reliable LLM reasoning.

---

## 3. Multi-Strategy Smart Locators

The `LocatorResolver` resolves locators in order of robustness and accessibility standards:

| Prefix / Pattern | Example | Resolution Strategy |
| :--- | :--- | :--- |
| `role=` | `role=button[name='Apply']` | Resolves via `page.get_by_role()` |
| `text=` | `text=Continue to Step 2` | Resolves via `page.get_by_text(exact=False)` |
| `placeholder=` | `placeholder=Enter your email` | Resolves via `page.get_by_placeholder()` |
| `label=` | `label=Full Legal Name` | Resolves via `page.get_by_label()` |
| `test-id=` | `test-id=resume-upload-input` | Resolves via `page.get_by_test_id()` |
| `[id]` | `#submit-job-form` | Resolves via standard CSS ID selector |
| `css=` / `xpath=` | `//form//button[@type='submit']` | Direct Playwright locator query |

---

## 4. Form Field Analysis and Semantic Mapping

The `FormAnalyzer` inspects all `<form>` containers and standalone form controls on the page:

1. **Classification**: Maps input fields into semantic types:
   - `first_name`, `last_name`, `full_name`
   - `email`, `phone`, `location`, `linkedin_url`, `github_url`, `portfolio_url`
   - `resume_upload`, `cover_letter`
   - `work_authorization`, `sponsorship_required`, `eeo_gender`, `eeo_veteran`
2. **Applicant Profile Matching**: Matches extracted fields against the user's verified applicant profile in the database.
3. **Confidence Scoring**: Computes a confidence score (0.0 to 1.0) for every matched field.
4. **Submission Boundary Enforcement**: Identifies the submission button and asserts whether the agent is preauthorized to click it or if a user approval request is required under Stage 14 policies.

---

## 5. Action Verification Engine

Every action execution (click, fill, navigate, select) is evaluated by the `ActionVerifier`:

- **Navigation Verification**: Asserts that `page.url` matches the target or expected domain.
- **Visibility Verification**: Asserts that the targeted element, or an expected follow-up element (e.g. success banner, confirmation modal), is visible.
- **Value Verification**: For `fill` actions, reads back the element's `.input_value()` to guarantee the text was accepted by the component framework (React, Vue, Angular).
- **Error Detection**: Scans the page for standard error banners (`.error-message`, `[role='alert']`, `alert-danger`) and flags action failures.
