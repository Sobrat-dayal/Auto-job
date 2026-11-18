"""Source Code Filtering and Exclusion Rules (Stage 22)."""

from __future__ import annotations

from pathlib import Path

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500 KB per source file limit
MAX_SAMPLED_FILES = 60  # Maximum representative files to fetch per repository

IGNORED_DIRECTORIES = {
    "node_modules",
    "venv",
    ".venv",
    "target",
    "dist",
    "build",
    "bin",
    "obj",
    ".git",
    "vendor",
    "__pycache__",
    ".idea",
    ".vscode",
    "Pods",
    ".terraform",
    ".next",
    ".nuget",
}

BINARY_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".wasm",
    ".pyc",
    ".class",
    ".jar",
    ".war",
    ".bin",
    ".woff",
    ".woff2",
    ".ttf",
    ".mp4",
    ".mp3",
}

MANIFEST_FILENAMES = {
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "README.md",
    "README.txt",
}


class SourceFilter:
    """Enforces safety, size bounds, and ignores binaries and vendor code."""

    @classmethod
    def should_ignore_path(cls, path: str) -> bool:
        parts = Path(path).parts
        for part in parts:
            if part.lower() in IGNORED_DIRECTORIES:
                return True
        ext = Path(path).suffix.lower()
        if ext in BINARY_EXTENSIONS:
            return True
        # Generated minified bundles
        name = Path(path).name.lower()
        if name.endswith(".min.js") or name.endswith(".min.css") or name.endswith(".bundle.js"):
            return True
        return False

    @classmethod
    def is_manifest_file(cls, path: str) -> bool:
        name = Path(path).name.lower()
        return name in MANIFEST_FILENAMES or path.startswith(".github/workflows/")

    @classmethod
    def is_safe_relative_path(cls, path: str) -> bool:
        if not path or path.startswith("/") or path.startswith("\\"):
            return False
        parts = Path(path).parts
        if ".." in parts:
            return False
        return True

    @classmethod
    def should_inspect_file(cls, path: str, size_bytes: int = 0) -> bool:
        if size_bytes > MAX_FILE_SIZE_BYTES:
            return False
        if not cls.is_safe_relative_path(path):
            return False
        return not cls.should_ignore_path(path)
