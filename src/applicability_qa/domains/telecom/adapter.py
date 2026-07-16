from __future__ import annotations

import re

from ...core.jsonl_utils import read_jsonl
from ...core.schemas import (
    BenchmarkItem, BenchmarkRecord, EvidenceAnnotation, EvidenceItem, FormulaSpec,
    GoldAnnotation, GoldAnswer, RuntimeEvidence, RuntimeQuestion,
)

FORMULA_IDS = {
    "C = B log2(1 + SNR_linear)": "shannon_capacity", "eta = C / B": "spectral_efficiency",
    "FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44": "free_space_path_loss",
    "SINR = S / (I + N)": "sinr", "P_out = 1 - exp(-gamma_th / gamma_bar)": "rayleigh_outage",
    "P_b = Q(sqrt(2 Eb/N0_linear))": "bpsk_ber", "R_s <= 2B": "nyquist_symbol_rate",
    "C = log2 det(I + rho / Nt * H H^H)": "mimo_capacity_identity",
    "Pr = Pt Gt Gr (lambda / (4 pi d))^2": "friis_received_power",
    "SNR_linear = 10^(SNR_dB / 10)": "snr_db_to_linear",
}


def extract_requested_output_from_question(question: str) -> str | None:
    """Extract an explicitly requested output phrase without consulting gold."""
    patterns = (
        r"(?:express(?:ed)?|report|give|answer)\s+(?:the\s+)?(?:result|answer)?\s*(?:in|as)\s+([A-Za-z][A-Za-z0-9/%·^._ -]{0,30})",
        r"(?:in units of|unit(?:s)?\s*[:=])\s*([A-Za-z][A-Za-z0-9/%·^._ -]{0,30})",
    )
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            value = re.split(r"[?.;,]", match.group(1), maxsplit=1)[0].strip()
            return value or None
    return None


def normalize_telecom_answer(row: dict) -> GoldAnswer:
    return GoldAnswer(value=row["gold_value"], unit=row.get("gold_unit"), output_type="telecom_quantity")


def normalize_telecom_evidence(row: dict) -> list[EvidenceItem]:
    result = []
    for source, label in (("valid_evidence", "valid"), ("invalid_evidence", "invalid"), ("contested_evidence", "unknown")):
        result.extend(EvidenceItem(id=item["id"], text=item["text"], label=label, invalidity_type=item.get("conflict_type")) for item in row.get(source, []))
    return result


def convert_fave_row(row: dict) -> BenchmarkItem:
    expression = row.get("gold_formula")
    formula_id = str(row.get("formula_id") or FORMULA_IDS.get(expression, "unknown"))
    return BenchmarkItem(id=str(row["id"]), domain="telecom", task_type="quantitative_qa", question=row["question"], gold_answer=normalize_telecom_answer(row), formula=FormulaSpec(id=formula_id, expression=expression), required_variables=row.get("required_variables", {}), required_conditions=row.get("required_conditions", []), evidence=normalize_telecom_evidence(row), metadata={"clean_context": row.get("clean_context", []), "mixed_context": row.get("mixed_context", []), "expected_arbitration": row.get("expected_arbitration", {}), "invalid_evidence": row.get("invalid_evidence", []), "tolerance": row.get("tolerance", {})})


def load_telecom_items(path: str) -> list[BenchmarkItem]:
    return [convert_fave_row(row) for row in read_jsonl(path)]


def convert_fave_record(row: dict) -> BenchmarkRecord:
    evidence = []
    annotations = []
    label_map = {"valid_evidence": "valid", "contested_evidence": "contested", "invalid_evidence": "rejected"}
    for field, label in label_map.items():
        for item in row.get(field, []):
            evidence.append(RuntimeEvidence(id=item["id"], text=item["text"]))
            conflict = str(item.get("conflict_type", "none")).lower()
            normalized = "none"
            for candidate in ("unit_compatibility", "condition_mismatch", "variable_binding", "formula_convention", "approximation_misuse", "physical_constraint", "solution_step_corruption"):
                if candidate.replace("_", " ") in conflict.replace("/", " ").replace("-", " "):
                    normalized = candidate
                    break
            annotations.append(EvidenceAnnotation(evidence_id=item["id"], label=label, conflict_type=normalized, rationale=item.get("valid_in_context")))
    requested = extract_requested_output_from_question(row["question"])
    runtime = RuntimeQuestion(id=str(row["id"]), domain="telecom", question=row["question"], requested_output=requested, evidence=evidence, metadata={"clean_context": row.get("clean_context", []), "mixed_context": row.get("mixed_context", [])})
    expression = row.get("gold_formula")
    gold = GoldAnnotation(answer=normalize_telecom_answer(row), formula_id=str(row.get("formula_id") or FORMULA_IDS.get(expression, "unknown")), formula_expression=expression, required_variables=row.get("required_variables", {}), required_units=row.get("required_units", {}), evidence_annotations=annotations, tolerance=row.get("tolerance", {}), trap_answers=[{"evidence_id": item["id"], "value": item.get("trap_answer"), "unit": item.get("trap_unit")} for item in row.get("invalid_evidence", [])])
    return BenchmarkRecord(schema_version="0.3", source={"dataset": row.get("source", "fave_seed_v0.2"), "source_id": str(row["id"]), "adaptation": "legacy seed converted without mutating source"}, runtime=runtime, gold=gold)


def load_telecom_records(path: str) -> list[BenchmarkRecord]:
    return [convert_fave_record(row) for row in read_jsonl(path)]
