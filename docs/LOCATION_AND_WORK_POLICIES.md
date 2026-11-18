# AUTONOM Location, Remote & Work Policies

## Stage 25 of 50 — Geographic & Arrangement Governance

---

### Work Arrangements

The engine enforces four distinct work models:
- **`remote`**: 100% work-from-home, distributed team.
- **`hybrid`**: Partial onsite requirement (governed by `max_hybrid_days_onsite`).
- **`onsite`**: 100% in-office requirement.
- **`flexible`**: Employee-directed arrangement.

---

### Geographic Inclusions & Exclusions

```
                          Job Opportunity Location
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
             Explicitly Excluded?             Target Country/City?
                    │                                 │
           YES ─────┴─────► Level 8 REJECT            ▼
                                             In Target Geography?
                                                      │
                                             NO ──────┴─────► Level 8 REJECT
                                                      │ YES
                                                      ▼
                                                Eligible Geography
```

- **Excluded Geographies**: Immediate Level 8 rejection if the job is located in an excluded city, state, or country (e.g. `excluded_cities: ["Dallas"]`).
- **Relocation Preferences**: Governed by `not_willing`, `willing_domestic`, `willing_international`, `remote_only`, or `open`.
- **Time Zone Boundaries**: Compares target IANA timezone offsets against applicant home timezone. Rejects listings exceeding `max_timezone_offset_hours` unless the role is asynchronous.
