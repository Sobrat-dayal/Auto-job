# AUTONOM Employer & Industry Restrictions

## Stage 25 of 50 — Organization Governance & Filtering

---

### Filtering Modes

1. **`no_allowlist` (Open Market)**:
   - Any legitimate hiring company is considered unless explicitly matched on the Blocklist.
2. **`prefer_allowlist` (Tiered Preference)**:
   - Opportunities at approved companies receive high soft-score bonuses; open market companies are still considered.
3. **`strict_allowlist` (Veto Enforcement)**:
   - All opportunities at organizations not present on the Allowed Employers list are immediately rejected at Level 8.

---

### Employer Blocklists & Ambiguity Detection

- **Exact & Normalized Matching**:
  - Employer names are normalized (stripped of punctuation, common legal suffixes like "Inc", "LLC", "Corp", "GmbH", and lowercased).
  - Domain matching checks root domain equality (e.g. `careers.stripe.com` matches `stripe.com`).
- **Brand Ambiguity Detection**:
  - If a job mentions a company that shares 4+ character tokens with an existing entity (e.g. "Stripe Payments" vs "Stripe"), AUTONOM flags identity ambiguity and triggers `ReviewTrigger.EMPLOYER_AMBIGUOUS` to prevent accidental submissions to unwanted subsidiaries or phishing recruiters.
- **Industry Restrictions**:
  - Keywords such as `gambling`, `tobacco`, `weapons`, or `crypto` can be blacklisted.
