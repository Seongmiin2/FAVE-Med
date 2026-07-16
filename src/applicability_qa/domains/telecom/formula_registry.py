from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path(__file__).resolve().parents[4] / "data" / "telecom" / "formulas" / "formula_registry.json"


def load_formula_registry(path: str | Path = DEFAULT_REGISTRY) -> list[dict[str, Any]]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = [row["formula_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Formula registry IDs must be unique")
    return rows


def formula_by_id(formula_id: str, registry: list[dict]) -> dict | None:
    return next((row for row in registry if row["formula_id"] == formula_id), None)
