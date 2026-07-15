from applicability_qa.domains.telecom.adapter import load_telecom_items
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider


REQUIRED = {
    "id", "domain", "method", "model", "prompt_version", "answer", "abstain",
    "abstain_reason", "accepted_evidence_ids", "rejected_evidence_ids",
    "extracted_variables", "verification", "execution", "usage", "raw_response",
}


def test_mock_pipelines_share_output_schema():
    item = load_telecom_items("data/telecom/benchmark/fave_bench_10.jsonl")[0]
    config = {"model": {"name": "mock-model"}, "prompt_version": "test-v1"}
    results = [run_pipeline(name, item, MockProvider(), config) for name in ("llm_only", "vanilla_rag", "fave", "demo", "fave_demo", "fave_silent", "demo_multi_executor")]
    assert all(set(row) == REQUIRED for row in results)
    assert all(set(row["answer"]) == {"final_value", "final_unit"} for row in results)
    assert all(row["execution"]["success"] for row in results)
