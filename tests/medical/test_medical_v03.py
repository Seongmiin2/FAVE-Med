from applicability_qa.domains.medical.adapter import convert_demomed_record
from applicability_qa.domains.medical.calculator_registry import load_calculator_registry
from applicability_qa.domains.medical.calculator_selector import select_calculator
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider


class CaptureProvider(MockProvider):
    def __init__(self, response):
        super().__init__(lambda *_: response)
        self.prompts = []

    def generate_json(self, system_prompt, user_prompt, schema=None):
        self.prompts.append(user_prompt)
        return super().generate_json(system_prompt, user_prompt, schema)


def test_medical_runtime_separates_patient_context_from_gold():
    row = {"id": "m1", "patient_note": "Weight 70 kg and height 1.75 m.", "question": "Calculate Body Mass Index.", "calculator_name": "GOLD_CALCULATOR_SENTINEL Body Mass Index", "ground_truth_answer": "22.86", "relevant_entities": "{'GOLD_ENTITY_SENTINEL': 1}"}
    record = convert_demomed_record(row)
    dumped = record.runtime.model_dump_json()
    assert "Weight 70 kg" in dumped
    assert "GOLD_CALCULATOR_SENTINEL" not in dumped
    assert "GOLD_ENTITY_SENTINEL" not in dumped


def test_medical_patient_note_is_present_in_prompt_and_gold_is_absent():
    row = {"id": "m1", "patient_note": "Patient weighs 70 kg and is 1.75 m tall.", "question": "Calculate Body Mass Index.", "calculator_name": "Body Mass Index", "ground_truth_answer": "22.86", "relevant_entities": "{'secret_gold_weight': 70}"}
    record = convert_demomed_record(row)
    provider = CaptureProvider({"extracted_variables": {"weight_kg": 70, "height_m": 1.75}, "verification": {}})
    result = run_pipeline("medical_predicted_executor", record.runtime, provider, {"experiment_name": "medical_mock", "schema_version": "0.3", "evaluator_version": "v2", "model": {"name": "mock"}, "runtime": {"strict_structured_output": True}})
    combined = "\n".join(provider.prompts)
    assert "Patient note:\nPatient weighs 70 kg" in combined
    assert "Question:\nCalculate Body Mass Index" in combined
    assert "secret_gold_weight" not in combined
    assert result["execution"]["success"] is True


def test_calculator_selector_finds_all_ten_without_gold_name():
    registry = load_calculator_registry()
    questions = {
        "body_mass_index": "Calculate BMI from weight and height.",
        "mean_arterial_pressure": "Calculate mean arterial pressure from systolic and diastolic pressure.",
        "anion_gap": "Find the anion gap from sodium chloride and bicarbonate.",
        "cockcroft_gault": "Estimate Cockcroft-Gault creatinine clearance.",
        "corrected_calcium": "Calculate corrected calcium using albumin.",
        "body_surface_area_mosteller": "Find Mosteller body surface area.",
        "serum_osmolality": "Calculate serum osmolality from sodium glucose and BUN.",
        "fractional_excretion_sodium": "Calculate fractional excretion of sodium FENa.",
        "qtc_bazett": "Calculate Bazett corrected QTc from QT and RR.",
        "meld_na": "Calculate MELD-Na from MELD and sodium.",
    }
    for expected, question in questions.items():
        assert select_calculator(question, registry)["predicted_formula_id"] == expected
