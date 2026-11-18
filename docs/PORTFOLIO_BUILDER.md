# AUTONOM — Professional Portfolio Builder (Stage 23)

## 1. Portfolio Architecture & Motivation

Resumes are space-constrained documents (typically 1-2 pages) focused on career chronology. Software engineers, technical architects, and researchers require richer technical depth to showcase complex systems architecture, contribution evidence, code quality, and engineering narratives.

The **Portfolio Builder** (`PortfolioService`) creates multi-page project dossiers that combine:
- High-level technical narrative and engineering philosophy.
- Deep dives into showcased repositories and applications.
- Technology stacks and architectural diagrams.
- Direct links to verified public open-source contributions.
- Privacy filtering to protect confidential or private repositories.

---

## 2. Privacy Review & Repository Scrubbing

Engineers frequently connect GitHub accounts containing both open-source work and private repositories under client or proprietary NDAs.

Before generating any public portfolio document:
1. **Private Repository URL Removal**:
   Any repository tagged as private (`is_private == True`) has its URLs stripped.
2. **Confidential Claim Sanitization**:
   Metrics or architectural descriptions originating from unverified or confidential client projects are excluded.
3. **Public Contact Obfuscation**:
   Personal phone numbers and physical street addresses are replaced with city/region and professional email coordinates.

---

## 3. Dual Export Support

The portfolio builder exports documents in two distinct formats:

### 3.1 Multi-Page PDF Dossier
- Rendered via `ReportLab` with elegant typography, project summary blocks, technical stack badges, and contribution evidence callouts.
- Formatted for clean digital viewing or physical printing.

### 3.2 Standalone Static HTML Showcase
- Standalone HTML document containing responsive embedded CSS styles.
- Zero external runtime dependencies; can be hosted on GitHub Pages, Vercel, or attached to digital applications.
