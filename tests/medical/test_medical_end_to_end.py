import json
import re

from applicability_qa.core.schemas import MedicalRuntimeQuestion, RunRecord
from applicability_qa.domains.medical.formula_executor import execute
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider


CASES = [
    ("BMI", "Calculate BMI from weight and height.", {"weight_kg": 70, "height_m": 1.75}, "body_mass_index"),
    ("MAP", "Calculate mean arterial pressure from systolic and diastolic pressure.", {"systolic_bp": 120, "diastolic_bp": 75}, "mean_arterial_pressure"),
    ("AG", "Find the anion gap from sodium chloride and bicarbonate.", {"sodium": 140, "chloride": 104, "bicarbonate": 24}, "anion_gap"),
    ("CG", "Estimate Cockcroft-Gault creatinine clearance.", {"age_years": 60, "weight_kg": 70, "serum_creatinine": 1, "sex": "male"}, "cockcroft_gault"),
    ("CA", "Calculate corrected calcium using albumin.", {"calcium_mg_dl": 8, "albumin_g_dl": 2}, "corrected_calcium"),
    ("BSA", "Find Mosteller body surface area.", {"height_cm": 175, "weight_kg": 70}, "body_surface_area_mosteller"),
    ("OSM", "Calculate serum osmolality from sodium glucose and BUN.", {"sodium": 140, "glucose_mg_dl": 90, "bun_mg_dl": 14}, "serum_osmolality"),
    ("FENA", "Calculate fractional excretion of sodium FENa.", {"urine_sodium": 40, "plasma_creatinine": 2, "plasma_sodium": 140, "urine_creatinine": 100}, "fractional_excretion_sodium"),
    ("QTC", "Calculate Bazett corrected QTc from QT and RR.", {"qt_seconds": 0.4, "rr_seconds": 0.8}, "qtc_bazett"),
    ("MELD", "Calculate MELD-Na from MELD and sodium.", {"meld_i": 20, "sodium": 130}, "meld_na"),
]


class MedicalSmokeProvider(MockProvider):
    def generate_json(self, system_prompt, user_prompt, schema=None):
        if system_prompt.startswith("Classify evidence") or "Relevance is not sufficient" in system_prompt:
            payload = json.loads(user_prompt)
            return {"decisions": [{"evidence_id": row["id"], "label": "rejected" if row["id"].endswith("_trap") else "valid", "conflict_type": "formula_convention" if row["id"].endswith("_trap") else "none", "reason": "deterministic smoke label", "confidence": 1.0} for row in payload["candidate_evidence"]]}
        for marker, question, entities, calculator_id in CASES:
            if question in user_prompt:
                value, unit = execute(calculator_id, entities)
                return {"answer": {"final_value": value, "final_unit": unit}, "extracted_variables": entities, "verification": {"unit_check": "pass", "condition_check": "pass", "variable_check": "pass"}}
        return {"answer": {"final_value": None, "final_unit": None}, "extracted_variables": {}, "verification": {}}


def test_five_medical_methods_complete_ten_family_smoke():
    config = {"experiment_name": "medical_mock_v03", "schema_version": "0.3", "evaluator_version": "v2", "model": {"name": "mock"}, "runtime": {"strict_structured_output": True}, "retrieval": {"top_k": 5, "corpus_path": "data/medical/corpus/calculator_evidence_v0.3.jsonl"}}
    methods = ("medical_llm_only", "medical_vanilla_retrieval", "medical_fave_retrieval", "medical_retrieval_predicted_executor", "medical_fave_retrieval_predicted_executor", "medical_typed_fave_retrieval_predicted_executor")
    for marker, question, entities, calculator_id in CASES:
        item = MedicalRuntimeQuestion(id=marker, patient_note=f"Synthetic integration fixture with values {entities}.", question=question)
        for method in methods:
            result = RunRecord.model_validate(run_pipeline(method, item, MedicalSmokeProvider(), config))
            assert result.answer["final_value"] is not None
            if "predicted_executor" in method:
                assert result.formula_selection.predicted_formula_id == calculator_id
                assert result.execution["success"] is True
            if "typed_fave" in method:
                assert result.execution_gate and result.execution_gate.allowed
                assert result.requirement_signature is not None
