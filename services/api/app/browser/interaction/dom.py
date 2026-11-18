"""DOM inspection and structured accessibility tree extraction for AI agents."""

import json
import logging
from typing import Any
from playwright.async_api import Page

from app.browser.contracts import (
    DOMElementNode,
    DOMInspectionRequest,
    DOMInspectionResponse,
    FormFieldInfo,
    FormInspectionResponse,
)

logger = logging.getLogger(__name__)

# In-page JS script to extract interactive elements and forms cleanly
EXTRACT_INTERACTIVE_DOM_JS = """
(maxElements) => {
    let nextId = 1;
    const elements = [];
    const forms = [];
    
    // Select interactive candidates
    const selector = 'button, a[href], input, select, textarea, [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [tabindex]:not([tabindex="-1"])';
    const nodes = Array.from(document.querySelectorAll(selector));

    for (const node of nodes) {
        if (elements.length >= maxElements) break;

        // Check visibility
        const style = window.getComputedStyle(node);
        const isVisible = style && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
        const rect = node.getBoundingClientRect();
        const inViewport = (rect.width > 0 && rect.height > 0);

        if (!isVisible || !inViewport) continue;

        const id = nextId++;
        node.setAttribute('data-autonom-id', String(id));

        const tag = node.tagName.toLowerCase();
        const role = node.getAttribute('role') || (tag === 'button' ? 'button' : tag === 'a' ? 'link' : tag === 'input' ? 'input' : null);
        const name = node.getAttribute('name') || node.getAttribute('aria-label') || node.getAttribute('title') || null;
        let text = (node.innerText || node.textContent || '').trim().replace(/\\s+/g, ' ');
        if (text.length > 100) text = text.substring(0, 100) + '...';

        const placeholder = node.getAttribute('placeholder') || null;
        const val = (node.value !== undefined && tag !== 'button' && tag !== 'a') ? String(node.value) : null;
        const isEnabled = !node.disabled && !node.getAttribute('aria-disabled');
        const isClickable = tag === 'button' || tag === 'a' || role === 'button' || role === 'link' || typeof node.onclick === 'function';
        const isChecked = node.type === 'checkbox' || node.type === 'radio' ? node.checked : (node.getAttribute('aria-checked') === 'true');

        const attributes = {};
        if (node.id) attributes['id'] = node.id;
        if (node.className && typeof node.className === 'string') attributes['class'] = node.className.substring(0, 50);
        if (node.type) attributes['type'] = node.type;
        if (node.href) attributes['href'] = node.href.substring(0, 120);

        let selectorStr = `[data-autonom-id='${id}']`;
        if (node.id) selectorStr = `#${node.id}`;
        else if (name) selectorStr = `${tag}[name='${name}']`;

        elements.push({
            id: id,
            tag: tag,
            role: role,
            name: name,
            text: text || null,
            placeholder: placeholder,
            value: val,
            selector: selectorStr,
            is_visible: true,
            is_enabled: isEnabled,
            is_clickable: isClickable,
            is_checked: isChecked,
            attributes: attributes
        });
    }

    // Inspect forms
    const formNodes = Array.from(document.querySelectorAll('form'));
    for (const f of formNodes) {
        const formId = f.id || f.getAttribute('name') || null;
        const actionUrl = f.getAttribute('action') || null;
        const method = (f.getAttribute('method') || 'GET').toUpperCase();
        
        const fieldNodes = Array.from(f.querySelectorAll('input, select, textarea'));
        const fields = [];
        let submitBtnSelector = null;
        let submitBtnText = null;

        for (const fn of fieldNodes) {
            const ftype = (fn.getAttribute('type') || fn.tagName.toLowerCase()).toLowerCase();
            if (ftype === 'submit' || ftype === 'button') {
                submitBtnSelector = fn.id ? `#${fn.id}` : `button[type='submit']`;
                submitBtnText = (fn.innerText || fn.value || '').trim();
                continue;
            }

            const fname = fn.getAttribute('name') || fn.id || '';
            const fplaceholder = fn.getAttribute('placeholder') || null;
            const frequired = fn.required || fn.getAttribute('aria-required') === 'true';
            const fval = fn.value || null;
            const isSens = ftype === 'password' || fname.toLowerCase().includes('password') || fname.toLowerCase().includes('token') || fname.toLowerCase().includes('ssn');

            let flabel = null;
            if (fn.id) {
                const l = document.querySelector(`label[for='${fn.id}']`);
                if (l) flabel = (l.innerText || '').trim();
            }

            fields.push({
                name: fname,
                field_type: ftype,
                label: flabel,
                placeholder: fplaceholder,
                required: frequired,
                current_value: fval,
                selector: fn.id ? `#${fn.id}` : `${fn.tagName.toLowerCase()}[name='${fname}']`,
                is_sensitive: isSens
            });
        }

        const submitBtn = f.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
        if (submitBtn && !submitBtnSelector) {
            submitBtnSelector = submitBtn.id ? `#${submitBtn.id}` : 'button[type="submit"]';
            submitBtnText = (submitBtn.innerText || submitBtn.value || '').trim();
        }

        forms.push({
            form_id: formId,
            action_url: actionUrl,
            method: method,
            fields: fields,
            submit_button_selector: submitBtnSelector,
            submit_button_text: submitBtnText
        });
    }

    return {
        elements: elements,
        forms: forms,
        total_count: elements.length
    };
}
"""


class DOMExtractor:
    """Extracts compact, structured DOM trees and form representations for AI agent consumption."""

    @classmethod
    async def inspect(
        cls,
        page: Page,
        session_id: str,
        tab_id: str,
        request: DOMInspectionRequest | None = None,
    ) -> DOMInspectionResponse:
        """Inspects the active page DOM and returns structured interactive elements and forms."""
        req = request or DOMInspectionRequest()
        url = page.url
        title = await page.title()

        try:
            raw_data = await page.evaluate(EXTRACT_INTERACTIVE_DOM_JS, req.max_elements)
            raw_elements = raw_data.get("elements", [])
            raw_forms = raw_data.get("forms", []) if req.include_forms else []

            elements: list[DOMElementNode] = []
            for e in raw_elements:
                elements.append(
                    DOMElementNode(
                        id=e["id"],
                        tag=e["tag"],
                        role=e.get("role"),
                        name=e.get("name"),
                        text=e.get("text"),
                        placeholder=e.get("placeholder"),
                        value=e.get("value"),
                        selector=e["selector"],
                        is_visible=e["is_visible"],
                        is_enabled=e["is_enabled"],
                        is_clickable=e["is_clickable"],
                        is_checked=e.get("is_checked"),
                        attributes=e.get("attributes", {}),
                    )
                )

            forms: list[FormInspectionResponse] = []
            for f in raw_forms:
                fields: list[FormFieldInfo] = []
                for fld in f.get("fields", []):
                    fields.append(
                        FormFieldInfo(
                            name=fld["name"],
                            field_type=fld["field_type"],
                            label=fld.get("label"),
                            placeholder=fld.get("placeholder"),
                            required=fld["required"],
                            current_value=fld.get("current_value"),
                            selector=fld["selector"],
                            is_sensitive=fld["is_sensitive"],
                        )
                    )
                forms.append(
                    FormInspectionResponse(
                        form_id=f.get("form_id"),
                        action_url=f.get("action_url"),
                        method=f.get("method", "POST"),
                        fields=fields,
                        submit_button_selector=f.get("submit_button_selector"),
                        submit_button_text=f.get("submit_button_text"),
                    )
                )

            # Estimate token cost (~4 chars per token)
            serialized = json.dumps([e.model_dump() for e in elements])
            token_estimate = max(1, len(serialized) // 4)

            return DOMInspectionResponse(
                session_id=session_id,
                tab_id=tab_id,
                url=url,
                title=title,
                elements=elements,
                forms=forms,
                total_elements_count=len(elements),
                token_estimate=token_estimate,
            )

        except Exception as exc:
            logger.error(f"Error during DOM inspection on {url}: {exc}")
            return DOMInspectionResponse(
                session_id=session_id,
                tab_id=tab_id,
                url=url,
                title=title,
                elements=[],
                forms=[],
                total_elements_count=0,
                token_estimate=0,
            )
