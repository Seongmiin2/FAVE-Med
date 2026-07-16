from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def validate(path: Path) -> dict[str, object]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row["candidate_id"] for row in rows]
    fingerprints = [row["fingerprint"] for row in rows]
    errors: list[str] = []
    if len(ids) != len(set(ids)):
        errors.append("duplicate candidate_id")
    if len(fingerprints) != len(set(fingerprints)):
        errors.append("duplicate fingerprint")
    for row in rows:
        source = row.get("source", {})
        review = row.get("review", {})
        if row.get("status") != "needs_review":
            errors.append(f"{row.get('candidate_id')}: unreviewed candidate has invalid status")
        if not source.get("dataset") or not source.get("source_id"):
            errors.append(f"{row.get('candidate_id')}: missing provenance")
        if source.get("source_paper_license") != "needs_verification":
            errors.append(f"{row.get('candidate_id')}: source license must remain pending")
        if any(review.get(field) is not None for field in (
            "is_quantitative_calculation", "formula_supported", "answer_verified", "source_license_verified"
        )):
            errors.append(f"{row.get('candidate_id')}: fabricated review label")
    result = {
        "items": len(rows),
        "families": dict(sorted(Counter(row["proposed_formula_family"] for row in rows).items())),
        "splits": dict(sorted(Counter(row["proposed_split"] for row in rows).items())),
        "errors": errors,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    args = parser.parse_args()
    result = validate(args.input)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
