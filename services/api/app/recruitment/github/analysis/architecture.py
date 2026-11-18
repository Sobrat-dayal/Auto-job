"""Repository Architecture and Project Layout Analysis (Stage 22)."""

from __future__ import annotations

import logging

from app.recruitment.github.contracts import (
    ArchitectureType,
    DetectionConfidence,
    RepositoryArchitecture,
    SourceTreeEntry,
    TechCategory,
    TechnologyFinding,
)

logger = logging.getLogger("autonom.recruitment.github.analysis.architecture")


class ArchitectureAnalyzer:
    """Infers structural codebase design, entrypoints, and DevOps configurations."""

    @classmethod
    def analyze_layout(
        cls, repo_id: str, entries: list[SourceTreeEntry]
    ) -> tuple[RepositoryArchitecture, list[TechnologyFinding]]:
        paths = [e.path.lower() for e in entries]
        additional_findings: list[TechnologyFinding] = []

        has_frontend = any(
            p.startswith("frontend/") or p.startswith("client/") or p.startswith("ui/")
            or "react" in p or "app.tsx" in p or "main.tsx" in p or "index.html" in p
            for p in paths
        )
        has_backend = any(
            p.startswith("backend/") or p.startswith("server/") or p.startswith("api/")
            or "main.py" in p or "app.py" in p or "server.js" in p or "main.go" in p or "main.rs" in p
            for p in paths
        )
        has_tests = any("test" in p or "spec" in p for p in paths)
        has_ci = any(p.startswith(".github/workflows/") or ".gitlab-ci.yml" in p for p in paths)
        has_docker = any("dockerfile" in p or "docker-compose" in p for p in paths)
        has_docs = any("readme" in p or "docs/" in p for p in paths)
        is_monorepo = any(p.startswith("packages/") or p.startswith("apps/") or "pnpm-workspace.yaml" in p for p in paths)

        # Detect Docker
        if has_docker:
            additional_findings.append(
                TechnologyFinding(
                    repo_id=repo_id,
                    technology_name="Docker",
                    canonical_name="docker",
                    category=TechCategory.CONTAINERIZATION,
                    confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                    evidence_type="config_file",
                    source_file="Dockerfile",
                    source_excerpt="Container configuration detected",
                )
            )

        # Detect GitHub Actions
        if has_ci:
            ci_file = next((p for p in paths if p.startswith(".github/workflows/")), ".github/workflows")
            additional_findings.append(
                TechnologyFinding(
                    repo_id=repo_id,
                    technology_name="GitHub Actions",
                    canonical_name="github-actions",
                    category=TechCategory.CI_CD,
                    confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                    evidence_type="config_file",
                    source_file=ci_file,
                    source_excerpt="CI/CD automated pipeline workflows",
                )
            )

        # Determine architecture classification
        if is_monorepo:
            arch_type = ArchitectureType.MONOREPO
            summary = "Multi-package workspace monorepo layout"
        elif has_frontend and has_backend:
            arch_type = ArchitectureType.FULLSTACK_APPLICATION
            summary = "Full-stack application with distinct client and server modules"
        elif has_backend and not has_frontend:
            arch_type = ArchitectureType.BACKEND_API
            summary = "Backend API service / microservice architecture"
        elif has_frontend and not has_backend:
            arch_type = ArchitectureType.FRONTEND_ONLY
            summary = "Client-side frontend user interface architecture"
        elif any("cli" in p for p in paths):
            arch_type = ArchitectureType.CLI_TOOL
            summary = "Command-line utility application"
        else:
            arch_type = ArchitectureType.LIBRARY_PACKAGE
            summary = "Modular library / software component package"

        # Identify candidate entrypoints
        entrypoints = [
            e.path
            for e in entries
            if e.path.lower().endswith(
                ("main.py", "app.py", "server.js", "main.rs", "main.go", "index.ts", "index.js", "main.tsx")
            )
        ]

        # Identify top-level key directories
        key_dirs = sorted(list({e.path.split("/")[0] for e in entries if "/" in e.path}))[:8]

        arch = RepositoryArchitecture(
            repo_id=repo_id,
            architecture_type=arch_type,
            has_frontend=has_frontend,
            has_backend=has_backend,
            has_tests=has_tests,
            has_ci=has_ci,
            has_docker=has_docker,
            has_docs=has_docs,
            structure_summary=summary,
            entrypoints=entrypoints,
            key_directories=key_dirs,
        )

        return arch, additional_findings
