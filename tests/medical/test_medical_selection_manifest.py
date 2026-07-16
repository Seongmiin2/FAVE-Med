import json
from collections import Counter
from pathlib import Path


def test_verified_selection_manifest_is_balanced_and_contains_no_gold_payload():
    rows = [json.loads(line) for line in Path("data/medical/collection/verified_selection_v0.3.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 120
    assert len({row["candidate_id"] for row in rows}) == 120
    assert Counter(row["proposed_split"] for row in rows) == {"development": 20, "test": 100}
    assert set(Counter(row["calculator_id"] for row in rows).values()) == {12}
    serialized = json.dumps(rows)
    for forbidden in ("patient_note", "ground_truth_answer", "relevant_entities", "ground_truth_explanation"):
        assert forbidden not in serialized.lower()
