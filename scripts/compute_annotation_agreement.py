from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

FIELDS = ("is_quantitative_calculation", "formula_supported", "answer_verified", "source_license_verified", "decision")


def load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["candidate_id"].strip(): row for row in csv.DictReader(stream)}


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    labels = sorted({value for pair in pairs for value in pair})
    observed = sum(a == b for a, b in pairs) / len(pairs)
    expected = sum(
        (sum(a == label for a, _ in pairs) / len(pairs)) * (sum(b == label for _, b in pairs) / len(pairs))
        for label in labels
    )
    return None if expected == 1 else (observed - expected) / (1 - expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    args = parser.parse_args()
    a, b = load(args.reviewer_a), load(args.reviewer_b)
    shared = sorted(a.keys() & b.keys())
    if not shared:
        raise SystemExit("no shared candidate IDs; agreement was not computed")
    result = {"shared_items": len(shared), "fields": {}}
    for field in FIELDS:
        pairs = [(a[item].get(field, "").strip().lower(), b[item].get(field, "").strip().lower()) for item in shared]
        pairs = [(left, right) for left, right in pairs if left and right]
        result["fields"][field] = {
            "labeled_pairs": len(pairs),
            "percent_agreement": None if not pairs else sum(x == y for x, y in pairs) / len(pairs),
            "cohen_kappa": cohen_kappa(pairs),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
