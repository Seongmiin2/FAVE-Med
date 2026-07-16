from __future__ import annotations

from ..domains.telecom.formula_executor import execute
from ..domains.telecom.formula_registry import formula_by_id, load_formula_registry
from ..domains.telecom.formula_selector import select_formula
from .common import normalize
from .demo_multi_executor import EXTRACTION_SYSTEM


def run_demo_predicted_executor(item, provider, config):
    registry = load_formula_registry(config.get("formula_registry_path", None) or load_formula_registry.__defaults__[0])
    evidence_text = "\n".join(row.text for row in item.evidence)
    selection = select_formula(item.question, evidence_text, registry, config.get("formula_top_k", 3))
    if selection["abstain"]:
        raw = {"answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": selection["abstain_reason"], "execution": {"mode": "python", "success": False, "error": selection["abstain_reason"]}}
    else:
        formula = formula_by_id(selection["predicted_formula_id"], registry)
        raw = provider.generate_json(EXTRACTION_SYSTEM, f"Formula: {formula.expression}\nQuestion: {item.question}\nContext:\n{evidence_text}")
        try:
            value, unit = execute(formula.executor_name, raw.get("extracted_variables", {}))
            raw.update(answer={"final_value": value, "final_unit": unit}, execution={"mode": "python", "success": True, "error": None})
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    result = normalize(item, "demo_predicted_executor", raw)
    result.update(formula_mode="predicted", is_primary_result=True, formula_selection=selection)
    return result
