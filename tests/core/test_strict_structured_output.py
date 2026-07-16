from applicability_qa.core.schemas import RuntimeEvidence, RuntimeQuestion
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider
from applicability_qa.domains.telecom.formula_selector import validate_formula_selection
import pytest


def runtime():
    return RuntimeQuestion(id="strict", domain="telecom", question="Given B = 10 MHz and SNR = 20 dB, calculate Shannon capacity.", evidence=[RuntimeEvidence(id="e1", text="Shannon capacity uses linear SNR.")])


def config(strict=True):
    return {"experiment_name": "strict_test", "schema_version": "0.3", "evaluator_version": "v2", "model": {"name": "mock"}, "runtime": {"strict_structured_output": strict}}


def test_strict_classifier_rejects_legacy_shape():
    result = run_pipeline("fave_predicted_executor", runtime(), MockProvider({"accepted_evidence_ids": ["e1"], "rejected_evidence_ids": []}), config())
    assert result["abstain_reason"] == "classifier_parse_failure"


def test_legacy_mode_keeps_historical_classifier_fallback():
    result = run_pipeline("fave_predicted_executor", runtime(), MockProvider({"accepted_evidence_ids": ["e1"], "rejected_evidence_ids": []}), config(False))
    assert result["abstain_reason"] != "classifier_parse_failure"


def test_strict_variable_extractor_rejects_missing_schema():
    result = run_pipeline("demo_predicted_executor", runtime(), MockProvider(lambda *_: {"answer": {"final_value": 1, "final_unit": "bps"}}), config())
    assert result["abstain_reason"] == "variable_extractor_parse_failure"


def test_formula_selector_schema_rejects_missing_selection():
    with pytest.raises(Exception) as error:
        validate_formula_selection({"candidate_formula_ids": ["shannon_capacity"], "abstain": False})
    assert error.value.code == "formula_selector_parse_failure"
