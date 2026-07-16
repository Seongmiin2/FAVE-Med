from applicability_qa.core.schemas import RuntimeEvidence, RuntimeQuestion
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider
from applicability_qa.domains.telecom.adapter import load_telecom_records
from applicability_qa.domains.telecom.adapter import convert_fave_record


class CapturingProvider(MockProvider):
    def __init__(self):
        super().__init__()
        self.prompts = []

    def generate_json(self, system_prompt, user_prompt, schema=None):
        self.prompts.append(system_prompt + "\n" + user_prompt)
        return super().generate_json(system_prompt, user_prompt, schema)


def sentinel_runtime():
    return RuntimeQuestion(
        id="sentinel",
        domain="telecom",
        question="Given B = 10 MHz and SNR = 20 dB, calculate Shannon capacity.",
        requested_output="capacity in Mbps",
        evidence=[RuntimeEvidence(id="e1", text="Shannon capacity uses bandwidth and linear SNR.")],
    )


def test_predicted_pipeline_has_no_gold_fields_or_fallback():
    item = sentinel_runtime()
    assert not hasattr(item, "formula")
    assert not hasattr(item, "gold_answer")
    assert not hasattr(item, "required_variables")
    provider = CapturingProvider()
    result = run_pipeline("demo_predicted_executor", item, provider, {"model": {"name": "mock"}})
    combined = "\n".join(provider.prompts)
    assert "GOLD_FORMULA_SENTINEL_DO_NOT_LEAK" not in combined
    assert "GOLD_ANSWER_SENTINEL_DO_NOT_LEAK" not in combined
    assert result["formula_mode"] == "predicted"
    assert result["formula_selection"]["predicted_formula_id"] == "shannon_capacity"


def test_unknown_formula_abstains_without_oracle_fallback():
    item = RuntimeQuestion(id="unknown", domain="telecom", question="Compute an unsupported quantum widget invariant.")
    result = run_pipeline("demo_predicted_executor", item, CapturingProvider(), {"model": {"name": "mock"}})
    assert result["abstain"]
    assert result["formula_selection"]["predicted_formula_id"] is None


def test_seed_formula_selection_is_correct_without_pipeline_gold_access():
    records = load_telecom_records("data/telecom/benchmark/fave_bench_10.jsonl")
    for record in records:
        result = run_pipeline("demo_predicted_executor", record.runtime, CapturingProvider(), {"model": {"name": "mock"}})
        assert result["formula_selection"]["predicted_formula_id"] == record.gold.formula_id


def test_runtime_does_not_derive_requested_output_from_gold_unit():
    base = {"id": "u1", "question": "Calculate channel capacity.", "gold_value": 1, "gold_formula": "C = B log2(1 + SNR_linear)"}
    first = convert_fave_record({**base, "gold_unit": "GOLD_UNIT_SENTINEL_DO_NOT_LEAK"})
    second = convert_fave_record({**base, "gold_unit": "bps"})
    assert first.runtime.requested_output is None
    assert first.runtime == second.runtime


def test_runtime_extracts_only_explicit_question_unit():
    row = {"id": "u2", "question": "Calculate channel capacity and report the result in Mbps.", "gold_value": 1, "gold_unit": "GOLD_UNIT_SENTINEL_DO_NOT_LEAK", "gold_formula": "C = B log2(1 + SNR_linear)"}
    assert convert_fave_record(row).runtime.requested_output == "Mbps"
