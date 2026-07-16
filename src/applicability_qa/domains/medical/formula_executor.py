from __future__ import annotations

import math
from collections.abc import Callable


def number(e: dict, name: str) -> float:
    if e.get(name) is None:
        raise ValueError(f"Missing required entity: {name}")
    return float(e[name])


def bmi(e):
    w, h = number(e, "weight_kg"), number(e, "height_m")
    if w <= 0 or h <= 0 or h > 3:
        raise ValueError("Weight and height must be positive SI values")
    return w / h**2, "kg/m^2"


def map_score(e):
    sbp, dbp = number(e, "systolic_bp"), number(e, "diastolic_bp")
    if sbp <= dbp or dbp <= 0:
        raise ValueError("Blood pressure values are impossible")
    return (sbp + 2 * dbp) / 3, "mmHg"


def anion_gap(e):
    return number(e, "sodium") - number(e, "chloride") - number(e, "bicarbonate"), "mEq/L"


def cockcroft_gault(e):
    age, weight, scr = number(e, "age_years"), number(e, "weight_kg"), number(e, "serum_creatinine")
    sex = str(e.get("sex", "")).lower()
    if age < 0 or weight <= 0 or scr <= 0 or sex not in {"male", "female"}:
        raise ValueError("Age, weight, creatinine, and binary formula sex branch are required")
    return ((140 - age) * weight / (72 * scr)) * (0.85 if sex == "female" else 1), "mL/min"


def corrected_calcium(e):
    return number(e, "calcium_mg_dl") + 0.8 * (4 - number(e, "albumin_g_dl")), "mg/dL"


def bsa(e):
    height, weight = number(e, "height_cm"), number(e, "weight_kg")
    if height <= 0 or weight <= 0:
        raise ValueError("Height and weight must be positive")
    return math.sqrt(height * weight / 3600), "m^2"


def osmolality(e):
    return 2 * number(e, "sodium") + number(e, "glucose_mg_dl") / 18 + number(e, "bun_mg_dl") / 2.8, "mOsm/kg"


def fena(e):
    denominator = number(e, "plasma_sodium") * number(e, "urine_creatinine")
    if denominator <= 0:
        raise ValueError("FENa denominator must be positive")
    return 100 * number(e, "urine_sodium") * number(e, "plasma_creatinine") / denominator, "%"


def qtc(e):
    qt, rr = number(e, "qt_seconds"), number(e, "rr_seconds")
    if qt <= 0 or rr <= 0:
        raise ValueError("QT and RR must be positive seconds")
    return qt / math.sqrt(rr), "s"


def meld_na(e):
    meld = min(40, max(6, number(e, "meld_i")))
    sodium = min(137, max(125, number(e, "sodium")))
    return round(meld + 1.32 * (137 - sodium) - 0.033 * meld * (137 - sodium)), "score"


MEDICAL_EXECUTORS: dict[str, Callable[[dict], tuple[float, str]]] = {
    "body_mass_index": bmi, "mean_arterial_pressure": map_score, "anion_gap": anion_gap,
    "cockcroft_gault": cockcroft_gault, "corrected_calcium": corrected_calcium,
    "body_surface_area_mosteller": bsa, "serum_osmolality": osmolality,
    "fractional_excretion_sodium": fena, "qtc_bazett": qtc, "meld_na": meld_na,
}


def execute(calculator_id: str, entities: dict) -> tuple[float, str]:
    try:
        return MEDICAL_EXECUTORS[calculator_id](entities)
    except KeyError as exc:
        raise ValueError(f"Unsupported medical calculator ID: {calculator_id}") from exc
