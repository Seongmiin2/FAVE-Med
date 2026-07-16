from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/telecom/annotations/candidate_review_sheet.csv"))
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["candidate_id", "formula_family", "source_dataset", "source_id", "paper_id", "question_text", "equation", "correct_answer", "is_quantitative_calculation", "formula_supported", "answer_verified", "source_license_verified", "decision", "reviewer_id", "reviewer_notes"]
    with args.output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"candidate_id": row["candidate_id"], "formula_family": row["proposed_formula_family"], "source_dataset": row["source"]["dataset"], "source_id": row["source"]["source_id"], "paper_id": row["source"].get("paper_id"), "question_text": row["original"]["question_text"], "equation": row["original"]["equation"], "correct_answer": row["original"]["correct_answer"]})
    print(f"wrote {len(rows)} rows -> {args.output}")


if __name__ == "__main__":
    main()
