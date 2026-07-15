from __future__ import annotations

from collections.abc import Callable
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
        if system_prompt.startswith("Classify evidence"):
            evidence_ids = re.findall(r"^(\S+):", user_prompt, re.MULTILINE)
            rejected = [evidence_id for evidence_id in evidence_ids if "37b5d8" in evidence_id]
            return {
                "accepted_evidence_ids": [evidence_id for evidence_id in evidence_ids if evidence_id not in rejected],
                "rejected_evidence_ids": rejected,
            }
        value = self.response(system_prompt, user_prompt) if callable(self.response) else self.response
        return dict(value)
