from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

FAMILIES = {
    "shannon_capacity": r"shannon|channel capacity|achievable rate",
    "spectral_efficiency": r"spectral efficiency",
    "fspl_path_loss": r"free.?space path loss|path loss",
    "friis_received_power": r"friis|received power",
    "snr_conversion": r"\bsnr\b|signal.to.noise",
    "sinr": r"\bsinr\b|interference.plus.noise",
    "outage_probability": r"outage probability",
    "ber": r"bit error|\bber\b|bpsk",
    "nyquist_rate": r"nyquist|symbol rate",
    "mimo_capacity": r"mimo.*capacity|capacity.*mimo",
    "noise_power": r"noise power|thermal noise",
    "link_budget": r"link budget",
    "ebn0_relation": r"eb.?n0|energy per bit",
    "path_loss_exponent": r"path loss exponent",
    "doppler_shift": r"doppler",
}


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def fingerprint(row: dict) -> str:
    value = normalized(f"{row.get('question_text', '')} {row.get('equation', '')}")
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def suitability(row: dict) -> int:
    question = row.get("question_text", "")
    answer = str(row.get("correct_answer", ""))
    score = 0
    score += 3 * bool(re.search(r"calculate|compute|determine|what is the value", question, re.I))
    score += 2 * bool(re.search(r"\d", answer))
    score += 2 * bool(re.search(r"\d", row.get("background", "")))
    score += bool(row.get("equation"))
    score += bool(row.get("paper_id"))
    return score


def load_rows(path: Path, dataset: str) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            row["_dataset"] = dataset
            row["_source_id"] = str(row.get("id", row.get("question_id")))
            rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wireless", type=Path, default=Path("../FAVE-RAG/data/raw/wirelessmathbench_full.jsonl"))
    parser.add_argument("--xl", type=Path, default=Path("../FAVE-RAG/data/raw/wirelessmathbench_xl_full.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    parser.add_argument("--quota-per-family", type=int, default=10)
    args = parser.parse_args()

    source_rows = load_rows(args.wireless, "XINLI1997/WirelessMathBench") + load_rows(args.xl, "XINLI1997/WirelessMATHBench-XL")
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in source_rows:
        searchable = " ".join(str(row.get(field, "")) for field in ("background", "question_text", "equation"))
        for family, pattern in FAMILIES.items():
            if re.search(pattern, searchable, re.I):
                buckets[family].append(row)

    selected, used = [], set()
    for family in FAMILIES:
        ranked = sorted(buckets[family], key=lambda row: (-suitability(row), row["_dataset"], row["_source_id"]))
        family_count = 0
        for row in ranked:
            key = fingerprint(row)
            if key in used:
                continue
            used.add(key)
            family_count += 1
            candidate_id = f"candidate_{family}_{family_count:02d}"
            selected.append(
                {
                    "candidate_id": candidate_id,
                    "collection_version": "0.3",
                    "status": "needs_review",
                    "proposed_formula_family": family,
                    "proposed_split": "development" if family_count <= 2 else "test",
                    "suitability_score": suitability(row),
                    "fingerprint": key,
                    "source": {
                        "dataset": row["_dataset"],
                        "source_id": row["_source_id"],
                        "paper_id": row.get("paper_id"),
                        "dataset_license": "CC-BY-4.0",
                        "source_paper_license": "needs_verification",
                        "adaptation": "candidate only; not yet converted to quantitative QA",
                    },
                    "original": {
                        "type": row.get("type"),
                        "background": row.get("background", ""),
                        "question_text": row.get("question_text", ""),
                        "equation": row.get("equation", ""),
                        "options": row.get("options"),
                        "correct_answer": row.get("correct_answer"),
                    },
                    "review": {
                        "is_quantitative_calculation": None,
                        "formula_supported": None,
                        "answer_verified": None,
                        "source_license_verified": None,
                        "reviewer_notes": "",
                    },
                }
            )
            if family_count >= args.quota_per_family:
                break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in selected:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary_path = args.output.with_name("candidate_pool_summary.csv")
    counts = Counter(row["proposed_formula_family"] for row in selected)
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["formula_family", "candidate_count", "available_source_matches"])
        writer.writeheader()
        for family in FAMILIES:
            writer.writerow({"formula_family": family, "candidate_count": counts[family], "available_source_matches": len(buckets[family])})
    print(f"wrote {len(selected)} candidates -> {args.output}")
    print(f"wrote family summary -> {summary_path}")


if __name__ == "__main__":
    main()
