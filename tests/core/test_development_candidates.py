import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / relative).read_text(encoding="utf-8").splitlines()]


def assert_review_ready(rows: list[dict], expected_count: int) -> None:
    assert len(rows) == expected_count
    assert len({row["runtime"]["id"] for row in rows}) == expected_count
    for row in rows:
        runtime = row["runtime"]
        assert row["review_status"].startswith("pending_")
        assert "draft_gold_for_review" in row
        assert not ({"gold", "expected_label", "source_type", "trap", "distractor"} & runtime.keys())
        for evidence in runtime.get("evidence", []):
            assert set(evidence) == {"id", "text"}
            assert not any(word in evidence["id"].lower() for word in ("valid", "trap", "distractor", "gold"))


def test_telecom_development_has_30_review_pending_candidates():
    assert_review_ready(load("data/telecom/development/candidates_30_v0.1.jsonl"), 30)


def test_medical_development_has_20_review_pending_candidates():
    assert_review_ready(load("data/medical/development/candidates_20_v0.1.jsonl"), 20)
