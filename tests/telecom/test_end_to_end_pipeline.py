from applicability_qa.core.schemas import RunRecord
from applicability_qa.domains.telecom.adapter import load_telecom_records
from applicability_qa.pipelines import run_pipeline
from applicability_qa.providers.mock_provider import MockProvider


CONFIG = {
    "experiment_name": "test_e2e", "schema_version": "0.3", "evaluator_version": "v2",
    "model": {"name": "mock"}, "retrieval": {"top_k": 5, "corpus_path": "data/telecom/corpus/evidence_corpus_seed.jsonl"},
}


def test_retrieval_executor_methods_complete_seed_without_gold_runtime_access():
    records = load_telecom_records("data/telecom/benchmark/fave_bench_10.jsonl")
    for method in ("vanilla_retrieval_predicted_executor", "fave_retrieval_predicted_executor"):
        for record in records:
            result = run_pipeline(method, record.runtime, MockProvider(), CONFIG)
            validated = RunRecord.model_validate(result)
            assert validated.retrieval is not None
            assert validated.formula_mode == "predicted"
            assert validated.formula_selection.predicted_formula_id == record.gold.formula_id
            assert validated.execution["success"] is True
