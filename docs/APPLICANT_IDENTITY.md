# AUTONOM Applicant Identity Management (Stage 21)

## 1. Scope & Objective

The Applicant Identity subsystem manages legal name, contact coordinates, geographic location, and employment eligibility. In keeping with AUTONOM's strict security standards:
- User-provided data is preserved without unsolicited alteration.
- Automated extraction from resumes or documents will never override user-confirmed identity fields without explicit review.
- Downstream recruitment agents receive restricted views governed by Stage 14 permissions.

---

## 2. Identity Fields & Specifications

### 2.1 Contact Information
- **Legal Name**: The official legal name required for payroll and government verification.
- **Preferred Name**: Used in friendly communication or interview context.
- **Primary Email**: Validated against RFC 5322 regex.
- **Phone**: Stored in standard format with international country code.
- **Professional Links**: GitHub, LinkedIn, portfolio websites, and scholarly profiles.

### 2.2 Geographic Location & Work Preferences
- **Structured Address**: City, State/Province, Postal Code, Country.
- **Timezone**: Extracted or selected from standard IANA tz database (e.g. `America/Chicago`).
- **Remote Preferences**:
  - `remote_only`: Only remote roles accepted.
  - `hybrid`: Willing to commute part of the week.
  - `onsite`: Open to full-time office work.
  - `flexible`: Adaptable to employer structure.
- **Relocation Willingness**: Flag with optional destination constraints.

### 2.3 Legal Employment Eligibility
Recruitment agents frequently interact with applicant tracking systems (ATS) that require legal attestations regarding work authorization. AUTONOM strictly enforces:
- **Zero Hallucination**: AUTONOM will NEVER invent work authorization, visa sponsorships, or clearances.
- **Explicit Confirmation**: The applicant must check `confirmed_by_user: true` in the desktop UI before any agent is authorized to submit applications claiming work eligibility.
- **Sponsorship Clarity**: Explicit boolean `requires_sponsorship` and visa status string ensure clear disclosure.

---

## 3. Storage and Data Protection

1. **Local Isolation**: All profile data is persisted in the local SQLite/app database and encrypted vault directory (`~/.autonom/evidence/`).
2. **Access Scopes**:
   - `applicant.identity.read`
   - `applicant.contact.read`
   - `applicant.eligibility.read`
   - `applicant.profile.update`
3. **Tenant Boundary**: `owner_id` verification prevents multi-tenant crossover on shared systems.
