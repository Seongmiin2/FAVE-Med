from __future__ import annotations

from collections import Counter, defaultdict

from ..core.answer_parser import evaluate_answer
from ..core.metrics import precision_recall_f1, safe_div
from ..core.schemas import BenchmarkRecord, RunRecord
from ..core.unit_utils import close_to, convert_value
from .error_taxonomy import primary_error


def evaluate_record(record: BenchmarkRecord, prediction: dict | RunRecord) -> dict:
    run = prediction if isinstance(prediction, RunRecord) else RunRecord.model_validate(prediction)
    answer = evaluate_answer(run.model_dump(), record.gold.answer.model_dump(), record.runtime.domain)
    if answer["parsed"] and record.gold.answer.output_type in {"decimal", "integer", "telecom_quantity"}:
        try:
            converted, ambiguous = convert_value(float(run.answer["final_value"]), run.answer.get("final_unit"), record.gold.answer.unit)
            answer["unit_correct"] = converted is not None and not ambiguous
            answer["correct"] = close_to(converted, float(record.gold.answer.value), record.gold.tolerance.get("rel", 0.01) or 0.01, record.gold.tolerance.get("abs", 1e-6) or 1e-6)
            answer["error_type"] = None if answer["correct"] else "wrong_answer"
        except (TypeError, ValueError):
            answer.update(correct=False, error_type="parse_error")
    gold_by_id = {row.evidence_id: row for row in record.gold.evidence_annotations}
    predicted_by_id = {row.evidence_id: row for row in run.evidence_decisions}
    invalid_gold = {item for item, row in gold_by_id.items() if row.label == "rejected"}
    valid_gold = {item for item, row in gold_by_id.items() if row.label == "valid"}
    rejected = {item for item, row in predicted_by_id.items() if row.label == "rejected"}
    tp, fp, fn = len(invalid_gold & rejected), len(rejected - invalid_gold), len(invalid_gold - rejected)
    selection = run.formula_selection
    formula_correct = None if selection is None else selection.predicted_formula_id == record.gold.formula_id
    candidates = [] if selection is None else selection.candidate_formula_ids
    retrieval_hit = None
    if run.retrieval is not None:
        retrieval_hit = any(row.source_id == record.gold.formula_id for row in run.retrieval.results)
    trap_hit = False
    if run.answer.get("final_value") is not None:
        for trap in record.gold.trap_answers:
            if trap.get("value") is None:
                continue
            converted, _ = convert_value(float(run.answer["final_value"]), run.answer.get("final_unit"), trap.get("unit", record.gold.answer.unit))
            if close_to(converted, float(trap["value"]), record.gold.tolerance.get("rel", 0.01) or 0.01, record.gold.tolerance.get("abs", 1e-6) or 1e-6):
                trap_hit = True
                break
    conflict_pairs = []
    for evidence_id, gold in gold_by_id.items():
        predicted = predicted_by_id.get(evidence_id)
        if predicted is not None and gold.conflict_type != "none":
            conflict_pairs.append((gold.conflict_type, predicted.conflict_type))
    result = {
        "id": record.runtime.id, "method": run.method, **answer,
        "abstain": run.abstain, "trap_hit": trap_hit,
        "invalid_tp": tp, "invalid_fp": fp, "invalid_fn": fn,
        "valid_false_rejections": len(valid_gold & rejected), "valid_total": len(valid_gold),
        "formula_correct": formula_correct, "formula_in_top3": record.gold.formula_id in candidates[:3],
        "formula_rank": candidates.index(record.gold.formula_id) + 1 if record.gold.formula_id in candidates else None,
        "retrieval_hit": retrieval_hit, "conflict_pairs": conflict_pairs,
    }
    result["primary_error"] = primary_error(run.model_dump(), correct=result["correct"], parsed=result["parsed"], formula_correct=formula_correct, retrieval_hit=retrieval_hit)
    return result


def summarize_records(rows: list[dict]) -> dict:
    if not rows:
        return {}
    tp, fp, fn = sum(row["invalid_tp"] for row in rows), sum(row["invalid_fp"] for row in rows), sum(row["invalid_fn"] for row in rows)
    prf = precision_recall_f1(tp, fp, fn)
    all_pairs = [pair for row in rows for pair in row["conflict_pairs"]]
    labels = sorted({label for pair in all_pairs for label in pair if label != "none"})
    conflict_scores = {}
    for label in labels:
        tp = sum(gold == label and predicted == label for gold, predicted in all_pairs)
        fp = sum(gold != label and predicted == label for gold, predicted in all_pairs)
        fn = sum(gold == label and predicted != label for gold, predicted in all_pairs)
        conflict_scores[label] = precision_recall_f1(tp, fp, fn)["f1"]
    formula_rows = [row for row in rows if row["formula_correct"] is not None]
    retrieval_rows = [row for row in rows if row["retrieval_hit"] is not None]
    return {
        "n": len(rows), "accuracy": safe_div(sum(row["correct"] for row in rows), len(rows)),
        "parse_success_rate": safe_div(sum(row["parsed"] for row in rows), len(rows)),
        "abstention_rate": safe_div(sum(row["abstain"] for row in rows), len(rows)),
        "trap_hit_rate": safe_div(sum(row["trap_hit"] for row in rows), len(rows)),
        "invalid_evidence_precision": prf["precision"], "invalid_evidence_recall": prf["recall"], "invalid_evidence_f1": prf["f1"],
        "valid_evidence_false_rejection_rate": safe_div(sum(row["valid_false_rejections"] for row in rows), sum(row["valid_total"] for row in rows)),
        "conflict_type_macro_f1": safe_div(sum(conflict_scores.values()), len(conflict_scores)), "conflict_type_scores": conflict_scores,
        "formula_accuracy_at_1": safe_div(sum(row["formula_correct"] for row in formula_rows), len(formula_rows)),
        "formula_recall_at_3": safe_div(sum(row["formula_in_top3"] for row in formula_rows), len(formula_rows)),
        "formula_mrr": safe_div(sum(1 / row["formula_rank"] if row["formula_rank"] else 0 for row in formula_rows), len(formula_rows)),
        "relevant_source_recall_at_k": safe_div(sum(row["retrieval_hit"] for row in retrieval_rows), len(retrieval_rows)),
        "error_counts": dict(Counter(row["primary_error"] or "none" for row in rows)),
    }
