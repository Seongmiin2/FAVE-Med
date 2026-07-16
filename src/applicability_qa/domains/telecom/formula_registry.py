from __future__ import annotations

import json
from pathlib import Path

from ...core.schemas import TelecomFormulaSpec

DEFAULT_REGISTRY = Path(__file__).resolve().parents[4] / "data" / "telecom" / "formulas" / "formula_registry.json"


def load_formula_registry(path: str | Path = DEFAULT_REGISTRY) -> list[TelecomFormulaSpec]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    registry = [TelecomFormulaSpec.model_validate(_upgrade_legacy(row)) for row in rows]
    ids = [row.formula_id for row in registry]
    if len(ids) != len(set(ids)):
        raise ValueError("Formula registry IDs must be unique")
    return registry


def _upgrade_legacy(row: dict) -> dict:
    """Keep historical registries readable while exposing a strict typed API."""
    if "required_variables" in row and "output" in row:
        return row
    variable_names = {
        "shannon_capacity": [("B", "bandwidth", "Hz"), ("snr_linear", "signal_to_noise_ratio", "linear")],
        "spectral_efficiency": [("C", "data_rate", "bps"), ("B", "bandwidth", "Hz")],
        "free_space_path_loss": [("d_km", "distance", "km"), ("f_MHz", "frequency", "MHz")],
        "sinr": [("S", "signal_power", "W"), ("I", "interference_power", "W"), ("N", "noise_power", "W")],
        "rayleigh_outage": [("gamma_th", "snr_threshold", "linear"), ("gamma_bar", "average_snr", "linear")],
        "bpsk_ber": [("eb_n0_linear", "energy_per_bit_to_noise_density", "linear")],
        "nyquist_symbol_rate": [("B", "bandwidth", "Hz")],
        "mimo_capacity_identity": [("rho", "total_snr", "linear"), ("Nt", "transmit_antenna_count", "count"), ("H", "channel_matrix", "dimensionless")],
        "friis_received_power": [("Pt", "transmit_power", "W"), ("Gt", "transmit_gain", "linear"), ("Gr", "receive_gain", "linear"), ("lambda", "wavelength", "m"), ("d", "distance", "m")],
        "snr_db_to_linear": [("snr_db", "signal_to_noise_ratio", "dB")],
    }
    outputs = {
        "shannon_capacity": ("capacity", "bps"), "spectral_efficiency": ("spectral_efficiency", "bps/Hz"),
        "free_space_path_loss": ("path_loss", "dB"), "sinr": ("sinr", "linear"),
        "rayleigh_outage": ("outage_probability", "probability"), "bpsk_ber": ("bit_error_rate", "probability"),
        "nyquist_symbol_rate": ("symbol_rate", "symbols/s"), "mimo_capacity_identity": ("spectral_efficiency", "bps/Hz"),
        "friis_received_power": ("received_power", "W"), "snr_db_to_linear": ("signal_to_noise_ratio", "linear"),
    }
    formula_id = row["formula_id"]
    upgraded = dict(row)
    upgraded["executor_name"] = formula_id
    runtime_aliases = {
        "free_space_path_loss": {"d_km": ["d"], "f_MHz": ["f"]},
        "bpsk_ber": {"eb_n0_linear": ["eb_n0_db"]},
    }
    upgraded["required_variables"] = [{"name": name, "quantity": quantity, "canonical_unit": unit, "accepted_aliases": runtime_aliases.get(formula_id, {}).get(name, [])} for name, quantity, unit in variable_names[formula_id]]
    quantity, unit = outputs[formula_id]
    upgraded["output"] = {"quantity": quantity, "canonical_unit": unit}
    upgraded["applicability_conditions"] = []
    upgraded["unsupported_conditions"] = []
    return upgraded


def formula_by_id(formula_id: str, registry: list[TelecomFormulaSpec]) -> TelecomFormulaSpec | None:
    return next((row for row in registry if row.formula_id == formula_id), None)
