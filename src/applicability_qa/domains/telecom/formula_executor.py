from __future__ import annotations

import math


def execute(formula_id: str, variables: dict) -> tuple[float, str]:
    key = formula_id.lower()
    if "shannon" in key or "log2(1 + snr" in key:
        bandwidth = float(variables.get("B", variables.get("bandwidth_hz")))
        snr = float(variables.get("snr_linear", variables.get("SNR_linear", variables.get("SNR"))))
        if variables.get("snr_db") is not None:
            snr = 10 ** (float(variables["snr_db"]) / 10)
        return bandwidth * math.log2(1 + snr), "bps"
    if "friis" in key or "pr = pt" in key:
        distance = variables.get("d", variables.get("R", variables.get("distance_m")))
        wavelength = variables.get("lambda", variables.get("wavelength"))
        return float(variables["Pt"]) * float(variables["Gt"]) * float(variables["Gr"]) * (float(wavelength) / (4 * math.pi * float(distance))) ** 2, "W"
    if "eta = c / b" in key or "spectral efficiency" in key:
        capacity = float(variables.get("C", variables.get("capacity_bps")))
        bandwidth = float(variables.get("B", variables.get("bandwidth_hz")))
        if capacity >= 1e6 and bandwidth < 1e4:
            bandwidth *= 1e6
        return capacity / bandwidth, "bps/Hz"
    if "free-space" in key or "fspl" in key:
        if "d_km" in key or "f_mhz" in key:
            distance = float(variables.get("d", variables.get("d_km", variables.get("distance_km"))))
            frequency = float(variables.get("f", variables.get("f_MHz", variables.get("frequency_mhz"))))
            return 20 * math.log10(distance) + 20 * math.log10(frequency) + 32.44, "dB"
        distance = float(variables.get("distance_m", variables.get("d")))
        frequency = float(variables.get("frequency_hz", variables.get("f")))
        return 20 * math.log10(distance) + 20 * math.log10(frequency) - 147.55, "dB"
    if "sinr" in key and "s / (i + n)" in key:
        return float(variables["S"]) / (float(variables["I"]) + float(variables["N"])), "linear"
    if "1 - exp" in key and "gamma" in key:
        threshold = float(variables["gamma_th"])
        average = float(variables["gamma_bar"])
        return 1 - math.exp(-threshold / average), "probability"
    if "q(sqrt(2" in key or "bpsk" in key:
        ratio = variables.get("eb_n0_linear", variables.get("Eb/N0_linear"))
        if ratio is None:
            ratio = 10 ** (float(variables.get("eb_n0_db", variables.get("Eb/N0"))) / 10)
        return 0.5 * math.erfc(math.sqrt(float(ratio))), "probability"
    if "r_s <= 2b" in key or "nyquist" in key:
        return 2 * float(variables.get("B", variables.get("bandwidth_hz"))), "symbols/s"
    if "log2 det" in key and "h h^h" in key:
        rho = float(variables["rho"])
        antennas = int(variables["Nt"])
        if str(variables.get("H", "identity")).lower() not in {"identity", "2x2 identity", "i"}:
            raise ValueError("Only identity MIMO matrices are supported")
        return antennas * math.log2(1 + rho / antennas), "bps/Hz"
    if "10^(snr_db / 10)" in key or "snr_linear" in key and "10^" in key:
        return 10 ** (float(variables.get("snr_db", variables.get("SNR"))) / 10), "linear"
    raise ValueError(f"Unsupported telecom formula: {formula_id}")
