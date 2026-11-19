"""HTML to clean text extraction preserving structure (Stage 26)."""

import html
import re
from app.recruitment.discovery.security.content_sanitization import sanitize_html


def extract_clean_text_from_html(html_content: str) -> str:
    """Transform HTML into clean plain text while maintaining section breaks and bullet points."""
    if not html_content or not isinstance(html_content, str):
        return ""

    sanitized = sanitize_html(html_content)

    # 1. Replace block elements with newlines
    text = re.sub(r"<\s*(h[1-6]|p|div|section|article)[^>]*>", "\n", sanitized, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/(h[1-6]|p|div|section|article)\s*>", "\n", text, flags=re.IGNORECASE)

    # 2. Replace list items with bullet points
    text = re.sub(r"<\s*li[^>]*>", "\n• ", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/li\s*>", "", text, flags=re.IGNORECASE)

    # 3. Replace breaks
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # 4. Remove all remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # 5. Decode HTML entities (&amp;, &nbsp;, etc.)
    text = html.unescape(text)

    # 6. Normalize excessive blank lines
    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_blank = False
        elif not prev_blank:
            cleaned_lines.append("")
            prev_blank = True

    return "\n".join(cleaned_lines).strip()


# Alias for convenience
extract_text_from_html = extract_clean_text_from_html
