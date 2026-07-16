from applicability_qa.evaluation.statistics import exact_mcnemar, holm_correction, paired_bootstrap


def test_exact_mcnemar_known_discordant_counts():
    result = exact_mcnemar([True, True, False, False], [True, False, True, True])
    assert result["a_correct_b_wrong"] == 1
    assert result["a_wrong_b_correct"] == 2
    assert result["p_value"] == 1.0


def test_paired_bootstrap_is_reproducible():
    a, b = [False, False, True, True], [True, True, True, True]
    assert paired_bootstrap(a, b, resamples=1000, seed=7) == paired_bootstrap(a, b, resamples=1000, seed=7)


def test_holm_is_monotonic_and_controls_family():
    result = holm_correction({"a": 0.001, "b": 0.02, "c": 0.5})
    assert result["a"]["reject"] is True
    assert result["a"]["adjusted_p"] <= result["b"]["adjusted_p"] <= result["c"]["adjusted_p"]
