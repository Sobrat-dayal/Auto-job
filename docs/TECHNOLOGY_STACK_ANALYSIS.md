# Stage 22: Technology Stack Analysis & Manifest Parsing

## 1. Supported Ecosystems & Parsers

AUTONOM features static parsers for the primary software ecosystems. All parsers operate safely in-memory without executing build scripts, downloading external packages, or running subprocesses.

```
Manifest Files
  ├── Python: requirements.txt, pyproject.toml
  ├── JavaScript / TypeScript: package.json
  ├── Rust: Cargo.toml
  └── Go: go.mod
         │
         v
DependencyManifestParser (AST / JSON / TOML / Regex Parsing)
         │
         v
Raw Dependencies [name, version_spec, is_dev]
         │
         v
TechnologyClassifier (Taxonomy Resolution)
         │
         v
TechnologyFinding [canonical_name, category, confidence, excerpt]
```

### 1.1 Python (`requirements.txt`, `pyproject.toml`)
- **`requirements.txt`**: Evaluates pip requirement lines, separating package names, environment markers, and version specifiers (`==`, `>=`, `<=`, `~=`).
- **`pyproject.toml`**: Evaluates PEP 621 `[project.dependencies]` and Poetry `[tool.poetry.dependencies]`, extracting framework dependencies while ignoring the runtime python version.

### 1.2 Node.js & TypeScript (`package.json`)
- Evaluates `dependencies` (production runtime libraries) and `devDependencies` (build tools, testing frameworks, linters).
- Extracts semantic version ranges (`^18.3.1`, `~5.0.0`).

### 1.3 Rust (`Cargo.toml`)
- Evaluates `[dependencies]` and `[dev-dependencies]`.
- Handles both string version specs (`serde = "1.0"`) and inline table definitions (`tokio = { version = "1.38", features = ["full"] }`).

### 1.4 Go (`go.mod`)
- Parses single-line and block `require (...)` declarations.
- Normalizes module paths (e.g., `github.com/gin-gonic/gin v1.9.1` -> short name `gin`, canonical `gin`).

---

## 2. Canonical Technology Taxonomy

The `TechnologyClassifier` resolves raw package names against a standardized taxonomy, preventing fragmentation (e.g., mapping `torch` and `pytorch` to `PyTorch`, `psycopg2` and `asyncpg` to `PostgreSQL`).

### Classification Categories:
- **`LANGUAGE`**: Python, TypeScript, JavaScript, Rust, Go, SQL, HTML/CSS.
- **`FRAMEWORK`**: FastAPI, React, Next.js, Django, Flask, Express, NestJS, Spring Boot, Gin, Actix Web, Vue, Tailwind CSS.
- **`DATABASE`**: PostgreSQL, MySQL, Redis, MongoDB, SQLite.
- **`ORM`**: SQLAlchemy, Prisma, TypeORM, Tortoise ORM, Diesel.
- **`TESTING`**: PyTest, Vitest, Jest, Playwright, Cypress, Mocha.
- **`AI_ML`**: PyTorch, TensorFlow, Hugging Face Transformers, Scikit-Learn, LangChain, OpenAI SDK.
- **`CONTAINERIZATION`**: Docker, Kubernetes.
- **`BUILD_TOOL`**: Vite, Webpack, Cargo, Turborepo, Pnpm.
- **`LIBRARY`**: General utilities and supporting modules.
- **`OTHER`**: Unclassified dependencies.

Each finding retains an exact `source_excerpt` (e.g., `"fastapi": "^0.115.0"`) and `source_file` reference for evidence provenance.
