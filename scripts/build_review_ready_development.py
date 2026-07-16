from __future__ import annotations

import json
from pathlib import Path

from applicability_qa.domains.medical.formula_executor import execute as execute_medical
from applicability_qa.domains.telecom.formula_executor import execute as execute_telecom


TELECOM = [
    ("shannon_capacity", [{"B": 2e6, "snr_linear": 10}, {"B": 5e6, "snr_linear": 20}, {"B": 8e6, "snr_linear": 5}], "Estimate the information-rate ceiling for a channel with B={B} Hz and linear SNR={snr_linear}.", "Use bandwidth in hertz and a linear SNR in C=B log2(1+SNR).", "Insert an SNR stated in dB directly into the logarithm."),
    ("spectral_efficiency", [{"C": 12e6, "B": 3e6}, {"C": 25e6, "B": 5e6}, {"C": 9e6, "B": 2e6}], "Determine bits per second per hertz when rate C={C} bps occupies B={B} Hz.", "Spectral efficiency is rate in bps divided by bandwidth in Hz.", "Leave bandwidth numerically in MHz while rate remains in bps."),
    ("free_space_path_loss", [{"d_km": 1, "f_MHz": 900}, {"d_km": 3, "f_MHz": 1800}, {"d_km": 0.5, "f_MHz": 2400}], "Find free-space attenuation for distance {d_km} km and frequency {f_MHz} MHz.", "With distance in km and frequency in MHz, FSPL uses the 32.44 dB constant.", "Use the 32.44 constant with frequency entered in GHz."),
    ("sinr", [{"S": 2, "I": .3, "N": .1}, {"S": 1, "I": .1, "N": .05}, {"S": 5, "I": 1, "N": .5}], "Compute SINR from signal {S} W, interference {I} W, and noise {N} W.", "SINR divides signal power by interference plus noise in compatible units.", "Ignore interference and divide signal only by noise."),
    ("rayleigh_outage", [{"gamma_th": 2, "gamma_bar": 8}, {"gamma_th": 4, "gamma_bar": 12}, {"gamma_th": 1, "gamma_bar": 5}], "Under Rayleigh fading, calculate outage for linear threshold {gamma_th} and mean SNR {gamma_bar}.", "Exact Rayleigh outage is one minus exp of negative threshold divided by mean SNR.", "Use threshold divided by mean SNR as an exact identity at every ratio."),
    ("bpsk_ber", [{"eb_n0_linear": 4}, {"eb_n0_linear": 8}, {"eb_n0_linear": 12}], "For coherent BPSK in AWGN, find BER at linear Eb/N0={eb_n0_linear}.", "Coherent BPSK in AWGN uses Q(sqrt(2 Eb/N0)) with linear Eb/N0.", "Feed an Eb/N0 value measured in dB directly to the Q-function."),
    ("nyquist_symbol_rate", [{"B": 1500}, {"B": 2500}, {"B": 4000}], "Give the ideal noiseless baseband symbol-rate limit for B={B} Hz.", "The Nyquist symbol-rate limit for an ideal noiseless baseband channel is twice bandwidth in Hz.", "Treat 3 kHz as 300 Hz before applying the limit."),
    ("mimo_capacity_identity", [{"rho": 6, "Nt": 2, "H": "identity"}, {"rho": 12, "Nt": 2, "H": "identity"}, {"rho": 9, "Nt": 2, "H": "identity"}], "For a 2x2 identity MIMO channel with total linear SNR rho={rho}, compute spectral efficiency.", "Under the total SNR convention, divide rho by Nt inside the identity-channel determinant.", "For total SNR, never divide rho by the transmit-antenna count."),
    ("friis_received_power", [{"Pt": 1, "Gt": 1, "Gr": 1, "lambda": .1, "d": 50}, {"Pt": 2, "Gt": 1, "Gr": 1, "lambda": .12, "d": 100}, {"Pt": .5, "Gt": 2, "Gr": 2, "lambda": .08, "d": 40}], "Using Friis free-space propagation, find received power for Pt={Pt} W, Gt={Gt}, Gr={Gr}, wavelength={lambda} m, distance={d} m.", "Friis received power squares the wavelength over four-pi-distance propagation factor.", "Apply the wavelength over four-pi-distance factor only once."),
    ("snr_db_to_linear", [{"snr_db": 3}, {"snr_db": 7}, {"snr_db": 15}], "Convert the power-ratio SNR of {snr_db} dB to linear scale.", "For a power ratio, convert dB with ten raised to dB divided by ten.", "Use a divisor of twenty in the exponent for this power ratio."),
]

MEDICAL = [
    ("body_mass_index", {"weight_kg": 72, "height_m": 1.8}, "Calculate BMI for a 72 kg adult who is 1.80 m tall.", "Estimate the standard weight-for-height index for a 72 kg adult of height 1.80 m."),
    ("mean_arterial_pressure", {"systolic_bp": 118, "diastolic_bp": 76}, "Calculate mean arterial pressure from 118/76 mmHg.", "Estimate average arterial driving pressure for blood pressure 118/76 mmHg."),
    ("anion_gap", {"sodium": 139, "chloride": 103, "bicarbonate": 23}, "Calculate the potassium-excluding anion gap: Na 139, Cl 103, HCO3 23 mEq/L.", "Quantify the unmeasured-ion gap from sodium 139, chloride 103, and bicarbonate 23 mEq/L, excluding potassium."),
    ("cockcroft_gault", {"age_years": 64, "weight_kg": 68, "serum_creatinine": 1.1, "sex": "female"}, "Calculate Cockcroft-Gault clearance for a 64-year-old female, 68 kg, creatinine 1.1 mg/dL.", "Estimate conventional creatinine clearance for a 64-year-old woman weighing 68 kg with serum creatinine 1.1 mg/dL."),
    ("corrected_calcium", {"calcium_mg_dl": 7.9, "albumin_g_dl": 2.5}, "Calculate corrected calcium for calcium 7.9 mg/dL and albumin 2.5 g/dL.", "Adjust measured calcium 7.9 mg/dL for albumin 2.5 g/dL using the conventional correction."),
    ("body_surface_area_mosteller", {"height_cm": 168, "weight_kg": 62}, "Calculate Mosteller BSA for 168 cm and 62 kg.", "Estimate body surface area using the square-root height-weight convention for 168 cm and 62 kg."),
    ("serum_osmolality", {"sodium": 138, "glucose_mg_dl": 108, "bun_mg_dl": 16}, "Calculate serum osmolality from Na 138, glucose 108 mg/dL, BUN 16 mg/dL.", "Estimate calculated plasma tonicity-related osmolality from sodium 138, glucose 108, and BUN 16 in conventional US units."),
    ("fractional_excretion_sodium", {"urine_sodium": 35, "plasma_creatinine": 1.8, "plasma_sodium": 140, "urine_creatinine": 90}, "Calculate FENa from paired UNa 35, PCr 1.8, PNa 140, UCr 90.", "Using paired urine and plasma samples, find the percentage of filtered sodium excreted: UNa 35, PCr 1.8, PNa 140, UCr 90."),
    ("qtc_bazett", {"qt_seconds": .38, "rr_seconds": .8}, "Calculate Bazett QTc for QT 0.38 s and RR 0.80 s.", "Apply the square-root RR heart-rate correction to QT 0.38 s with RR 0.80 s."),
    ("meld_na", {"meld_i": 18, "sodium": 129}, "Calculate 2016 MELD-Na from MELD(i)=18 and sodium 129 mEq/L.", "Apply the standard clamped sodium correction to a base liver score of 18 with sodium 129 mEq/L."),
]


def dump(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def main() -> None:
    telecom = []
    for family_index, (formula, variants, template, valid, incompatible) in enumerate(TELECOM):
        for variant, variables in enumerate(variants):
            value, unit = execute_telecom(formula, variables)
            difficulty = ("easy", "medium", "hard")[variant]
            item_id = f"tel-dev-{family_index + 1:02d}-{variant + 1}"
            telecom.append({"schema_version": "dev-candidate-0.1", "review_status": "pending_independent_review", "source": {"type": "project_authored", "license": "CC-BY-4.0"}, "runtime": {"id": item_id, "domain": "telecom", "question": template.format(**variables), "evidence": [{"id": f"e-{item_id}-a", "text": valid}, {"id": f"e-{item_id}-b", "text": incompatible}], "metadata": {"difficulty": difficulty, "template_group_id": f"tel-template-{family_index + 1:02d}"}}, "draft_gold_for_review": {"formula_id": formula, "answer": {"value": value, "unit": unit}, "required_variables": variables, "evidence_annotations": [{"evidence_id": f"e-{item_id}-a", "proposed_label": "applicable"}, {"evidence_id": f"e-{item_id}-b", "proposed_label": "true_but_inapplicable"}]}})
    medical = []
    for index, (calculator, variables, explicit, fuzzy) in enumerate(MEDICAL):
        value, unit = execute_medical(calculator, variables)
        for track, question in (("explicit_name", explicit), ("fuzzy_intent", fuzzy)):
            item_id = f"med-dev-{index + 1:02d}-{track[:1]}"
            medical.append({"schema_version": "dev-candidate-0.1", "review_status": "pending_clinical_and_independent_review", "source": {"type": "synthetic_project_authored", "license": "CC-BY-4.0", "clinical_use": False}, "runtime": {"id": item_id, "domain": "medical", "patient_note": question, "question": question, "evidence": [], "metadata": {"track": track, "difficulty": "easy" if track == "explicit_name" else "medium", "template_group_id": f"med-template-{index + 1:02d}"}}, "draft_gold_for_review": {"calculator_id": calculator, "answer": {"value": value, "unit": unit}, "required_entities": variables}})
    assert len(telecom) == 30 and len(medical) == 20
    dump(Path("data/telecom/development/candidates_30_v0.1.jsonl"), telecom)
    dump(Path("data/medical/development/candidates_20_v0.1.jsonl"), medical)
    print("wrote Telecom 30 and Medical 20 review-ready development candidates")


if __name__ == "__main__":
    main()
