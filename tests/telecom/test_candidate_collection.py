import json
from pathlib import Path

from scripts.compute_annotation_agreement import cohen_kappa
from scripts.validate_candidate_pool import validate


def test_checked_in_candidate_pool_has_provenance_and_no_fabricated_labels():
    result = validate(Path("data/telecom/collection/candidate_pool_v0.3.jsonl"))
    assert result["items"] == 129
    assert len(result["families"]) == 15
    assert result["splits"] == {"development": 29, "test": 100}
    assert result["errors"] == []


def test_candidate_pool_is_fingerprint_unique():
    rows = [json.loads(line) for line in Path("data/telecom/collection/candidate_pool_v0.3.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len({row["fingerprint"] for row in rows}) == len(rows)


def test_kappa_handles_perfect_and_chance_degenerate_cases():
    assert cohen_kappa([("yes", "yes"), ("no", "no")]) == 1.0
    assert cohen_kappa([("yes", "yes")]) is None
