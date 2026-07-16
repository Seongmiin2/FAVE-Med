from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED = ("applicability_label", "conflict_type", "answer_verified", "unit_verified", "license_verified", "reviewer_id", "reviewer_role")


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--domain", choices=("telecom", "medical"), required=True)
    args = parser.parse_args()
    a, b = load(args.reviewer_a), load(args.reviewer_b)
    ids_a = {row["reviewer_id"].strip() for row in a if row["reviewer_id"].strip()}
    ids_b = {row["reviewer_id"].strip() for row in b if row["reviewer_id"].strip()}
    errors = []
    if len(ids_a) != 1 or len(ids_b) != 1 or ids_a == ids_b:
        errors.append("reviewer_id must identify two distinct reviewers")
    for label, rows in (("A", a), ("B", b)):
        for index, row in enumerate(rows, 2):
            missing = [field for field in REQUIRED if not row.get(field, "").strip()]
            if missing:
                errors.append(f"reviewer {label} row {index}: missing {missing}")
    if args.domain == "medical" and not any("physician" in row.get("reviewer_role", "").lower() or "nurse" in row.get("reviewer_role", "").lower() or "clinical" in row.get("reviewer_role", "").lower() for row in a + b):
        errors.append("medical review requires a declared clinical reviewer role")
    report = {"valid": not errors, "reviewer_a": sorted(ids_a), "reviewer_b": sorted(ids_b), "rows_a": len(a), "rows_b": len(b), "errors": errors}
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
