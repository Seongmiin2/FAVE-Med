from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--domain", choices=("telecom", "medical"), required=True)
    parser.add_argument("--sample-size", type=int, default=60)
    parser.add_argument("--seed", type=int, default=20260716)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < args.sample_size:
        raise SystemExit(f"need {args.sample_size} rows, found {len(rows)}")
    rng = random.Random(args.seed)
    chosen = rng.sample(rows, args.sample_size)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["item_id", "question", "evidence_id", "evidence_text", "applicability_label", "conflict_type", "answer_verified", "unit_verified", "license_verified", "reviewer_id", "reviewer_role", "notes"]
    for reviewer, seed_offset in (("A", 1), ("B", 2)):
        packet = list(chosen)
        random.Random(args.seed + seed_offset).shuffle(packet)
        path = args.output_dir / f"{args.domain}_reviewer_{reviewer}.csv"
        with path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in packet:
                runtime = row.get("runtime", row)
                evidence = runtime.get("evidence", []) or [{}]
                for item in evidence:
                    writer.writerow({"item_id": runtime.get("id", row.get("candidate_id")), "question": runtime.get("question", row.get("question_text", "")), "evidence_id": item.get("id", ""), "evidence_text": item.get("text", "")})
    manifest = {"domain": args.domain, "input": str(args.input), "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(), "sample_size": args.sample_size, "seed": args.seed, "reviewers": ["A", "B"], "status": "awaiting_independent_human_review"}
    (args.output_dir / f"{args.domain}_packet_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
