from applicability_qa.benchmark_tools import assign_difficulty, benchmark_track, make_minimal_pair


def test_minimal_pair_marks_roles_and_only_mutates_contrast():
    row = {"runtime": {"id": "q1", "question": "original", "metadata": {}}, "gold": {"answer": {"value": 1}}}
    control, contrast = make_minimal_pair(row, "p1", {"runtime": {"question": "contrast"}})
    assert control["runtime"]["question"] == "original"
    assert contrast["runtime"]["question"] == "contrast"
    assert {control["runtime"]["metadata"]["pair_role"], contrast["runtime"]["metadata"]["pair_role"]} == {"control", "contrast"}


def test_difficulty_and_track_are_deterministic():
    row = {"runtime": {"metadata": {"holdout": True}}, "gold": {"evidence_annotations": [{"label": "rejected"}], "trap_answers": [{"value": 2}]}}
    assert assign_difficulty(row) == "medium"
    assert benchmark_track(row) == "holdout"
