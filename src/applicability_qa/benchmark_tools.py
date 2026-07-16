from __future__ import annotations

from copy import deepcopy
from typing import Any


def make_minimal_pair(row: dict[str, Any], pair_id: str, mutation: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create an offline authoring pair while keeping gold out of runtime fields."""
    control, contrast = deepcopy(row), deepcopy(row)
    for item, role in ((control, "control"), (contrast, "contrast")):
        item.setdefault("runtime", {}).setdefault("metadata", {}).update(pair_id=pair_id, pair_role=role)
    contrast["runtime"].update(mutation.get("runtime", {}))
    contrast["gold"].update(mutation.get("gold", {}))
    return control, contrast


def assign_difficulty(row: dict[str, Any]) -> str:
    gold = row.get("gold", {})
    rejected = sum(item.get("label") == "rejected" for item in gold.get("evidence_annotations", []))
    conditions = len(gold.get("applicability_conditions", [])) + len(row.get("runtime", {}).get("metadata", {}).get("required_conditions", []))
    score = rejected + conditions + int(bool(gold.get("trap_answers")))
    return "hard" if score >= 3 else "medium" if score >= 1 else "easy"


def benchmark_track(row: dict[str, Any]) -> str:
    metadata = row.get("runtime", {}).get("metadata", {})
    if metadata.get("cross_domain"):
        return "cross_domain"
    if metadata.get("holdout"):
        return "holdout"
    return "in_domain"
