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
        if not callable(self.response):
            for marker, answer, unit, variables in fixtures:
                if marker in user_prompt:
                    return {
                        "answer": {"final_value": answer, "final_unit": unit},
                        "extracted_variables": variables,
                        "verification": {"unit_check": "pass", "condition_check": "pass", "variable_check": "pass"},
                    }
        value = self.response(system_prompt, user_prompt) if callable(self.response) else self.response
        return dict(value)
