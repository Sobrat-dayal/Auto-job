"""Safe Dependency Manifest Parsers (Stage 22)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.recruitment.github.contracts import DetectionConfidence, TechCategory, TechnologyFinding

logger = logging.getLogger("autonom.recruitment.github.analysis.dependencies")

PIP_LINE_REGEX = re.compile(r"^([a-zA-Z0-9_\-]+)\s*(?:([><=~!^]+.*))?$")


class DependencyManifestParser:
    """Parses standard ecosystem manifest files into structured TechnologyFinding objects."""

    @classmethod
    def parse_manifest(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        filename = path.split("/")[-1].lower()
        findings: list[TechnologyFinding] = []

        try:
            if filename == "package.json":
                findings.extend(cls._parse_package_json(repo_id, path, content))
            elif filename in ("requirements.txt", "requirements-dev.txt"):
                findings.extend(cls._parse_requirements_txt(repo_id, path, content))
            elif filename == "pyproject.toml":
                findings.extend(cls._parse_pyproject_toml(repo_id, path, content))
            elif filename == "cargo.toml":
                findings.extend(cls._parse_cargo_toml(repo_id, path, content))
            elif filename == "go.mod":
                findings.extend(cls._parse_go_mod(repo_id, path, content))
        except Exception as exc:
            logger.warning(f"Error parsing manifest '{path}': {exc}")

        return findings

    @classmethod
    def _parse_package_json(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        findings: list[TechnologyFinding] = []
        data = json.loads(content)
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})

        for pkg, ver in deps.items():
            findings.append(
                TechnologyFinding(
                    repo_id=repo_id,
                    technology_name=pkg,
                    canonical_name=pkg.lower().strip(),
                    category=TechCategory.LIBRARY,
                    confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                    evidence_type="manifest_dependency",
                    source_file=path,
                    source_excerpt=f'"{pkg}": "{ver}"',
                    version_spec=str(ver),
                    is_dev_dependency=False,
                )
            )

        for pkg, ver in dev_deps.items():
            findings.append(
                TechnologyFinding(
                    repo_id=repo_id,
                    technology_name=pkg,
                    canonical_name=pkg.lower().strip(),
                    category=TechCategory.TESTING if any(t in pkg for t in ["jest", "vitest", "test", "mocha", "playwright"]) else TechCategory.BUILD_TOOL,
                    confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                    evidence_type="manifest_dependency",
                    source_file=path,
                    source_excerpt=f'"{pkg}": "{ver}"',
                    version_spec=str(ver),
                    is_dev_dependency=True,
                )
            )
        return findings

    @classmethod
    def _parse_requirements_txt(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        findings: list[TechnologyFinding] = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            match = PIP_LINE_REGEX.match(line)
            if match:
                pkg_name = match.group(1)
                raw_ver = match.group(2) or None
                ver_clean = None
                if raw_ver:
                    raw_ver = raw_ver.strip()
                    ver_clean = raw_ver.lstrip("=~><!^ ").strip()
                findings.append(
                    TechnologyFinding(
                        repo_id=repo_id,
                        technology_name=pkg_name,
                        canonical_name=pkg_name.lower().replace("_", "-").strip(),
                        category=TechCategory.LIBRARY,
                        confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                        evidence_type="manifest_dependency",
                        source_file=path,
                        source_excerpt=line,
                        version_spec=raw_ver,
                        version=ver_clean or raw_ver,
                    )
                )
        return findings

    @classmethod
    def _parse_pyproject_toml(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        findings: list[TechnologyFinding] = []
        in_deps_section = False
        for line in content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if ("dependencies" in line_str.lower() and "[" in line_str) or ("dependencies" in line_str.lower() and "=" in line_str):
                in_deps_section = True
                continue
            if in_deps_section and line_str.startswith("[") and "dependencies" not in line_str.lower():
                in_deps_section = False
            if in_deps_section:
                if "=" in line_str:
                    pkg = line_str.split("=")[0].strip().strip('"\',')
                    ver = line_str.split("=")[1].strip().strip('"\',')
                    if pkg and pkg != "python":
                        findings.append(
                            TechnologyFinding(
                                repo_id=repo_id,
                                technology_name=pkg,
                                canonical_name=pkg.lower().replace("_", "-").strip(),
                                category=TechCategory.LIBRARY,
                                confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                                evidence_type="manifest_dependency",
                                source_file=path,
                                source_excerpt=line_str,
                                version_spec=ver,
                            )
                        )
                elif '"' in line_str or "'" in line_str:
                    cleaned = line_str.strip('",\' []')
                    if cleaned:
                        match = PIP_LINE_REGEX.match(cleaned)
                        if match:
                            pkg = match.group(1)
                            findings.append(
                                TechnologyFinding(
                                    repo_id=repo_id,
                                    technology_name=pkg,
                                    canonical_name=pkg.lower().replace("_", "-").strip(),
                                    category=TechCategory.LIBRARY,
                                    confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                                    evidence_type="manifest_dependency",
                                    source_file=path,
                                    source_excerpt=line_str,
                                )
                            )
        return findings

    @classmethod
    def _parse_cargo_toml(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        findings: list[TechnologyFinding] = []
        in_deps = False
        for line in content.splitlines():
            s = line.strip()
            if s in ("[dependencies]", "[dev-dependencies]"):
                in_deps = True
                continue
            elif s.startswith("[") and in_deps:
                in_deps = False
            if in_deps and "=" in s and not s.startswith("#"):
                pkg = s.split("=")[0].strip()
                ver = s.split("=")[1].strip()
                findings.append(
                    TechnologyFinding(
                        repo_id=repo_id,
                        technology_name=pkg,
                        canonical_name=pkg.lower().replace("_", "-").strip(),
                        category=TechCategory.LIBRARY,
                        confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                        evidence_type="manifest_dependency",
                        source_file=path,
                        source_excerpt=s,
                        version_spec=ver,
                    )
                )
        return findings

    @classmethod
    def _parse_go_mod(cls, repo_id: str, path: str, content: str) -> list[TechnologyFinding]:
        findings: list[TechnologyFinding] = []
        in_require = False
        for line in content.splitlines():
            s = line.strip()
            if s.startswith("require ("):
                in_require = True
                continue
            elif s == ")" and in_require:
                in_require = False
            if (in_require or s.startswith("require ")) and not s.startswith("//"):
                parts = s.replace("require", "").strip().split()
                if len(parts) >= 1:
                    module_name = parts[0]
                    short_name = module_name.split("/")[-1]
                    ver = parts[1] if len(parts) > 1 else None
                    findings.append(
                        TechnologyFinding(
                            repo_id=repo_id,
                            technology_name=module_name,
                            name=module_name,
                            canonical_name=module_name.lower().strip(),
                            category=TechCategory.LIBRARY,
                            confidence=DetectionConfidence.STRONGLY_SUPPORTED,
                            evidence_type="manifest_dependency",
                            source_file=path,
                            source_excerpt=s,
                            version_spec=ver,
                            version=ver,
                        )
                    )
        return findings
