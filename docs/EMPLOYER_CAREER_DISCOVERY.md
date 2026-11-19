# Employer Career Discovery and ATS Detection (Stage 26)

## Overview
Many companies host branded career portals on custom domains (e.g. `careers.stripe.com`, `netflix.jobs`, `openai.com/careers`). AUTONOM's `CareerPageConnector` extracts opportunities from approved origins using progressive discovery:

```mermaid
flowchart TD
    A["Target Employer Career URL"] --> B["Origin Verification & SSRF Check"]
    B --> C["Static HTTP Fetch"]
    C --> D{"Schema.org JobPosting in HTML?"}
    D -- "Yes" --> E["Extract JSON-LD JobPosting metadata"]
    D -- "No" --> F{"Embedded ATS detected?"}
    F -- "Yes (Greenhouse/Lever/Ashby)" --> G["Delegate to specialized ATS connector"]
    F -- "No" --> H["Extract Semantic Job Links from HTML"]
    H --> I{"SPA / Empty Links & Browser Allowed?"}
    I -- "Yes" --> J["Bounded Headless Browser DOM Inspection"]
    I -- "No" --> K["Return Extracted Static Observations"]
```

## ATS Platform Heuristics
The `ats_detection` subsystem inspects URL structures, redirects, and inline script tags:
- **Greenhouse**: `boards.greenhouse.io/{token}` or `greenhouse.io/embed`.
- **Lever**: `jobs.lever.co/{site}` or `api.lever.co`.
- **Ashby**: `jobs.ashbyhq.com/{token}` or `ashby_embed`.
- **Workday**: `*.myworkdayjobs.com` -> parses Schema.org JobPosting.
- **SmartRecruiters**: `jobs.smartrecruiters.com` -> parses structured JSON-LD.
