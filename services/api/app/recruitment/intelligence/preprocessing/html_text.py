"""HTML normalization and cleaning for job descriptions."""

import html
import re


def clean_html_description(raw_html_or_text: str) -> str:
    """Normalize HTML or text into clean plain text preserving structure and list items."""
    if not raw_html_or_text:
        return ""

    text = raw_html_or_text

    # If it doesn't look like HTML, normalize newlines and whitespace directly
    if "<" not in text and ">" not in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse excessive newlines
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    # Pre-clean script and style blocks
    text = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", text, flags=re.IGNORECASE)

    # Convert structural HTML tags to newlines or bullets
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*p\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/div\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*div\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*li\b[^>]*>", "\n• ", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/li\s*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/?(?:ul|ol)\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*h[1-6]\b[^>]*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/h[1-6]\s*>", "\n\n", text, flags=re.IGNORECASE)

    # Strip all remaining tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode HTML entities (e.g. &amp;, &quot;, &nbsp;, &#39;, &mdash;, &ndash;)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")

    # Normalize line breaks and spaces
    lines = [line.strip() for line in text.splitlines()]
    # Remove excessive blank lines
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    return "\n".join(cleaned_lines).strip()
