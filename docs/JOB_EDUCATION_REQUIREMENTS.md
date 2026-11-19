# Education Requirements & Equivalencies (Stage 28)

## 1. Overview
The Education Extraction module identifies formal educational prerequisites, degree levels, acceptable fields of study, degree completion status, and practical experience substitutions.

## 2. Degree Levels
- `DOCTORATE`: Ph.D., Doctorate, Doctoral degree.
- `MASTER`: Master's degree, M.S., M.Sc., MBA, M.Eng.
- `BACHELOR`: Bachelor's degree, B.S., B.Sc., B.A., B.Eng., 4-year degree.
- `ASSOCIATE`: Associate's degree, 2-year college degree.
- `HIGH_SCHOOL`: High school diploma, GED, secondary school.
- `NOT_REQUIRED`: Explicitly states no degree is required.
- `EQUIVALENT`: Practical work experience accepted in lieu of a degree.

## 3. Fields of Study
Extracted disciplines include:
- Computer Science
- Software Engineering
- Data Science
- Information Technology
- Electrical Engineering
- Mathematics & Statistics
- Physics

## 4. Alternative Work Experience
Employers frequently pair degree requirements with practical work experience alternatives:
- Example: *"Bachelor's degree in Computer Science or equivalent practical experience."*
  - Extracted: `degree_level = DegreeLevel.BACHELOR`, `alternative_experience_years = 4.0`.
- Explicit duration alternatives:
  - Example: *"Master's degree or 6 years of equivalent industry experience."*
  - Extracted: `degree_level = DegreeLevel.MASTER`, `alternative_experience_years = 6.0`.
