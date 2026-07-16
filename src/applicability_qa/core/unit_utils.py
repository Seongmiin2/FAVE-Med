from __future__ import annotations

import math

GROUPS = {
    "rate": {"bps": 1.0, "kbps": 1e3, "Mbps": 1e6, "Gbps": 1e9},
    "frequency": {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9},
    "power": {"W": 1.0, "mW": 1e-3, "uW": 1e-6, "µW": 1e-6, "nW": 1e-9},
}
ALIASES = {
    "mbps": "Mbps",
    "gbps": "Gbps",
    "khz": "kHz",
    "mhz": "MHz",
    "ghz": "GHz",
    "db": "dB",
    "dbm": "dBm",
    "linear ratio": "linear",
    "linear scale": "linear",
    "ber": "probability",
    "symbols per second": "symbols/s",
    "symbol/s": "symbols/s",
    "bits/s/hz": "bps/Hz",
    "bit/s/hz": "bps/Hz",
}


def canonical_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    return ALIASES.get(unit.strip().lower(), unit.strip())


def convert_value(value: float, source: str | None, target: str | None) -> tuple[float | None, bool]:
    source, target = canonical_unit(source), canonical_unit(target)
    if not target or source == target:
        return value, source is None and target is not None
    if source is None:
        return value, True
    for units in GROUPS.values():
        if source in units and target in units:
            return value * units[source] / units[target], False
    if source == "dBm" and target in GROUPS["power"]:
        watts = 10 ** ((value - 30) / 10)
        return watts / GROUPS["power"][target], False
    return None, False


def close_to(value: float | None, target: float, relative: float = 0.01, absolute: float = 1e-6) -> bool:
    return value is not None and math.isclose(value, target, rel_tol=relative, abs_tol=absolute)
