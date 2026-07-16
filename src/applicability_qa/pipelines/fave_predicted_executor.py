from __future__ import annotations

from ..domains.telecom.formula_executor import execute
from ..domains.telecom.formula_registry import formula_by_id, load_formula_registry
from ..domains.telecom.formula_selector import select_formula
from ..domains.telecom.validity_checker import classify_evidence
from .common import merge_usage, normalize
from .fave_demo import EXTRACTION_SYSTEM


def run_fave_predicted_executor(item, provider, config):
    classification = classify_evidence(item, item.evidence, provider)
    accepted = {row.evidence_id for row in classification.decisions if row.label == "valid"}
    evidence_text = "\n".join(row.text for row in item.evidence if row.id in accepted)
    registry = load_formula_registry(config.get("formula_registry_path", None) or load_formula_registry.__defaults__[0])
    selection = select_formula(item.question, evidence_text, registry, config.get("formula_top_k", 3))
    raw = {"evidence_decisions": [row.model_dump() for row in classification.decisions], "accepted_evidence_ids": sorted(accepted), "rejected_evidence_ids": [row.evidence_id for row in classification.decisions if row.label == "rejected"]}
    if selection["abstain"]:
        raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason=selection["abstain_reason"], execution={"mode": "python", "success": False, "error": selection["abstain_reason"]})
    else:
        formula = formula_by_id(selection["predicted_formula_id"], registry)
        generated = provider.generate_json(EXTRACTION_SYSTEM, f"Formula: {formula.expression}\nQuestion: {item.question}\nApplicable evidence:\n{evidence_text}")
        raw.update(generated)
        raw["usage"] = merge_usage(classification.usage, generated.get("usage", {}))
        try:
            value, unit = execute(formula.executor_name, raw.get("extracted_variables", {}))
            raw.update(answer={"final_value": value, "final_unit": unit}, execution={"mode": "python", "success": True, "error": None})
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    result = normalize(item, "fave_predicted_executor", raw)
    result.update(formula_mode="predicted", is_primary_result=True, formula_selection=selection, evidence_decisions=raw["evidence_decisions"])
    return result
