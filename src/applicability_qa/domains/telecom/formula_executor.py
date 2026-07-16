from __future__ import annotations

import math
from collections.abc import Callable


def _value(variables: dict, *names: str) -> float:
    for name in names:
        if variables.get(name) is not None:
            return float(variables[name])
    raise ValueError(f"Missing required variable; expected one of {names}")


def execute_shannon_capacity(v: dict) -> tuple[float, str]:
    bandwidth = _value(v, "B", "bandwidth_hz")
    snr = 10 ** (_value(v, "snr_db") / 10) if v.get("snr_db") is not None else _value(v, "snr_linear", "SNR_linear", "SNR")
    if bandwidth <= 0 or snr < 0:
        raise ValueError("Bandwidth must be positive and linear SNR non-negative")
    return bandwidth * math.log2(1 + snr), "bps"


def execute_spectral_efficiency(v: dict) -> tuple[float, str]:
    capacity, bandwidth = _value(v, "C", "capacity_bps"), _value(v, "B", "bandwidth_hz")
    if bandwidth <= 0:
        raise ValueError("Bandwidth must be positive")
    return capacity / bandwidth, "bps/Hz"


def execute_free_space_path_loss(v: dict) -> tuple[float, str]:
    distance, frequency = _value(v, "d_km", "d", "distance_km"), _value(v, "f_MHz", "f", "frequency_mhz")
    if distance <= 0 or frequency <= 0:
        raise ValueError("Distance and frequency must be positive")
    return 20 * math.log10(distance) + 20 * math.log10(frequency) + 32.44, "dB"


def execute_sinr(v: dict) -> tuple[float, str]:
    denominator = _value(v, "I") + _value(v, "N")
    if denominator <= 0:
        raise ValueError("Interference plus noise must be positive")
    return _value(v, "S") / denominator, "linear"


def execute_rayleigh_outage(v: dict) -> tuple[float, str]:
    threshold, average = _value(v, "gamma_th"), _value(v, "gamma_bar")
    if threshold < 0 or average <= 0:
        raise ValueError("Threshold must be non-negative and average SNR positive")
    return 1 - math.exp(-threshold / average), "probability"


def execute_bpsk_ber(v: dict) -> tuple[float, str]:
    ratio = _value(v, "eb_n0_linear", "Eb/N0_linear") if v.get("eb_n0_linear") is not None or v.get("Eb/N0_linear") is not None else 10 ** (_value(v, "eb_n0_db", "Eb/N0") / 10)
    if ratio < 0:
        raise ValueError("Eb/N0 must be non-negative")
    return 0.5 * math.erfc(math.sqrt(ratio)), "probability"


def execute_nyquist_symbol_rate(v: dict) -> tuple[float, str]:
    bandwidth = _value(v, "B", "bandwidth_hz")
    if bandwidth <= 0:
        raise ValueError("Bandwidth must be positive")
    return 2 * bandwidth, "symbols/s"


def execute_mimo_capacity_identity(v: dict) -> tuple[float, str]:
    rho, antennas = _value(v, "rho"), int(_value(v, "Nt"))
    matrix = v.get("H", "identity")
    if matrix not in ([[1, 0], [0, 1]], [[1.0, 0.0], [0.0, 1.0]]) and str(matrix).lower() not in {"identity", "2x2 identity", "i"}:
        raise ValueError("Only identity MIMO matrices are supported")
    if rho < 0 or antennas <= 0:
        raise ValueError("SNR must be non-negative and antenna count positive")
    return antennas * math.log2(1 + rho / antennas), "bps/Hz"


def execute_friis_received_power(v: dict) -> tuple[float, str]:
    distance, wavelength = _value(v, "d", "R", "distance_m"), _value(v, "lambda", "wavelength")
    if distance <= 0 or wavelength <= 0:
        raise ValueError("Distance and wavelength must be positive")
    return _value(v, "Pt") * _value(v, "Gt") * _value(v, "Gr") * (wavelength / (4 * math.pi * distance)) ** 2, "W"


def execute_snr_db_to_linear(v: dict) -> tuple[float, str]:
    return 10 ** (_value(v, "snr_db", "SNR_dB", "SNR") / 10), "linear"


EXECUTORS: dict[str, Callable[[dict], tuple[float, str]]] = {
    "shannon_capacity": execute_shannon_capacity,
    "spectral_efficiency": execute_spectral_efficiency,
    "free_space_path_loss": execute_free_space_path_loss,
    "sinr": execute_sinr,
    "rayleigh_outage": execute_rayleigh_outage,
    "bpsk_ber": execute_bpsk_ber,
    "nyquist_symbol_rate": execute_nyquist_symbol_rate,
    "mimo_capacity_identity": execute_mimo_capacity_identity,
    "friis_received_power": execute_friis_received_power,
    "snr_db_to_linear": execute_snr_db_to_linear,
}


def execute(formula_id: str, variables: dict) -> tuple[float, str]:
    try:
        executor = EXECUTORS[formula_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported telecom formula ID: {formula_id}") from exc
    return executor(variables)
