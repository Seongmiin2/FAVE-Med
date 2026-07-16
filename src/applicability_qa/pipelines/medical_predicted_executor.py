from __future__ import annotations

from ..domains.medical.calculator_registry import calculator_by_id, load_calculator_registry
from ..domains.medical.calculator_selector import select_calculator
from ..domains.medical.formula_executor import execute
from ..core.compatibility import verify_applicability
from ..core.execution_gate import build_execution_gate
from ..core.planning import build_solution_plan
from ..core.post_validation import validate_execution
from ..core.signature_builders import evidence_signatures_from_extraction, requirement_from_formula
from .common import normalize, question_prompt, validate_extraction

SYSTEM = "Return JSON with extracted_variables and verification only. Extract normalized entities from the patient note and question."


def run_medical_predicted_executor(item, provider, config):
    registry = load_calculator_registry()
    selection = select_calculator(item.question, registry, config.get("calculator_top_k", 3))
    if selection["abstain"]:
        raw = {"answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": selection["abstain_reason"], "execution": {"success": False, "error": selection["abstain_reason"]}}
    else:
        calculator = calculator_by_id(selection["predicted_formula_id"], registry)
        evidence = "\n".join(f"- {row.id}: {row.text}" for row in item.evidence)
        raw = provider.generate_json(SYSTEM, f"{question_prompt(item)}\n\nEvidence:\n{evidence}")
        validate_extraction(raw, config.get("runtime", {}).get("strict_structured_output", False))
        requirement = requirement_from_formula(calculator)
        signatures = evidence_signatures_from_extraction([row.id for row in item.evidence], raw.get("extracted_variables", {}))
        decisions = [verify_applicability(requirement, signature) for signature in signatures]
        gate = build_execution_gate(decisions)
        raw.update(requirement_signature=requirement.model_dump(), evidence_signatures=[row.model_dump() for row in signatures], typed_applicability_decisions=[row.model_dump() for row in decisions], solution_plan=build_solution_plan(calculator.executor_name, requirement, decisions).model_dump(), execution_gate=gate.model_dump())
        if not gate.allowed:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="typed_execution_gate", execution={"mode": "python", "success": False, "error": gate.reason})
            result = normalize(item, "medical_predicted_executor", raw)
            result.update(formula_mode="predicted", formula_selection=selection, **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate")})
            return result
        try:
            value, unit = execute(calculator.executor_name, raw.get("extracted_variables", {}))
            post = validate_execution(value, unit, requirement.target_unit)
            raw.update(answer={"final_value": value, "final_unit": unit}, execution={"mode": "python", "success": post.passed, "error": None if post.passed else ";".join(post.errors)}, post_validation=post.model_dump())
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    result = normalize(item, "medical_predicted_executor", raw)
    result.update(formula_mode="predicted", formula_selection=selection, **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate", "post_validation") if key in raw})
    return result
