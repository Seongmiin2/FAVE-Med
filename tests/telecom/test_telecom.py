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
