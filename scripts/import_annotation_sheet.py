from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

BOOLEAN_FIELDS = ("is_quantitative_calculation", "formula_supported", "answer_verified", "source_license_verified")


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in {"true", "yes", "y", "1"}:
        return True
    if normalized in {"false", "no", "n", "0"}:
        return False
    raise ValueError(f"invalid boolean label: {value!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidates = {row["candidate_id"]: row for row in (json.loads(line) for line in args.candidates.read_text(encoding="utf-8").splitlines() if line.strip())}
    seen: set[str] = set()
    with args.annotations.open(encoding="utf-8-sig", newline="") as stream:
        for annotation in csv.DictReader(stream):
            candidate_id = annotation["candidate_id"].strip()
            if candidate_id not in candidates:
                raise ValueError(f"unknown candidate_id: {candidate_id}")
            if candidate_id in seen:
                raise ValueError(f"duplicate annotation: {candidate_id}")
            seen.add(candidate_id)
            row = candidates[candidate_id]
            for field in BOOLEAN_FIELDS:
                row["review"][field] = parse_bool(annotation.get(field, ""))
            row["review"]["reviewer_id"] = annotation.get("reviewer_id", "").strip()
            row["review"]["reviewer_notes"] = annotation.get("reviewer_notes", "").strip()
            decision = annotation.get("decision", "").strip().lower()
            if decision not in {"", "accept", "reject"}:
                raise ValueError(f"invalid decision for {candidate_id}: {decision!r}")
            row["status"] = {"accept": "reviewed_accepted", "reject": "reviewed_rejected"}.get(decision, "needs_review")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in candidates.values():
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"imported {len(seen)} annotations -> {args.output}")


if __name__ == "__main__":
    main()
