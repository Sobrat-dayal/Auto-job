# Stage 22: Repository Intelligence & Architecture Analysis

## 1. Architectural Classification

The `ArchitectureAnalyzer` examines repository directory layouts, dependency manifests, and entrypoint files to determine the software architecture archetype:

| Architecture Type | Identification Heuristics |
| :--- | :--- |
| **`MONOREPO`** | Presence of `pnpm-workspace.yaml`, `lerna.json`, `packages/`, `apps/`, or multiple distinct root project manifests. |
| **`MICROSERVICE`** | Compact backend footprint with Dockerfile, Protobuf/gRPC definitions, or Kubernetes manifests. |
| **`BACKEND_SERVICE`** | Presence of FastAPI, Express, Django, Spring Boot, or Gin with database models and API routers. |
| **`FRONTEND_SPA`** | Single-page application structures (React, Vue, Next.js, Angular, Svelte) with public assets and component directories. |
| **`FULLSTACK`** | Combined backend API and frontend client in the same repository (e.g., `client/` and `server/` or Next.js App Router). |
| **`CLI_TOOL`** | Binary entrypoint with argument parsers (`click`, `argparse`, `clap`, `cobra`) and console scripts in manifest. |
| **`LIBRARY`** | Reusable package structures with setup configurations, public exported interfaces, and unit test suites. |

---

## 2. Engineering Quality Indicators

AUTONOM extracts concrete indicators of software craftsmanship and professional software development practices:

1. **Automated Testing Suite (`has_tests`)**:
   - Searches for standard test directories (`tests/`, `__tests__/`, `spec/`) and test runners (`pytest`, `vitest`, `jest`, `cargo test`, `go test`).
2. **Continuous Integration & Delivery (`has_ci`)**:
   - Detects workflow files in `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, or `azure-pipelines.yml`.
3. **Containerization & Deployment (`has_docker`)**:
   - Evaluates `Dockerfile`, `docker-compose.yml`, or Helm charts.
4. **Documentation Health**:
   - Analyzes presence, length, and structured sections in `README.md`, `CONTRIBUTING.md`, and license files.
5. **Entrypoint Resolution**:
   - Identifies the principal entrypoint file (`src/main.rs`, `apps/desktop/src/main.tsx`, `services/api/app/main.py`) to anchor portfolio analysis in verified code roots.
