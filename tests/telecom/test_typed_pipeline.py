from applicability_qa.core.schemas import RunRecord
from applicability_qa.domains.telecom.adapter import load_telecom_records
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider


CONFIG = {"model": {"name": "mock"}, "retrieval": {"top_k": 5, "corpus_path": "data/telecom/corpus/evidence_corpus_seed.jsonl"}}


def test_typed_pipeline_executes_all_ten_and_records_passage_decisions():
    for record in load_telecom_records("data/telecom/benchmark/fave_bench_10.jsonl"):
        result = RunRecord.model_validate(run_pipeline("typed_fave_retrieval_predicted_executor", record.runtime, MockProvider(), CONFIG))
        assert result.execution["success"]
        assert result.execution_gate and result.execution_gate.allowed
        assert result.requirement_signature
        assert any(not decision.applicable for decision in result.typed_applicability_decisions if decision.evidence_id != "execution_inputs")
