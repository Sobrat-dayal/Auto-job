"""Unit tests for Stage 22 source code analysis, manifest parsers, and architecture evaluation."""

import pytest
from app.recruitment.github.analysis.architecture import ArchitectureAnalyzer
from app.recruitment.github.analysis.dependencies import DependencyManifestParser
from app.recruitment.github.analysis.frameworks import TechnologyClassifier
from app.recruitment.github.contracts import (
    ArchitectureType,
    DetectionConfidence,
    SourceTreeEntry,
    TechCategory,
    TechnologyFinding,
)


def test_parse_package_json():
    content = """{
      "name": "autonom-frontend",
      "dependencies": {
        "react": "^18.3.1",
        "react-dom": "^18.3.1",
        "@tanstack/react-query": "^5.0.0",
        "tailwindcss": "^3.4.0"
      },
      "devDependencies": {
        "vitest": "^2.1.0",
        "typescript": "^5.5.0"
      }
    }"""
    findings = DependencyManifestParser.parse_manifest("repo_1", "package.json", content)
    names = {f.name for f in findings}
    assert "react" in names
    assert "@tanstack/react-query" in names
    assert "vitest" in names
    assert "typescript" in names

    react_f = next(f for f in findings if f.name == "react")
    assert react_f.version == "^18.3.1"


def test_parse_requirements_txt():
    content = """
    # Core dependencies
    fastapi==0.115.0
    uvicorn[standard]>=0.30.0
    sqlalchemy>=2.0.0
    psycopg2-binary==2.9.9
    pytest>=8.0.0
    """
    findings = DependencyManifestParser.parse_manifest("repo_1", "requirements.txt", content)
    names = {f.name for f in findings}
    assert "fastapi" in names
    assert "sqlalchemy" in names
    assert "psycopg2-binary" in names

    fastapi_f = next(f for f in findings if f.name == "fastapi")
    assert fastapi_f.version == "0.115.0"


def test_parse_pyproject_toml():
    content = """
    [tool.poetry.dependencies]
    python = "^3.12"
    torch = "2.3.0"
    transformers = "4.41.0"
    pydantic = "^2.8.0"
    """
    findings = DependencyManifestParser.parse_manifest("repo_1", "pyproject.toml", content)
    names = {f.name for f in findings}
    assert "torch" in names
    assert "transformers" in names
    assert "pydantic" in names


def test_parse_cargo_toml():
    content = """
    [package]
    name = "autonom-desktop-core"
    version = "0.1.0"

    [dependencies]
    tokio = { version = "1.38", features = ["full"] }
    serde = { version = "1.0", features = ["derive"] }
    tauri = "2.0"
    """
    findings = DependencyManifestParser.parse_manifest("repo_1", "Cargo.toml", content)
    names = {f.name for f in findings}
    assert "tokio" in names
    assert "serde" in names
    assert "tauri" in names


def test_parse_go_mod():
    content = """
    module github.com/octocat/worker

    go 1.22

    require (
        github.com/gin-gonic/gin v1.9.1
        github.com/stretchr/testify v1.8.4
    )
    """
    findings = DependencyManifestParser.parse_manifest("repo_1", "go.mod", content)
    names = {f.name for f in findings}
    assert "github.com/gin-gonic/gin" in names
    assert "github.com/stretchr/testify" in names


def test_technology_classifier():
    raw_findings = [
        TechnologyFinding(name="fastapi", category=TechCategory.OTHER, confidence=DetectionConfidence.DETECTED, evidence_source="test", repo_id="r1"),
        TechnologyFinding(name="react", category=TechCategory.OTHER, confidence=DetectionConfidence.DETECTED, evidence_source="test", repo_id="r1"),
        TechnologyFinding(name="postgresql", category=TechCategory.OTHER, confidence=DetectionConfidence.DETECTED, evidence_source="test", repo_id="r1"),
        TechnologyFinding(name="torch", category=TechCategory.OTHER, confidence=DetectionConfidence.DETECTED, evidence_source="test", repo_id="r1"),
        TechnologyFinding(name="docker", category=TechCategory.OTHER, confidence=DetectionConfidence.DETECTED, evidence_source="test", repo_id="r1"),
    ]
    classified = TechnologyClassifier.classify_findings(raw_findings)
    categories_by_name = {f.name: f.category for f in classified}

    assert categories_by_name["FastAPI"] == TechCategory.FRAMEWORK
    assert categories_by_name["React"] == TechCategory.FRAMEWORK
    assert categories_by_name["PostgreSQL"] == TechCategory.DATABASE
    assert categories_by_name["PyTorch"] == TechCategory.AI_ML
    assert categories_by_name["Docker"] == TechCategory.CONTAINERIZATION


def test_architecture_analyzer():
    entries = [
        SourceTreeEntry(path="Dockerfile", mode="100644", type="blob", sha="sha1"),
        SourceTreeEntry(path=".github/workflows/ci.yml", mode="100644", type="blob", sha="sha2"),
        SourceTreeEntry(path="tests/test_api.py", mode="100644", type="blob", sha="sha3"),
        SourceTreeEntry(path="src/main.py", mode="100644", type="blob", sha="sha4"),
        SourceTreeEntry(path="pyproject.toml", mode="100644", type="blob", sha="sha5"),
    ]
    arch, findings = ArchitectureAnalyzer.analyze_layout("repo_test", entries)

    assert arch.has_docker is True
    assert arch.has_ci is True
    assert arch.has_tests is True
    assert "src/main.py" in arch.entrypoints
    assert arch.architecture_type == ArchitectureType.BACKEND_API
