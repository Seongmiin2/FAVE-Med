from __future__ import annotations

import ast
import csv

from ...core.schemas import BenchmarkItem, FormulaSpec, GoldAnswer, MedicalBenchmarkRecord, MedicalGoldAnnotation, MedicalRuntimeQuestion
from ..telecom.adapter import extract_requested_output_from_question


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


CALCULATOR_IDS = {
    "body mass index": "body_mass_index", "mean arterial pressure": "mean_arterial_pressure",
    "anion gap": "anion_gap", "creatinine clearance": "cockcroft_gault", "cockcroft": "cockcroft_gault",
    "corrected calcium": "corrected_calcium", "body surface area": "body_surface_area_mosteller",
    "serum osmolality": "serum_osmolality", "fractional excretion of sodium": "fractional_excretion_sodium",
    "qtc": "qtc_bazett", "meld": "meld_na",
}


def calculator_id(name: str) -> str:
    lowered = name.lower()
    return next((value for marker, value in CALCULATOR_IDS.items() if marker in lowered), "unknown")


def convert_demomed_record(row: dict) -> MedicalBenchmarkRecord:
    entities = row.get("relevant_entities", "")
    try:
        entities = ast.literal_eval(entities) if isinstance(entities, str) and entities else {}
    except (ValueError, SyntaxError):
        entities = {"raw": entities}
    runtime = MedicalRuntimeQuestion(
        id=str(row["id"]), patient_note=row.get("patient_note", ""), question=row.get("question", ""),
        requested_output=extract_requested_output_from_question(row.get("question", "")),
        metadata={"source_id": str(row["id"])},
    )
    gold = MedicalGoldAnnotation(
        answer=normalize_medical_answer(row), calculator_id=calculator_id(row.get("calculator_name", "")),
        required_entities=entities if isinstance(entities, dict) else {},
        tolerance={"lower_limit": _value(row.get("lower_limit")), "upper_limit": _value(row.get("upper_limit"))},
    )
    return MedicalBenchmarkRecord(source={"dataset": row.get("source_dataset", "legacy_medical_pilot"), "source_id": str(row["id"]), "status": "compatibility_only"}, runtime=runtime, gold=gold)


def load_medical_records(path: str) -> list[MedicalBenchmarkRecord]:
    with open(path, newline="", encoding="utf-8-sig") as stream:
        return [convert_demomed_record(row) for row in csv.DictReader(stream)]
