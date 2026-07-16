from __future__ import annotations

from ..domains.telecom.formula_executor import execute
from ..domains.telecom.formula_registry import formula_by_id, load_formula_registry
from ..domains.telecom.formula_selector import select_formula
from ..domains.telecom.validity_checker import classify_evidence
from ..core.compatibility import verify_applicability
from ..core.execution_gate import build_execution_gate
from ..core.planning import build_solution_plan
from ..core.post_validation import validate_execution
from ..core.signature_builders import evidence_signatures_from_extraction, requirement_from_formula
from .common import merge_usage, normalize, validate_extraction
from .fave_demo import EXTRACTION_SYSTEM


def run_fave_predicted_executor(item, provider, config):
    strict = config.get("runtime", {}).get("strict_structured_output", False)
    classification = classify_evidence(item, item.evidence, provider, strict=strict)
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
        validate_extraction(generated, strict)
        raw.update(generated)
        raw["usage"] = merge_usage(classification.usage, generated.get("usage", {}))
        requirement = requirement_from_formula(formula)
        signatures = evidence_signatures_from_extraction(sorted(accepted), raw.get("extracted_variables", {}), requirement)
        decisions = [verify_applicability(requirement, signature) for signature in signatures]
        gate = build_execution_gate(decisions)
        raw.update(requirement_signature=requirement.model_dump(), evidence_signatures=[row.model_dump() for row in signatures], typed_applicability_decisions=[row.model_dump() for row in decisions], solution_plan=build_solution_plan(formula.executor_name, requirement, decisions).model_dump(), execution_gate=gate.model_dump())
        if not gate.allowed:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="typed_execution_gate", execution={"mode": "python", "success": False, "error": gate.reason})
            result = normalize(item, "fave_predicted_executor", raw)
            result.update(formula_mode="predicted", is_primary_result=True, formula_selection=selection, evidence_decisions=raw["evidence_decisions"], **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate")})
            return result
        try:
            value, unit = execute(formula.executor_name, raw.get("extracted_variables", {}))
            post = validate_execution(value, unit, requirement.target_unit)
            raw.update(answer={"final_value": value, "final_unit": unit}, execution={"mode": "python", "success": post.passed, "error": None if post.passed else ";".join(post.errors)}, post_validation=post.model_dump())
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    result = normalize(item, "fave_predicted_executor", raw)
    result.update(formula_mode="predicted", is_primary_result=True, formula_selection=selection, evidence_decisions=raw["evidence_decisions"], **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate", "post_validation") if key in raw})
    return result
