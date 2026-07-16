from __future__ import annotations

from collections.abc import Callable
import json
import re

from .base import LLMProvider


class MockProvider(LLMProvider):
    def __init__(self, response: dict | Callable[[str, str], dict] | None = None):
        self.response = response or {
            "answer": {"final_value": 66.582115, "final_unit": "Mbps"},
            "extracted_variables": {"B": 10_000_000, "snr_linear": 100},
            "verification": {
                "unit_check": "pass",
                "condition_check": "pass",
                "variable_check": "pass",
            },
        }

    def generate_json(self, system_prompt: str, user_prompt: str, schema: dict | None = None) -> dict:
        if system_prompt.startswith("Classify evidence") or "Relevance is not sufficient for applicability" in system_prompt:
            evidence_ids = []
            if user_prompt.lstrip().startswith("{"):
                try:
                    evidence_ids = [row["id"] for row in json.loads(user_prompt).get("candidate_evidence", [])]
                except (json.JSONDecodeError, TypeError, KeyError):
                    evidence_ids = []
            if not evidence_ids:
                evidence_ids = re.findall(r"^(\S+):", user_prompt, re.MULTILINE)
            invalid_fixture_ids = {
                "ev_37b5d8", "ev_e8a264", "ev_9b79a5", "ev_d5f767", "ev_292289",
                "ev_107b9b", "ev_a50420", "ev_7d69ed", "ev_dca034", "ev_72b904",
            }
            rejected = [evidence_id for evidence_id in evidence_ids if evidence_id in invalid_fixture_ids or evidence_id.endswith("_trap")]
            return {
                "accepted_evidence_ids": [evidence_id for evidence_id in evidence_ids if evidence_id not in rejected],
                "rejected_evidence_ids": rejected,
            }
        fixtures = [
            ("Shannon capacity", 66.582115, "Mbps", {"B": 10_000_000, "snr_linear": 100}),
            ("A link has throughput", 6.0, "bps/Hz", {"C": 30_000_000, "B": 5_000_000}),
            ("Compute FSPL", 106.064825, "dB", {"d": 2, "f": 2400}),
            ("Compute SINR", 3.333333, "linear", {"S": 1, "I": 0.2, "N": 0.1}),
            ("outage probability", 0.393469, "probability", {"gamma_th": 5, "gamma_bar": 10}),
            ("compute the BER", 3.362723e-05, "probability", {"eb_n0_db": 9}),
            ("Nyquist symbol-rate", 6000.0, "symbols/s", {"B": 3000}),
            ("identity MIMO", 5.169925, "bps/Hz", {"rho": 10, "Nt": 2, "H": "identity"}),
            ("Compute received power", 9.894647e-09, "W", {"Pt": 1, "Gt": 1, "Gr": 1, "lambda": 0.125, "d": 100}),
            ("Convert SNR", 19.952623, "linear", {"snr_db": 13}),
        ]
        if system_prompt.startswith("Extract independent runtime facts"):
            formula_rules = {
                "Shannon capacity": ("shannon_capacity", ["linear_power_ratio"], ["convert_snr_to_linear"], {"B": "Hz", "snr_linear": "linear"}),
                "A link has throughput": ("spectral_efficiency", ["base_units"], ["normalize_bandwidth_hz"], {"C": "bps", "B": "Hz"}),
                "Compute FSPL": ("free_space_path_loss", ["distance_km_frequency_mhz"], ["use_32_44_constant"], {"d": "km", "f": "MHz"}),
                "Compute SINR": ("sinr", ["include_interference_and_noise"], ["sum_interference_and_noise"], {"S": "W", "I": "W", "N": "W"}),
                "outage probability": ("rayleigh_outage", ["exact_rayleigh"], ["use_exponential"], {"gamma_th": "linear", "gamma_bar": "linear"}),
                "compute the BER": ("bpsk_ber", ["coherent_bpsk_awgn", "linear_eb_n0"], ["convert_eb_n0_to_linear"], {"eb_n0_db": "dB"}),
                "Nyquist symbol-rate": ("nyquist_symbol_rate", ["ideal_noiseless_baseband"], ["normalize_bandwidth_hz"], {"B": "Hz"}),
                "identity MIMO": ("mimo_capacity_identity", ["total_snr"], ["divide_total_snr_by_nt"], {"rho": "linear", "Nt": "count", "H": "dimensionless"}),
                "Compute received power": ("friis_received_power", ["free_space_los"], ["square_propagation_factor"], {"Pt": "W", "Gt": "linear", "Gr": "linear", "lambda": "m", "d": "m"}),
                "Convert SNR": ("snr_db_to_linear", ["power_ratio_db"], ["divide_db_by_10"], {"snr_db": "dB"}),
            }
            for marker, _, _, variables in fixtures:
                if marker in user_prompt:
                    formula, tags, steps, units = formula_rules[marker]
                    return {"runtime_facts": {"variables": {name: {"observed_value": value, "observed_unit": units.get(name), "normalized_value": value, "normalized_unit": units.get(name), "conversion_operation": "identity", "source_span": f"{name}={value} {units.get(name, '')}".strip(), "confidence": 1.0} for name, value in variables.items()}, "asserted_formula_id": formula, "convention_tags": tags, "procedural_steps": steps, "conditions": {}}}
            return {"runtime_facts": {"variables": {}, "asserted_formula_id": None, "convention_tags": [], "procedural_steps": [], "conditions": {}}}
        if not callable(self.response):
            question_match = re.search(r"^Question:\s*(.+)$", user_prompt, re.MULTILINE)
            fixture_text = question_match.group(1) if question_match else user_prompt
            for marker, answer, unit, variables in fixtures:
                if marker in fixture_text:
                    return {
                        "answer": {"final_value": answer, "final_unit": unit},
                        "extracted_variables": variables,
                        "verification": {"unit_check": "pass", "condition_check": "pass", "variable_check": "pass"},
                    }
        value = self.response(system_prompt, user_prompt) if callable(self.response) else self.response
        return dict(value)
