"""Technology families and related skill evaluation for Stage 29 Matching Engine."""

from __future__ import annotations

from app.recruitment.matching.qualifications.aliases import normalize_skill

# Technology family groupings
TECHNOLOGY_FAMILIES: dict[str, set[str]] = {
    "python_backend_frameworks": {
        "django", "fastapi", "flask", "tornado", "pyramid", "aiohttp"
    },
    "relational_databases": {
        "postgresql", "mysql", "mariadb", "sqlite", "oracle", "sql server", "microsoft sql server"
    },
    "nosql_databases": {
        "mongodb", "couchbase", "cassandra", "dynamodb", "redis", "elasticsearch"
    },
    "frontend_spa_frameworks": {
        "react", "vue", "angular", "svelte", "solidjs"
    },
    "cloud_providers": {
        "amazon web services", "google cloud platform", "microsoft azure", "azure"
    },
    "container_orchestration": {
        "kubernetes", "docker swarm", "openshift", "nomad", "ecs"
    },
    "deep_learning_frameworks": {
        "pytorch", "tensorflow", "keras", "jax", "mxnet"
    },
    "iac_tools": {
        "terraform", "pulumi", "cloudformation", "ansible"
    },
}


def get_technology_family(skill: str) -> str | None:
    """Returns the recognized technology family for a skill if categorized."""
    norm = normalize_skill(skill)
    for family, members in TECHNOLOGY_FAMILIES.items():
        if norm in members:
            return family
    return None


def are_related_technologies(skill_a: str, skill_b: str) -> tuple[bool, str | None]:
    """Determines if two distinct technologies belong to the same functional family.
    
    Returns (is_related, family_name).
    """
    fam_a = get_technology_family(skill_a)
    fam_b = get_technology_family(skill_b)

    if fam_a and fam_b and fam_a == fam_b:
        return True, fam_a
    return False, None
