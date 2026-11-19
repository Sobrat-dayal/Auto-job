# Job Skill Taxonomy & Normalization (Stage 28)

## 1. Overview
The Skill Taxonomy maps diverse employer phrasings, acronyms, and aliases into canonical skill representations aligned with Stage 21 (Applicant Verified Skills).

## 2. Categorization Hierarchy
1. `PROGRAMMING_LANGUAGE`: Python, JavaScript, TypeScript, Go, Rust, Java, C++, C#, SQL.
2. `FRAMEWORK_LIBRARY`: React, Node.js, Next.js, FastAPI, Django, Flask, Spring Boot.
3. `DATABASE`: PostgreSQL, MySQL, MongoDB, Redis, Cassandra, DynamoDB.
4. `CLOUD_DEVOPS`: AWS, Google Cloud (GCP), Azure, Docker, Kubernetes, Terraform, CI/CD.
5. `AI_ML`: Machine Learning, PyTorch, TensorFlow, Deep Learning, NLP, LLMs.
6. `TOOLS_PLATFORMS`: REST APIs, GraphQL, Linux, Git.
7. `METHODOLOGY`: Agile, Scrum, Kanban, Microservices, System Architecture.
8. `NON_TECHNICAL`: Leadership, Communication, Problem Solving.

## 3. Alias Normalization Mapping
| Employer Mention | Canonical Display Name | Normalized Key | Category |
|---|---|---|---|
| "golang", "Go programming" | Go | `go` | `PROGRAMMING_LANGUAGE` |
| "py", "Python 3" | Python | `python` | `PROGRAMMING_LANGUAGE` |
| "k8s" | Kubernetes | `kubernetes` | `CLOUD_DEVOPS` |
| "postgres", "psql" | PostgreSQL | `postgresql` | `DATABASE` |
| "react.js", "reactjs" | React | `react` | `FRAMEWORK_LIBRARY` |
| "fast api" | FastAPI | `fastapi` | `FRAMEWORK_LIBRARY` |
| "gcp", "google cloud platform" | Google Cloud | `gcp` | `CLOUD_DEVOPS` |
| "amazon web services" | AWS | `aws` | `CLOUD_DEVOPS` |
| "continuous integration", "github actions" | CI/CD | `cicd` | `CLOUD_DEVOPS` |

## 4. Experience Bound Extraction
If an employer specifies "5+ years of experience with Python" or "3-5 years PostgreSQL", the extractor parses the numeric bound and binds it directly to the normalized skill.
