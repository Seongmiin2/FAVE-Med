from applicability_qa.domains.telecom.adapter import convert_fave_row
from applicability_qa.domains.telecom.formula_executor import execute


def test_shannon():
    value, unit = execute("Shannon capacity", {"B": 10_000_000, "snr_linear": 100})
    assert round(value / 1e6, 3) == 66.582
    assert unit == "bps"


def test_adapter():
    item = convert_fave_row({"id": "t1", "question": "q", "gold_value": 1, "gold_unit": "bps", "valid_evidence": [], "invalid_evidence": []})
    assert item.domain == "telecom"


def test_first_three_pilot_formulas():
    efficiency, _ = execute("eta = C / B", {"C": 30_000_000, "B": 5_000_000})
    fspl, _ = execute("FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44", {"d": 2, "f": 2400})
    assert efficiency == 6
    assert round(fspl, 3) == 106.065
    aliased, _ = execute("FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44", {"d_km": 2, "f_MHz": 2400})
    assert round(aliased, 3) == 106.065
    shannon, _ = execute("C = B log2(1 + SNR_linear)", {"B": 10_000_000, "SNR_linear": 100})
    assert round(shannon / 1e6, 3) == 66.582
    normalized_efficiency, _ = execute("eta = C / B", {"C": 30_000_000, "B": 5})
    assert normalized_efficiency == 6
    mimo, _ = execute("C = log2 det(I + rho / Nt * H H^H)", {"rho": 10, "Nt": 2, "H": [[1, 0], [0, 1]]})
    assert round(mimo, 6) == 5.169925
    linear, _ = execute("SNR_linear = 10^(SNR_dB / 10)", {"SNR_dB": 13})
    assert round(linear, 6) == 19.952623


def test_all_pilot_formulas():
    cases = [
        ("C = B log2(1 + SNR_linear)", {"B": 10_000_000, "snr_linear": 100}, 66_582_114.8275),
        ("eta = C / B", {"C": 30_000_000, "B": 5_000_000}, 6.0),
        ("FSPL_dB = 20 log10(d_km) + 20 log10(f_MHz) + 32.44", {"d": 2, "f": 2400}, 106.064825),
        ("SINR = S / (I + N)", {"S": 1, "I": 0.2, "N": 0.1}, 3.333333),
        ("P_out = 1 - exp(-gamma_th / gamma_bar)", {"gamma_th": 5, "gamma_bar": 10}, 0.393469),
        ("P_b = Q(sqrt(2 Eb/N0_linear))", {"eb_n0_db": 9}, 3.362723e-05),
        ("R_s <= 2B", {"B": 3000}, 6000.0),
        ("C = log2 det(I + rho / Nt * H H^H)", {"rho": 10, "Nt": 2, "H": "identity"}, 5.169925),
        ("Pr = Pt Gt Gr (lambda / (4 pi d))^2", {"Pt": 1, "Gt": 1, "Gr": 1, "lambda": 0.125, "d": 100}, 9.894647e-09),
        ("SNR_linear = 10^(SNR_dB / 10)", {"snr_db": 13}, 19.952623),
    ]
    for formula, variables, expected in cases:
        value, _ = execute(formula, variables)
        assert abs(value - expected) <= max(abs(expected) * 1e-5, 1e-9)
