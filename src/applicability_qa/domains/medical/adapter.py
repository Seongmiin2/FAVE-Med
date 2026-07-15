from __future__ import annotations

import ast
import csv

from ...core.schemas import BenchmarkItem, FormulaSpec, GoldAnswer


def _value(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def normalize_medical_answer(row: dict) -> GoldAnswer:
    kind = str(row.get("output_type", "decimal")).lower()
    output_type = kind if kind in {"decimal", "integer", "date", "categorical"} else "decimal"
    return GoldAnswer(value=_value(row.get("ground_truth_answer")), output_type=output_type)


def load_formula_metadata(row: dict) -> FormulaSpec | None:
    name = row.get("calculator_name")
    return FormulaSpec(id=name) if name else None


def convert_demomed_row(row: dict) -> BenchmarkItem:
    entities = row.get("relevant_entities", "")
    try:
        entities = ast.literal_eval(entities) if isinstance(entities, str) and entities else {}
    except (ValueError, SyntaxError):
        entities = {"raw": entities}
    return BenchmarkItem(id=str(row["id"]), domain="medical", task_type="clinical_calculation", question=row.get("question") or row.get("patient_note", ""), gold_answer=normalize_medical_answer(row), formula=load_formula_metadata(row), required_variables=entities if isinstance(entities, dict) else {"entities": entities}, metadata={"patient_note": row.get("patient_note", ""), "calculator_name": row.get("calculator_name", ""), "lower_limit": row.get("lower_limit"), "upper_limit": row.get("upper_limit")})


def load_medical_items(path: str) -> list[BenchmarkItem]:
    with open(path, newline="", encoding="utf-8-sig") as stream:
        return [convert_demomed_row(row) for row in csv.DictReader(stream)]
