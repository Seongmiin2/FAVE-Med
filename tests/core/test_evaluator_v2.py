from applicability_qa.core.schemas import BenchmarkRecord, EvidenceAnnotation, GoldAnnotation, GoldAnswer, RunRecord, RuntimeQuestion
from applicability_qa.evaluation.evaluate_v2_thesis import evaluate_record, summarize_records


def record():
    return BenchmarkRecord(
        runtime=RuntimeQuestion(id="x", domain="telecom", question="q"),
        gold=GoldAnnotation(
            answer=GoldAnswer(value=100, unit="bps", output_type="telecom_quantity"), formula_id="f",
            tolerance={"rel": 0.001, "abs": 0},
            evidence_annotations=[
                EvidenceAnnotation(evidence_id="v", label="valid"),
                EvidenceAnnotation(evidence_id="i", label="rejected", conflict_type="unit_compatibility"),
            ],
        ),
    )


def prediction(value=100):
    return RunRecord(
        id="x", experiment_id="e", domain="telecom", method="m", prompt_version="p",
        answer={"final_value": value, "final_unit": "bps"},
        evidence_decisions=[
            {"evidence_id": "v", "label": "valid", "reason": "ok", "confidence": 1},
            {"evidence_id": "i", "label": "rejected", "conflict_type": "unit_compatibility", "reason": "bad unit", "confidence": 1},
        ],
    )


def test_v2_uses_gold_annotation_tolerance_and_never_runtime_metadata():
    benchmark = record()
    benchmark.runtime.metadata = {"tolerance": {"rel": 1}, "expected_arbitration": {"Rejected": []}}
    assert evaluate_record(benchmark, prediction(100.05))["correct"] is True
    assert evaluate_record(benchmark, prediction(101))["correct"] is False


def test_conflict_macro_f1_uses_gold_annotations():
    row = evaluate_record(record(), prediction())
    summary = summarize_records([row])
    assert summary["invalid_evidence_f1"] == 1.0
    assert summary["conflict_type_macro_f1"] == 1.0
