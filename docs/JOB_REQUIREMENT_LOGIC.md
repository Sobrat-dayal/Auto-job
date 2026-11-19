# Logical Requirement Semantics and Negation (Stage 28)

## 1. Overview
Real job descriptions express requirements using nuanced boolean and conditional semantics. Flattening these statements into independent strings produces false rejections or incorrect matches. Stage 28 introduces the `RequirementGroup` model to capture rich logical relationships.

## 2. Supported Logical Operators
- `AND`: Conjunction. All child requirements must be satisfied (e.g. "Python and PostgreSQL").
- `OR`: Disjunction. At least one child requirement must be satisfied (e.g. "Python or Go").
- `AtLeastN`: Threshold choice. At least N items from a set must be satisfied (e.g. "At least 2 of Python, Java, Go").
- `EquivalentAlternative`: Alternative equivalency substitution (e.g. "Bachelor's degree or 4 years equivalent practical experience").
- `Conditional`: Qualification triggered only under certain conditions (e.g. "Security clearance required if assigned to defense client").
- `NOT`: Scoped negation. Explicitly indicates that a skill, degree, or condition is NOT required.

## 3. Scoped Negation Parsing
Adversarial and careless extraction pipelines frequently convert negative phrases into positive requirements. AUTONOM parses scoped negation patterns:
- "Prior AWS experience not required" -> Excluded from positive requirements.
- "No prior professional experience required" -> `minimum_years = 0.0`, `is_mandatory = False`.
- "High school diploma or degree not required" -> `degree_level = DegreeLevel.NOT_REQUIRED`.
- "Sponsorship unavailable" -> `visa_sponsorship_refused = True`.

## 4. Tree Model Example
```
Minimum Qualifications [AND]
├── Python [Mandatory, 5+ yrs]
├── PostgreSQL [Mandatory, 3+ yrs]
└── Education Equivalency [OR / EquivalentAlternative]
    ├── Bachelor's Degree in Computer Science
    └── 4 Years Equivalent Practical Experience
```
