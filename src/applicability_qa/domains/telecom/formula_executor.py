from __future__ import annotations

import math


def execute(formula_id: str, variables: dict) -> tuple[float, str]:
    key = formula_id.lower()
    if "shannon" in key or "log2(1 + snr" in key:
        bandwidth = float(variables.get("B", variables.get("bandwidth_hz")))
        snr = float(variables.get("snr_linear", variables.get("SNR")))
        if variables.get("snr_db") is not None:
            snr = 10 ** (float(variables["snr_db"]) / 10)
        return bandwidth * math.log2(1 + snr), "bps"
    if "friis" in key:
        return float(variables["Pt"]) * float(variables["Gt"]) * float(variables["Gr"]) * (float(variables["wavelength"]) / (4 * math.pi * float(variables["R"]))) ** 2, "W"
    if "eta = c / b" in key or "spectral efficiency" in key:
        capacity = float(variables.get("C", variables.get("capacity_bps")))
        bandwidth = float(variables.get("B", variables.get("bandwidth_hz")))
        return capacity / bandwidth, "bps/Hz"
    if "free-space" in key or "fspl" in key:
        if "d_km" in key or "f_mhz" in key:
            distance = float(variables.get("d", variables.get("distance_km")))
            frequency = float(variables.get("f", variables.get("frequency_mhz")))
            return 20 * math.log10(distance) + 20 * math.log10(frequency) + 32.44, "dB"
        distance = float(variables.get("distance_m", variables.get("d")))
        frequency = float(variables.get("frequency_hz", variables.get("f")))
        return 20 * math.log10(distance) + 20 * math.log10(frequency) - 147.55, "dB"
    raise ValueError(f"Unsupported telecom formula: {formula_id}")
