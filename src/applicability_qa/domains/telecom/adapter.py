from __future__ import annotations

from ...core.jsonl_utils import read_jsonl
from ...core.schemas import BenchmarkItem, EvidenceItem, FormulaSpec, GoldAnswer


def normalize_telecom_answer(row: dict) -> GoldAnswer:
    return GoldAnswer(value=row["gold_value"], unit=row.get("gold_unit"), output_type="telecom_quantity")


def normalize_telecom_evidence(row: dict) -> list[EvidenceItem]:
    result = []
    for source, label in (("valid_evidence", "valid"), ("invalid_evidence", "invalid"), ("contested_evidence", "unknown")):
        result.extend(EvidenceItem(id=item["id"], text=item["text"], label=label, invalidity_type=item.get("conflict_type")) for item in row.get(source, []))
    return result


def convert_fave_row(row: dict) -> BenchmarkItem:
    return BenchmarkItem(id=str(row["id"]), domain="telecom", task_type="quantitative_qa", question=row["question"], gold_answer=normalize_telecom_answer(row), formula=FormulaSpec(id=row.get("gold_formula", "unknown"), expression=row.get("gold_formula")), required_variables=row.get("required_variables", {}), required_conditions=row.get("required_conditions", []), evidence=normalize_telecom_evidence(row), metadata={"clean_context": row.get("clean_context", []), "mixed_context": row.get("mixed_context", []), "expected_arbitration": row.get("expected_arbitration", {}), "invalid_evidence": row.get("invalid_evidence", []), "tolerance": row.get("tolerance", {})})


def load_telecom_items(path: str) -> list[BenchmarkItem]:
    return [convert_fave_row(row) for row in read_jsonl(path)]
