from __future__ import annotations

import json
from pathlib import Path

from ...core.schemas import MedicalCalculatorSpec

DEFAULT_REGISTRY = Path(__file__).resolve().parents[4] / "data" / "medical" / "calculators" / "calculator_registry.json"


def load_calculator_registry(path: str | Path = DEFAULT_REGISTRY) -> list[MedicalCalculatorSpec]:
    registry = [MedicalCalculatorSpec.model_validate(row) for row in json.loads(Path(path).read_text(encoding="utf-8"))]
    ids = [row.calculator_id for row in registry]
    if len(ids) != len(set(ids)):
        raise ValueError("Calculator registry IDs must be unique")
    return registry


def calculator_by_id(calculator_id: str, registry: list[MedicalCalculatorSpec]) -> MedicalCalculatorSpec | None:
    return next((row for row in registry if row.calculator_id == calculator_id), None)
