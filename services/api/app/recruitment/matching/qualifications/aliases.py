"""Verified skill alias mapping and normalization for Stage 29 Matching Engine."""

from __future__ import annotations

import re

# Exact canonical equivalence mappings
CANONICAL_ALIASES: dict[str, str] = {
    "postgres": "postgresql",
    "pgsql": "postgresql",
    "postgresql": "postgresql",
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "python3": "python",
    "python 3": "python",
    "golang": "go",
    "go lang": "go",
    "go": "go",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "google cloud platform": "google cloud platform",
    "reactjs": "react",
    "react.js": "react",
    "react": "react",
    "nextjs": "next.js",
    "next.js": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "vue": "vue",
    "nodejs": "node.js",
    "node.js": "node.js",
    "node": "node.js",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "tf": "terraform",
    "terraform": "terraform",
    "docker": "docker",
    "sql": "sql",
}

# Strict non-aliases: pairs that must NEVER be treated as equivalent
FORBIDDEN_ALIAS_PAIRS: set[frozenset[str]] = {
    frozenset(["java", "javascript"]),
    frozenset(["react", "react native"]),
    frozenset(["docker", "kubernetes"]),
    frozenset(["sql", "postgresql"]),
    frozenset(["sql", "mysql"]),
    frozenset(["tensorflow", "pytorch"]),
    frozenset(["c", "c++"]),
    frozenset(["c++", "c#"]),
    frozenset(["c", "c#"]),
}


def normalize_skill(name: str) -> str:
    """Normalizes skill text into a canonical lowercase identifier."""
    if not name:
        return ""
    clean = re.sub(r"[^\w\s\.\+#]", "", name).strip().lower()
    return CANONICAL_ALIASES.get(clean, clean)


def are_aliases(skill_a: str, skill_b: str) -> bool:
    """Checks whether two skills are verified aliases, respecting negative guards."""
    norm_a = normalize_skill(skill_a)
    norm_b = normalize_skill(skill_b)

    if not norm_a or not norm_b:
        return False

    # Check forbidden pairs
    if frozenset([norm_a, norm_b]) in FORBIDDEN_ALIAS_PAIRS:
        return False

    return norm_a == norm_b
