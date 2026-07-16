from applicability_qa.domains.telecom.adapter import convert_fave_row
from applicability_qa.domains.telecom.formula_executor import execute


def test_shannon():
    value, unit = execute("shannon_capacity", {"B": 10_000_000, "snr_linear": 100})
    assert round(value / 1e6, 3) == 66.582
    assert unit == "bps"


def test_adapter():
    item = convert_fave_row({"id": "t1", "question": "q", "gold_value": 1, "gold_unit": "bps", "valid_evidence": [], "invalid_evidence": []})
    assert item.domain == "telecom"


def test_first_three_pilot_formulas():
    efficiency, _ = execute("spectral_efficiency", {"C": 30_000_000, "B": 5_000_000})
    fspl, _ = execute("free_space_path_loss", {"d": 2, "f": 2400})
    assert efficiency == 6
    assert round(fspl, 3) == 106.065
    aliased, _ = execute("free_space_path_loss", {"d_km": 2, "f_MHz": 2400})
    assert round(aliased, 3) == 106.065
    shannon, _ = execute("shannon_capacity", {"B": 10_000_000, "SNR_linear": 100})
    assert round(shannon / 1e6, 3) == 66.582
    normalized_efficiency, _ = execute("spectral_efficiency", {"C": 30, "B": 5})
    assert normalized_efficiency == 6
    mimo, _ = execute("mimo_capacity_identity", {"rho": 10, "Nt": 2, "H": [[1, 0], [0, 1]]})
    assert round(mimo, 6) == 5.169925
    linear, _ = execute("snr_db_to_linear", {"SNR_dB": 13})
    assert round(linear, 6) == 19.952623


def test_all_pilot_formulas():
    cases = [
        ("shannon_capacity", {"B": 10_000_000, "snr_linear": 100}, 66_582_114.8275),
        ("spectral_efficiency", {"C": 30_000_000, "B": 5_000_000}, 6.0),
        ("free_space_path_loss", {"d": 2, "f": 2400}, 106.064825),
        ("sinr", {"S": 1, "I": 0.2, "N": 0.1}, 3.333333),
        ("rayleigh_outage", {"gamma_th": 5, "gamma_bar": 10}, 0.393469),
        ("bpsk_ber", {"eb_n0_db": 9}, 3.362723e-05),
        ("nyquist_symbol_rate", {"B": 3000}, 6000.0),
        ("mimo_capacity_identity", {"rho": 10, "Nt": 2, "H": "identity"}, 5.169925),
        ("friis_received_power", {"Pt": 1, "Gt": 1, "Gr": 1, "lambda": 0.125, "d": 100}, 9.894647e-09),
        ("snr_db_to_linear", {"snr_db": 13}, 19.952623),
    ]
    for formula, variables, expected in cases:
        value, _ = execute(formula, variables)
        assert abs(value - expected) <= max(abs(expected) * 1e-5, 1e-9)


def test_executor_requires_exact_supported_id():
    import pytest

    with pytest.raises(ValueError, match="Unsupported telecom formula ID"):
        execute("shannon_capacity_with_hidden_suffix", {"B": 1, "snr_linear": 1})
