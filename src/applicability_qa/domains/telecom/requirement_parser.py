from __future__ import annotations

from ...core.signature_builders import requirement_from_formula
from ...core.signatures import ConditionPredicate, RequirementSignature


RULES = {
    "shannon_capacity": {"tags": ["linear_power_ratio"], "steps": ["convert_snr_to_linear"]},
    "spectral_efficiency": {"tags": ["base_units"], "steps": ["normalize_bandwidth_hz"]},
    "free_space_path_loss": {"tags": ["distance_km_frequency_mhz"], "steps": ["use_32_44_constant"]},
    "sinr": {"tags": ["include_interference_and_noise"], "steps": ["sum_interference_and_noise"]},
    "rayleigh_outage": {"tags": ["exact_rayleigh"], "steps": ["use_exponential"]},
    "bpsk_ber": {"tags": ["coherent_bpsk_awgn", "linear_eb_n0"], "steps": ["convert_eb_n0_to_linear"]},
    "nyquist_symbol_rate": {"tags": ["ideal_noiseless_baseband"], "steps": ["normalize_bandwidth_hz"]},
    "mimo_capacity_identity": {"tags": ["total_snr"], "steps": ["divide_total_snr_by_nt"]},
    "friis_received_power": {"tags": ["free_space_los"], "steps": ["square_propagation_factor"]},
    "snr_db_to_linear": {"tags": ["power_ratio_db"], "steps": ["divide_db_by_10"]},
}


def parse_requirement(question: str, spec) -> RequirementSignature:
    signature = requirement_from_formula(spec)
    rule = RULES.get(spec.formula_id, {})
    signature.convention_tags = rule.get("tags", [])
    signature.required_procedural_steps = rule.get("steps", [])
    signature.physical_constraints = [ConditionPredicate(field=row.name, operator="gt", value=0, description=f"{row.name} must be positive") for row in spec.required_variables if row.canonical_unit not in {"dB", "linear", "dimensionless"}]
    return signature
