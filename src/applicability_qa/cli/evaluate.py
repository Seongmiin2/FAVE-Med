from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict

from ..core.jsonl_utils import read_jsonl, write_jsonl
from ..evaluation.evaluate_v2_thesis import evaluate_record, summarize_records
from ..evaluation.statistics import exact_mcnemar, holm_correction, paired_bootstrap
from .common import load_config


def write_csv(path, rows: list[dict], fields: list[str] | None = None) -> None:
    rows = list(rows)
    fields = fields or sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config, root = load_config(args.config)
    if config.get("evaluator_version") != "v2" or config["domain"] != "telecom":
        raise SystemExit("Thesis evaluator currently requires evaluator_version=v2 and Telecom BenchmarkRecord input")
    from ..domains.telecom.adapter import load_telecom_records

    records = {row.runtime.id: row for row in load_telecom_records(str(root / config["input_path"]))}
    result_dir = root / config["result_dir"]
    result_dir.mkdir(parents=True, exist_ok=True)
    details, summaries, outcomes = [], [], {}
    for path in sorted((root / config["output_dir"]).glob("*.jsonl")):
        rows = [evaluate_record(records[prediction["id"]], prediction) for prediction in read_jsonl(path) if prediction["id"] in records]
        if not rows:
            continue
        details.extend(rows)
        summary = {"method": path.stem, **summarize_records(rows)}
        summaries.append(summary)
        outcomes[path.stem] = {row["id"]: bool(row["correct"]) for row in rows}
    write_jsonl(result_dir / "per_item.jsonl", details)
    summary_fields = ["method", "n", "accuracy", "parse_success_rate", "abstention_rate", "trap_hit_rate", "invalid_evidence_precision", "invalid_evidence_recall", "invalid_evidence_f1", "valid_evidence_false_rejection_rate", "conflict_type_macro_f1", "formula_accuracy_at_1", "formula_recall_at_3", "formula_mrr", "relevant_source_recall_at_k"]
    write_csv(result_dir / "summary.csv", summaries, summary_fields)
    error_rows = [{"method": row["method"], "error_type": error, "count": count} for row in summaries for error, count in row["error_counts"].items()]
    write_csv(result_dir / "error_analysis.csv", error_rows, ["method", "error_type", "count"])
    conflict_rows = [{"method": row["method"], "conflict_type": conflict, "score": score} for row in summaries for conflict, score in row["conflict_type_scores"].items()]
    write_csv(result_dir / "conflict_type_analysis.csv", conflict_rows, ["method", "conflict_type", "score"])
    formula_rows = [{"method": row["method"], "accuracy_at_1": row["formula_accuracy_at_1"], "recall_at_3": row["formula_recall_at_3"], "mrr": row["formula_mrr"]} for row in summaries]
    write_csv(result_dir / "formula_family_analysis.csv", formula_rows)
    comparisons = config.get("statistics", {}).get("comparisons", [])
    statistical_rows, p_values = [], {}
    for comparison in comparisons:
        a_name, b_name = comparison["a"], comparison["b"]
        shared = sorted(outcomes.get(a_name, {}).keys() & outcomes.get(b_name, {}).keys())
        if not shared:
            continue
        a, b = [outcomes[a_name][item] for item in shared], [outcomes[b_name][item] for item in shared]
        name = f"{a_name}_vs_{b_name}"
        mcnemar = exact_mcnemar(a, b)
        bootstrap = paired_bootstrap(a, b, resamples=config.get("statistics", {}).get("bootstrap_resamples", 10_000), seed=config.get("statistics", {}).get("seed", 42))
        p_values[name] = float(mcnemar["p_value"])
        statistical_rows.append({"comparison": name, "n": len(shared), **mcnemar, **bootstrap})
    corrected = holm_correction(p_values) if p_values else {}
    for row in statistical_rows:
        row.update(corrected[row["comparison"]])
    write_csv(result_dir / "statistics.csv", statistical_rows)
    provider_name = config.get("model", {}).get("provider", "unknown")
    qualification = "Mock results validate integration only; they are not research performance evidence." if provider_name == "mock" else "Small pilot results validate execution and cost only; the sample is too small for research conclusions."
    lines = [f"# {config['experiment_name']} report", "", qualification, "", "| Method | N | Accuracy | Parse success | Formula Acc@1 | Retrieval Recall@k |", "|---|---:|---:|---:|---:|---:|"]
    lines.extend(f"| {row['method']} | {row['n']} | {row['accuracy']:.3f} | {row['parse_success_rate']:.3f} | {row['formula_accuracy_at_1']:.3f} | {row['relevant_source_recall_at_k']:.3f} |" for row in summaries)
    (result_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote thesis evaluation artifacts -> {result_dir}")


if __name__ == "__main__":
    main()
