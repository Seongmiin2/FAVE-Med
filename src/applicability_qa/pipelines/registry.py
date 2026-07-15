from .cot import run_cot
from .demo import run_demo
from .demo_multi_executor import run_demo_multi_executor
from .fave import run_fave
from .fave_demo import run_fave_demo
from .llm_only import run_llm_only
from .vanilla_rag import run_vanilla_rag

PIPELINES = {"llm_only": run_llm_only, "cot": run_cot, "vanilla_rag": run_vanilla_rag, "fave": run_fave, "demo": run_demo, "fave_demo": run_fave_demo}
PIPELINES.update({"fave_silent": run_fave, "demo_multi_executor": run_demo_multi_executor})


def run_pipeline(name, item, provider, config):
    try:
        result = PIPELINES[name](item, provider, config)
        result["method"] = name
        result["model"] = config.get("model", {}).get("name")
        result["prompt_version"] = config.get("prompt_version", "v1")
        return result
    except Exception as exc:
        return {"id": item.id, "domain": item.domain, "method": name, "model": config.get("model", {}).get("name"), "prompt_version": config.get("prompt_version", "v1"), "answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": "pipeline_error", "accepted_evidence_ids": [], "rejected_evidence_ids": [], "extracted_variables": {}, "verification": {}, "execution": {"mode": "llm", "success": False, "error": str(exc)}, "usage": {"input_tokens": 0, "output_tokens": 0, "latency_seconds": 0.0}, "raw_response": {}}
