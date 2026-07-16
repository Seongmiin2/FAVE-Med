from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

CALCULATION_CUE = re.compile(r"calculate|compute|determine|what is the value", re.IGNORECASE)


def audit(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    numeric = [row for row in rows if re.search(r"\d", str(row["original"].get("correct_answer", "")))]
    calculation = [row for row in rows if CALCULATION_CUE.search(row["original"].get("question_text", ""))]
    direct = [row for row in numeric if CALCULATION_CUE.search(row["original"].get("question_text", ""))]
    return {
        "candidate_count": len(rows),
        "family_count": len({row["proposed_formula_family"] for row in rows}),
        "numeric_answer_candidates": len(numeric),
        "explicit_calculation_candidates": len(calculation),
        "numeric_and_explicit_calculation_candidates": len(direct),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "readiness": "not_experiment_ready",
        "reason": "Human review, quantitative adaptation, independent answer/unit verification, evidence construction, and license verification are incomplete.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/telecom/collection/readiness_audit_v0.3.json"))
    args = parser.parse_args()
    result = audit(args.input)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
