"""Employment Type Normalization & Compatibility Engine (Stage 27)."""

from typing import Optional


EMPLOYMENT_TYPE_MAP = {
    "full_time": "full_time",
    "full-time": "full_time",
    "full time": "full_time",
    "permanent": "full_time",
    "part_time": "part_time",
    "part-time": "part_time",
    "part time": "part_time",
    "contract": "contract",
    "contractor": "contract",
    "temp": "contract",
    "temporary": "contract",
    "internship": "internship",
    "intern": "internship",
    "co-op": "internship",
    "coop": "internship",
    "apprentice": "apprenticeship",
    "apprenticeship": "apprenticeship",
}


def normalize_employment_type(raw_type: Optional[str]) -> Optional[str]:
    """Map raw employment type string to canonical type."""
    if not raw_type:
        return None
    cleaned = raw_type.lower().strip()
    return EMPLOYMENT_TYPE_MAP.get(cleaned, cleaned)


def are_employment_types_compatible(type_a: Optional[str], type_b: Optional[str]) -> bool:
    """Verify whether two employment types are compatible.

    Crucial rule: An internship or apprenticeship CANNOT be merged with a full-time role!
    """
    norm_a = normalize_employment_type(type_a)
    norm_b = normalize_employment_type(type_b)

    if not norm_a or not norm_b:
        return True

    if norm_a == norm_b:
        return True

    # Strict separation: internship vs anything else
    if norm_a == "internship" or norm_b == "internship":
        return False

    # Strict separation: contract vs full_time
    if (norm_a == "contract" and norm_b == "full_time") or (norm_a == "full_time" and norm_b == "contract"):
        return False

    return False
