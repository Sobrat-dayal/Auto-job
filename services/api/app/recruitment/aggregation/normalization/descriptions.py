"""Description Normalization and Text Similarity Engine (Stage 27)."""

import html
import math
import re
from collections import Counter


def clean_description_text(raw_text: str) -> str:
    """Strip HTML tags, unescape entities, and collapse whitespace."""
    if not raw_text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", raw_text)
    cleaned = html.unescape(cleaned)
    # Lowercase & collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).lower().strip()
    return cleaned


def tokenize_text(text: str) -> list[str]:
    """Tokenize cleaned text into word tokens, discarding single-character noise."""
    tokens = re.findall(r"\b[a-z0-9_\-#+]{2,}\b", text.lower())
    return tokens


def calculate_jaccard_similarity(text_a: str, text_b: str) -> float:
    """Calculate token Jaccard similarity between two texts."""
    clean_a = clean_description_text(text_a)
    clean_b = clean_description_text(text_b)

    tokens_a = set(tokenize_text(clean_a))
    tokens_b = set(tokenize_text(clean_b))

    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0

    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))

    return round(intersection / union, 4)


def calculate_ngram_jaccard(text_a: str, text_b: str, n: int = 3) -> float:
    """Calculate character n-gram Jaccard similarity for short strings like titles."""
    clean_a = clean_description_text(text_a)
    clean_b = clean_description_text(text_b)

    if not clean_a and not clean_b:
        return 1.0
    if not clean_a or not clean_b:
        return 0.0

    ngrams_a = {clean_a[i : i + n] for i in range(len(clean_a) - n + 1)}
    ngrams_b = {clean_b[i : i + n] for i in range(len(clean_b) - n + 1)}

    if not ngrams_a and not ngrams_b:
        return 1.0
    if not ngrams_a or not ngrams_b:
        return 0.0

    return round(len(ngrams_a.intersection(ngrams_b)) / len(ngrams_a.union(ngrams_b)), 4)


def calculate_token_cosine_similarity(text_a: str, text_b: str) -> float:
    """Calculate term-frequency cosine similarity."""
    clean_a = clean_description_text(text_a)
    clean_b = clean_description_text(text_b)

    tokens_a = tokenize_text(clean_a)
    tokens_b = tokenize_text(clean_b)

    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0

    counts_a = Counter(tokens_a)
    counts_b = Counter(tokens_b)

    all_keys = set(counts_a.keys()).union(set(counts_b.keys()))

    dot_product = sum(counts_a[k] * counts_b[k] for k in all_keys)
    magnitude_a = math.sqrt(sum(v * v for v in counts_a.values()))
    magnitude_b = math.sqrt(sum(v * v for v in counts_b.values()))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return round(dot_product / (magnitude_a * magnitude_b), 4)
