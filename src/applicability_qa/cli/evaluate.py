from __future__ import annotations

import argparse
import csv
from collections import Counter

from ..core.jsonl_utils import read_jsonl, write_jsonl
from ..core.metrics import precision_recall_f1
from ..core.unit_utils import close_to, convert_value
from .common import load_config, load_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config, root = load_config(args.config)
    items = {item.id: item for item in load_items(config, root)}
    evaluator = __import__(f"applicability_qa.domains.{config['domain']}.evaluator", fromlist=["evaluate"]).evaluate
    result_dir = root / config["result_dir"]
    result_dir.mkdir(parents=True, exist_ok=True)
    details, summaries = [], []
    for path in sorted((root / config["output_dir"]).glob("*.jsonl")):
        method_rows = []
        for prediction in read_jsonl(path):
            if prediction["id"] not in items:
                continue
            row = {"id": prediction["id"], "method": prediction["method"], **evaluator(items[prediction["id"]], prediction), "abstain": prediction.get("abstain", False)}
            details.append(row)
            method_rows.append(row)
        if method_rows:
            errors = Counter(row.get("error_type") or "none" for row in method_rows)
            predictions = {row["id"]: row for row in read_jsonl(path)}
            tp = fp = fn = false_rejected = valid_total = trap_hits = 0
            for item_id, prediction in predictions.items():
                item = items.get(item_id)
                if not item:
                    continue
                expected = item.metadata.get("expected_arbitration", {})
                invalid = set(expected.get("Rejected", []))
                valid = set(expected.get("Valid", []))
                rejected = set(prediction.get("rejected_evidence_ids", []))
                tp += len(invalid & rejected)
                fp += len(rejected - invalid)
                fn += len(invalid - rejected)
                false_rejected += len(valid & rejected)
                valid_total += len(valid)
                value = prediction.get("answer", {}).get("final_value")
                unit = prediction.get("answer", {}).get("final_unit")
                if value is not None:
                    for evidence in item.metadata.get("invalid_evidence", []):
                        converted, _ = convert_value(float(value), unit, evidence.get("trap_unit", item.gold_answer.unit))
                        tolerance = item.metadata.get("tolerance", {})
                        if close_to(converted, float(evidence["trap_answer"]), tolerance.get("rel", 0.01), tolerance.get("abs") or 1e-6):
                            trap_hits += 1
                            break
            prf = precision_recall_f1(tp, fp, fn)
            summaries.append({"method": path.stem, "n": len(method_rows), "accuracy": sum(r["correct"] for r in method_rows) / len(method_rows), "parse_success_rate": sum(r["parsed"] for r in method_rows) / len(method_rows), "abstention_rate": sum(r["abstain"] for r in method_rows) / len(method_rows), "trap_hit_rate": trap_hits / len(method_rows), "invalid_evidence_precision": prf["precision"], "invalid_evidence_recall": prf["recall"], "invalid_evidence_f1": prf["f1"], "valid_evidence_false_rejection_rate": false_rejected / valid_total if valid_total else 0.0, "errors": dict(errors)})
    write_jsonl(result_dir / "per_item.jsonl", details)
    with (result_dir / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["method", "n", "accuracy", "parse_success_rate", "abstention_rate", "trap_hit_rate", "invalid_evidence_precision", "invalid_evidence_recall", "invalid_evidence_f1", "valid_evidence_false_rejection_rate"])
        writer.writeheader()
        writer.writerows({key: row[key] for key in writer.fieldnames} for row in summaries)
    lines = [f"# {config['experiment_name']} report", "", "| Method | N | Accuracy | Parse success | Trap hit | Invalid evidence F1 | Valid false rejection |", "|---|---:|---:|---:|---:|---:|---:|"]
    lines.extend(f"| {r['method']} | {r['n']} | {r['accuracy']:.3f} | {r['parse_success_rate']:.3f} | {r['trap_hit_rate']:.3f} | {r['invalid_evidence_f1']:.3f} | {r['valid_evidence_false_rejection_rate']:.3f} |" for r in summaries)
    (result_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {result_dir / 'summary.csv'} and {result_dir / 'report.md'}")


if __name__ == "__main__":
    main()
