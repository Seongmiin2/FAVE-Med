from .cot import run_cot
from .demo import run_demo
from .demo_multi_executor import run_demo_multi_executor
from .demo_oracle_executor import run_demo_oracle_executor
from .demo_predicted_executor import run_demo_predicted_executor
from .fave import run_fave
from .fave_demo import run_fave_demo
from .fave_oracle_executor import run_fave_oracle_executor
from .fave_predicted_executor import run_fave_predicted_executor
from .llm_only import run_llm_only
from .vanilla_rag import run_vanilla_rag
from .vanilla_controlled_rag import run_vanilla_controlled_rag
from .vanilla_retrieval_rag import run_vanilla_retrieval_rag
from .fave_controlled import run_fave_controlled
from .fave_retrieval import run_fave_retrieval
from .vanilla_retrieval_predicted_executor import run_vanilla_retrieval_predicted_executor
from .fave_retrieval_predicted_executor import run_fave_retrieval_predicted_executor
from .medical_predicted_executor import run_medical_predicted_executor
from .medical_retrieval import run_medical_vanilla_retrieval, run_medical_fave_retrieval, run_medical_retrieval_predicted_executor, run_medical_fave_retrieval_predicted_executor
from ..core.schemas import RunRecord
from ..core.errors import StructuredOutputError

PIPELINES = {"llm_only": run_llm_only, "cot": run_cot, "vanilla_rag": run_vanilla_rag, "fave": run_fave, "demo": run_demo, "fave_demo": run_fave_demo}
PIPELINES.update({"fave_silent": run_fave, "demo_multi_executor": run_demo_multi_executor})
PIPELINES.update({"demo_oracle_executor": run_demo_oracle_executor, "fave_oracle_executor": run_fave_oracle_executor, "demo_predicted_executor": run_demo_predicted_executor, "fave_predicted_executor": run_fave_predicted_executor})
PIPELINES.update({"vanilla_controlled_rag": run_vanilla_controlled_rag, "fave_controlled": run_fave_controlled, "vanilla_retrieval_rag": run_vanilla_retrieval_rag, "fave_retrieval": run_fave_retrieval})
PIPELINES.update({"vanilla_retrieval_predicted_executor": run_vanilla_retrieval_predicted_executor, "fave_retrieval_predicted_executor": run_fave_retrieval_predicted_executor})
PIPELINES.update({"medical_predicted_executor": run_medical_predicted_executor})
PIPELINES.update({"medical_llm_only": run_llm_only})
PIPELINES.update({"medical_vanilla_retrieval": run_medical_vanilla_retrieval, "medical_fave_retrieval": run_medical_fave_retrieval, "medical_retrieval_predicted_executor": run_medical_retrieval_predicted_executor, "medical_fave_retrieval_predicted_executor": run_medical_fave_retrieval_predicted_executor})


def run_pipeline(name, item, provider, config):
    try:
        result = PIPELINES[name](item, provider, config)
        result["method"] = name
        result["model"] = config.get("model", {}).get("name")
        result["prompt_version"] = config.get("prompt_version", "v1")
        result["experiment_id"] = config.get("experiment_name", "unversioned")
        result["schema_version"] = str(config.get("schema_version", "0.2"))
        result["evaluator_version"] = config.get("evaluator_version", "v1")
        result.setdefault("formula_mode", "none")
        result.setdefault("is_primary_result", True)
        result.setdefault("retrieval", None)
        result.setdefault("evidence_decisions", [])
        result.setdefault("formula_selection", None)
        result["usage"].setdefault("total_calls", 1 if result["usage"].get("input_tokens") or result["usage"].get("output_tokens") else 0)
        return RunRecord.model_validate(result).model_dump()
    except Exception as exc:
        failure_code = exc.code if isinstance(exc, StructuredOutputError) else "pipeline_error"
        failed = {"id": item.id, "experiment_id": config.get("experiment_name", "unversioned"), "domain": item.domain, "method": name, "model": config.get("model", {}).get("name"), "prompt_version": config.get("prompt_version", "v1"), "schema_version": str(config.get("schema_version", "0.3")), "evaluator_version": config.get("evaluator_version", "v2"), "answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": failure_code, "accepted_evidence_ids": [], "rejected_evidence_ids": [], "extracted_variables": {}, "verification": {}, "execution": {"mode": "llm", "success": False, "error": str(exc)}, "usage": {"input_tokens": 0, "output_tokens": 0, "latency_seconds": 0.0, "total_calls": 0}, "raw_response": {}}
        return RunRecord.model_validate(failed).model_dump()
