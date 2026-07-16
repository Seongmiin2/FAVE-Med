from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

REVISION = "591157b3343b4dda247294f9d929da4c75026fa8"
FAMILIES = {
    "Body Mass Index (BMI)": "body_mass_index",
    "Mean Arterial Pressure (MAP)": "mean_arterial_pressure",
    "Anion Gap": "anion_gap",
    "Creatinine Clearance (Cockcroft-Gault Equation)": "cockcroft_gault",
    "Calcium Correction for Hypoalbuminemia": "corrected_calcium",
    "Body Surface Area Calculator": "body_surface_area_mosteller",
    "Serum Osmolality": "serum_osmolality",
    "Fractional Excretion of Sodium (FENa)": "fractional_excretion_sodium",
    "QTc Bazett Calculator": "qtc_bazett",
    "MELD Na (UNOS/OPTN)": "meld_na",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/medical/raw/medcalc_bench_verified/test_data.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/medical/collection/verified_selection_v0.3.jsonl"))
    args = parser.parse_args()
    buckets = defaultdict(list)
    with args.input.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["Calculator Name"] in FAMILIES:
                buckets[row["Calculator Name"]].append(row)
    selected = []
    for name, calculator_id in FAMILIES.items():
        rows = sorted(buckets[name], key=lambda row: int(row["Row Number"]))
        if len(rows) < 12:
            raise ValueError(f"{name} has only {len(rows)} rows")
        for index, row in enumerate(rows[:12]):
            selected.append({
                "candidate_id": f"medcalc_verified_{row['Row Number']}", "source_row_number": row["Row Number"],
                "source_note_id": row["Note ID"], "calculator_id": calculator_id,
                "proposed_split": "development" if index < 2 else "test", "status": "needs_consistency_audit",
                "source": {"dataset": "nsk7153/MedCalc-Bench-Verified", "revision": REVISION, "license": "CC-BY-SA-4.0"},
                "excluded_gold_fields": ["Relevant Entities", "Ground Truth Answer", "Lower Limit", "Upper Limit", "Ground Truth Explanation"],
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in selected:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts = Counter(row["proposed_split"] for row in selected)
    print(json.dumps({"items": len(selected), "families": len(FAMILIES), "splits": counts, "status": "candidate_selection_only"}, default=dict, indent=2))


if __name__ == "__main__":
    main()
