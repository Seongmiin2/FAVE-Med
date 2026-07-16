from __future__ import annotations

import re

from ...core.signatures import EvidenceSignature


RULES = {
    "body_mass_index": (r"\bbmi\b|body mass", ["weight_kg", "height_m"], ["metric_bmi"], ["square_height_m"], r"meters squared"),
    "mean_arterial_pressure": (r"\bmap\b|mean arterial", ["systolic_bp", "diastolic_bp"], ["resting_map_approximation"], ["weight_diastolic_twice"], r"twice diastolic"),
    "anion_gap": (r"anion gap", ["sodium", "chloride", "bicarbonate"], ["potassium_excluding"], ["exclude_potassium"], r"potassium-excluding"),
    "cockcroft_gault": (r"cockcroft|creatinine clearance", ["age_years", "weight_kg", "serum_creatinine", "sex"], ["female_factor_0_85", "weight_policy_explicit"], ["apply_sex_coefficient", "select_weight_policy"], r"0\.85 female coefficient"),
    "corrected_calcium": (r"corrected calcium", ["calcium_mg_dl", "albumin_g_dl"], ["coefficient_0_8", "albumin_reference_4"], ["add_albumin_correction"], r"adds 0\.8 times four minus albumin"),
    "body_surface_area_mosteller": (r"mosteller|\bbsa\b", ["height_cm", "weight_kg"], ["mosteller"], ["square_root"], r"square root"),
    "serum_osmolality": (r"serum osmolality", ["sodium", "glucose_mg_dl", "bun_mg_dl"], ["us_conventional_units"], ["apply_glucose_bun_divisors"], r"divided by 18.*divided by 2\.8"),
    "fractional_excretion_sodium": (r"\bfena\b|fractional excretion", ["urine_sodium", "plasma_creatinine", "plasma_sodium", "urine_creatinine"], ["paired_samples"], ["preserve_urine_plasma_binding"], r"urine sodium times plasma creatinine.*plasma sodium times urine creatinine"),
    "qtc_bazett": (r"bazett|\bqtc\b", ["qt_seconds", "rr_seconds"], ["bazett"], ["divide_by_sqrt_rr"], r"divides qt.*square root of rr"),
    "meld_na": (r"meld-na|meld.*sodium", ["meld_i", "sodium"], ["meld_na_2016"], ["clamp_sodium_125_137", "clamp_meld_6_40"], r"standard sodium and meld clamps"),
}

CANONICAL_UNITS = {
    "body_mass_index": {"weight_kg": "kg", "height_m": "m"},
    "mean_arterial_pressure": {"systolic_bp": "mmHg", "diastolic_bp": "mmHg"},
    "corrected_calcium": {"calcium_mg_dl": "mg/dL", "albumin_g_dl": "g/dL"},
    "body_surface_area_mosteller": {"height_cm": "cm", "weight_kg": "kg"},
    "qtc_bazett": {"qt_seconds": "s", "rr_seconds": "s"},
}


def _text(evidence) -> tuple[str, str]:
    if isinstance(evidence, dict):
        return str(evidence.get("evidence_id") or evidence.get("id") or "evidence"), str(evidence.get("text", ""))
    return str(getattr(evidence, "evidence_id", None) or getattr(evidence, "id", "evidence")), str(getattr(evidence, "text", ""))


def parse_evidence_signature(evidence, question: str = "", patient_context: str | None = None) -> EvidenceSignature:
    evidence_id, original = _text(evidence)
    text = original.lower()
    match = next(((name, rule) for name, rule in RULES.items() if re.search(rule[0], text)), None)
    if match is None:
        return EvidenceSignature(evidence_id=evidence_id, source_type="text_only_rule_parser")
    calculator_id, (_, variables, expected_tags, expected_steps, positive_pattern) = match
    negated = bool(re.search(r"without|never|does not|simple average|swaps|subtracts|always add|multiplies", text))
    positive = bool(re.search(positive_pattern, text)) and not negated
    units = CANONICAL_UNITS.get(calculator_id, {}) if positive else {}
    return EvidenceSignature(evidence_id=evidence_id, asserted_formula_id=calculator_id, variables=variables, variable_units=units, convention_tags=expected_tags if positive else [], procedural_steps=expected_steps if positive else [], facts={}, factuality_claim="unverified", source_type="text_only_rule_parser")
