# Intelligent Job Duplicate Detection & Similarity Scoring (Stage 27)

## Overview
Duplicate detection determines when multiple source postings describe the exact same underlying hiring vacancy while strictly preserving distinct vacancies that merely share similar job titles.

## Multi-Factor Scoring Architecture

$$\text{Composite Score} = (0.40 \times S_{\text{title}}) + (0.40 \times S_{\text{desc}}) + (0.10 \times S_{\text{loc}}) + (0.10 \times S_{\text{type}})$$

### Factor Breakdown
1. **Title Token Cosine & Jaccard Similarity (40%)**:
   - Compares cleaned core title strings (e.g. `Senior Staff Software Engineer` vs `Sr. Staff Software Engineer`).
2. **Description N-Gram Jaccard (40%)**:
   - Shingles clean job description text into character and token n-grams to detect identical role scopes and responsibilities.
3. **Location Compatibility (10%)**:
   - Evaluates geographical alignment.
4. **Employment Type Compatibility (10%)**:
   - Assesses contract vs full-time consistency.

## Negative Evidence & Hard Contradictions
Heuristic similarity is immediately overridden to zero if any negative evidence rule triggers:
1. **Different Requisition IDs**: Vacancies under the same employer with explicit, differing requisition codes (e.g., `REQ-101` vs `REQ-102`) CANNOT be merged.
2. **Seniority Contradictions**: Pairings between `Junior / Associate` and `Staff / Principal` are forbidden from merging.
3. **Employment Type Clashes**: `Internship` vs `Full-time Permanent` are never merged.
4. **Physical Location Discrepancies**: Differing non-remote locations (e.g. London vs New York) are prohibited from merging *unless* they share the exact same requisition ID (multi-office same requisition exemption).

## Decision Thresholds
- **$\ge 0.92$ (or Deterministic Exact Rule)**: Automatic Merge into canonical vacancy.
- **$0.75 - 0.91$**: Queued to Human Review Queue (`duplicate_review`).
- **$< 0.75$**: Kept strictly separate as independent canonical vacancies.
