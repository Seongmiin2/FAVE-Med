from __future__ import annotations

from ...core.signature_builders import requirement_from_formula
from ...core.signatures import ConditionPredicate, RequirementSignature


RULES = {
    "body_mass_index": (["metric_bmi"], ["square_height_m"]),
    "mean_arterial_pressure": (["resting_map_approximation"], ["weight_diastolic_twice"]),
    "anion_gap": (["potassium_excluding"], ["exclude_potassium"]),
    "cockcroft_gault": (["female_factor_0_85", "weight_policy_explicit"], ["apply_sex_coefficient", "select_weight_policy"]),
    "corrected_calcium": (["coefficient_0_8", "albumin_reference_4"], ["add_albumin_correction"]),
    "body_surface_area_mosteller": (["mosteller"], ["square_root"]),
    "serum_osmolality": (["us_conventional_units"], ["apply_glucose_bun_divisors"]),
    "fractional_excretion_sodium": (["paired_samples"], ["preserve_urine_plasma_binding"]),
    "qtc_bazett": (["bazett"], ["divide_by_sqrt_rr"]),
    "meld_na": (["meld_na_2016"], ["clamp_sodium_125_137", "clamp_meld_6_40"]),
}


def parse_requirement(patient_note: str, question: str, spec) -> RequirementSignature:
    signature = requirement_from_formula(spec)
    tags, steps = RULES.get(spec.calculator_id, ([], []))
    signature.convention_tags = tags
    signature.required_procedural_steps = steps
    numeric = [row for row in spec.required_entities if row.canonical_unit != "categorical"]
    signature.physical_constraints = [ConditionPredicate(field=row.name, operator="gt", value=0, description=f"{row.name} must be positive") for row in numeric]
    if spec.calculator_id == "mean_arterial_pressure":
        signature.conditions.append(ConditionPredicate(field="systolic_bp", operator="gt", value={"field": "diastolic_bp"}, description="systolic pressure must exceed diastolic pressure"))
    return signature
