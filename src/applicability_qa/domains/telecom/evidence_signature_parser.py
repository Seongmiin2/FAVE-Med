from __future__ import annotations

import re

from ...core.signatures import EvidenceSignature


FORMULAS = {
    "shannon_capacity": (r"shannon|log2\s*\(1\s*\+\s*snr", ["B", "snr_linear"]),
    "spectral_efficiency": (r"spectral efficiency|throughput.*divided by bandwidth", ["C", "B"]),
    "free_space_path_loss": (r"free[- ]space path loss|32\.44", ["d_km", "f_MHz"]),
    "sinr": (r"\bsinr\b", ["S", "I", "N"]),
    "rayleigh_outage": (r"rayleigh.*outage|outage probability.*exp", ["gamma_th", "gamma_bar"]),
    "bpsk_ber": (r"bpsk.*ber|q of sqrt", ["eb_n0_linear"]),
    "nyquist_symbol_rate": (r"nyquist.*symbol|symbol-rate limit", ["B"]),
    "mimo_capacity_identity": (r"mimo.*capacity|rho divided by nt", ["rho", "Nt", "H"]),
    "friis_received_power": (r"friis|received power.*lambda", ["Pt", "Gt", "Gr", "lambda", "d"]),
    "snr_db_to_linear": (r"convert.*snr.*db.*linear|ten raised to snr", ["snr_db"]),
}

POSITIVE = {
    "shannon_capacity": ((r"linear power ratio", ["linear_power_ratio"]), (r"linear|converted", ["convert_snr_to_linear"])),
    "spectral_efficiency": ((r"bits per second.*hertz", ["base_units"]), (r"bandwidth in hertz", ["normalize_bandwidth_hz"])),
    "free_space_path_loss": ((r"distance_km.*frequency_mhz|distance.*km.*frequency.*mhz", ["distance_km_frequency_mhz"]), (r"32\.44", ["use_32_44_constant"])),
    "sinr": ((r"interference.*noise", ["include_interference_and_noise"]), (r"sum of interference.*noise", ["sum_interference_and_noise"])),
    "rayleigh_outage": ((r"one minus exp", ["exact_rayleigh"]), (r"one minus exp", ["use_exponential"])),
    "bpsk_ber": ((r"coherent bpsk.*awgn|awgn.*q", ["coherent_bpsk_awgn", "linear_eb_n0"]), (r"converted to linear", ["convert_eb_n0_to_linear"])),
    "nyquist_symbol_rate": ((r"ideal noiseless baseband", ["ideal_noiseless_baseband"]), (r"bandwidth in hertz", ["normalize_bandwidth_hz"])),
    "mimo_capacity_identity": ((r"total snr convention", ["total_snr"]), (r"rho divided by nt", ["divide_total_snr_by_nt"])),
    "friis_received_power": ((r"friis|free-space", ["free_space_los"]), (r"squared factor", ["square_propagation_factor"])),
    "snr_db_to_linear": ((r"power ratio", ["power_ratio_db"]), (r"divided by ten", ["divide_db_by_10"])),
}

def _units(formula_id: str | None, text: str) -> dict[str, str]:
    if formula_id == "shannon_capacity":
        return {"B": "Hz", "snr_linear": "linear" if "linear" in text else "dB" if "db" in text else "unknown"}
    if formula_id == "spectral_efficiency":
        return {"C": "bps", "B": "MHz" if "mhz" in text else "Hz"}
    if formula_id == "free_space_path_loss":
        return {"d_km": "km", "f_MHz": "GHz" if "ghz" in text else "MHz"}
    if formula_id in {"sinr", "friis_received_power"}:
        return {}
    if formula_id in {"rayleigh_outage", "bpsk_ber"}:
        return {name: "dB" if "db" in text and "converted" not in text else "linear" for name in FORMULAS[formula_id][1]}
    if formula_id == "nyquist_symbol_rate":
        return {"B": "Hz"}
    if formula_id == "snr_db_to_linear":
        return {"snr_db": "dB"}
    return {}


def _text(evidence) -> tuple[str, str]:
    if isinstance(evidence, dict):
        return str(evidence.get("evidence_id") or evidence.get("id") or "evidence"), str(evidence.get("text", ""))
    return str(getattr(evidence, "evidence_id", None) or getattr(evidence, "id", "evidence")), str(getattr(evidence, "text", ""))


def parse_evidence_signature(evidence, question: str = "", patient_context: str | None = None) -> EvidenceSignature:
    evidence_id, original = _text(evidence)
    text = original.lower()
    formula_id = next((name for name, (pattern, _) in FORMULAS.items() if re.search(pattern, text)), None)
    variables = [] if formula_id is None else FORMULAS[formula_id][1]
    tags, steps = [], []
    if formula_id in POSITIVE:
        (tag_pattern, tag_values), (step_pattern, step_values) = POSITIVE[formula_id]
        if re.search(tag_pattern, text):
            tags.extend(tag_values)
        if re.search(step_pattern, text):
            steps.extend(step_values)
    variable_units = _units(formula_id, text)
    return EvidenceSignature(evidence_id=evidence_id, asserted_formula_id=formula_id, variables=variables, variable_units=variable_units, convention_tags=tags, procedural_steps=steps, facts={}, factuality_claim="unverified", source_type="text_only_rule_parser")
