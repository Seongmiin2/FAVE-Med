from __future__ import annotations

from ..core.compatibility import verify_applicability
from ..core.execution_gate import build_execution_gate
from ..core.planning import build_solution_plan
from ..core.post_validation import validate_execution
from ..core.signatures import EvidenceSignature
from ..domains.medical.calculator_registry import calculator_by_id, load_calculator_registry
from ..domains.medical.calculator_selector import select_calculator
from ..domains.medical.evidence_signature_parser import parse_evidence_signature
from ..domains.medical.formula_executor import execute
from ..domains.medical.requirement_parser import parse_requirement
from ..retrieval import BM25Retriever, load_corpus
from .common import normalize, question_prompt, validate_extraction
from .medical_predicted_executor import SYSTEM


def run_medical_typed_fave_retrieval_predicted_executor(item, provider, config):
    top_k = config["retrieval"].get("top_k", 5)
    query = f"{item.question} {item.patient_note}"
    retrieved = BM25Retriever(load_corpus(config["retrieval"]["corpus_path"])).retrieve(query, top_k)
    registry = load_calculator_registry(config.get("calculator_registry_path", None) or load_calculator_registry.__defaults__[0])
    selection = select_calculator(item.question, registry, config.get("calculator_top_k", 3))
    if selection["abstain"]:
        raw = {"answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": selection["abstain_reason"], "execution": {"mode": "python", "success": False, "error": selection["abstain_reason"]}}
        result = normalize(item, "medical_typed_fave_retrieval_predicted_executor", raw)
        result.update(formula_mode="predicted", formula_selection=selection, retrieval={"query": query, "top_k": top_k, "results": [row.model_dump() for row in retrieved]})
        return result
    calculator = calculator_by_id(selection["predicted_formula_id"], registry)
    requirement = parse_requirement(item.patient_note, item.question, calculator)
    signatures = [parse_evidence_signature(row, requirement) for row in retrieved]
    passage_decisions = [verify_applicability(requirement, row) for row in signatures]
    accepted = [row.evidence_id for row in passage_decisions if row.applicable]
    evidence = "\n".join(row.text for row in retrieved if row.evidence_id in accepted)
    raw = provider.generate_json(SYSTEM, f"{question_prompt(item)}\n\nRule: {calculator.expression}\nApplicable evidence:\n{evidence}")
    validate_extraction(raw, config.get("runtime", {}).get("strict_structured_output", False))
    variables = raw.get("extracted_variables", {})
    execution_signature = EvidenceSignature(evidence_id="execution_inputs", quantities={requirement.target_quantity: requirement.target_unit}, variables=list(variables), facts=variables, asserted_formula_id=calculator.calculator_id, convention_tags=requirement.convention_tags, procedural_steps=requirement.required_procedural_steps, source_type="runtime_extraction")
    execution_decision = verify_applicability(requirement, execution_signature)
    gate = build_execution_gate([execution_decision])
    raw.update(requirement_signature=requirement.model_dump(), evidence_signatures=[row.model_dump() for row in signatures] + [execution_signature.model_dump()], typed_applicability_decisions=[row.model_dump() for row in passage_decisions] + [execution_decision.model_dump()], solution_plan=build_solution_plan(calculator.executor_name, requirement, passage_decisions).model_dump(), execution_gate=gate.model_dump(), accepted_evidence_ids=accepted, rejected_evidence_ids=[row.evidence_id for row in passage_decisions if not row.applicable])
    if gate.allowed:
        try:
            value, unit = execute(calculator.executor_name, variables)
            bounds = (0, 1) if calculator.output.canonical_unit == "probability" else (0, None)
            post = validate_execution(value, unit, requirement.target_unit, minimum=bounds[0], maximum=bounds[1])
            raw.update(answer={"final_value": value if post.passed else None, "final_unit": unit if post.passed else None}, abstain=not post.passed, abstain_reason=None if post.passed else "post_validation_failure", execution={"mode": "python", "success": post.passed, "error": None if post.passed else ";".join(post.errors)}, post_validation=post.model_dump())
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    else:
        raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="typed_execution_gate", execution={"mode": "python", "success": False, "error": gate.reason})
    result = normalize(item, "medical_typed_fave_retrieval_predicted_executor", raw)
    result.update(formula_mode="predicted", formula_selection=selection, retrieval={"query": query, "top_k": top_k, "results": [row.model_dump() for row in retrieved]}, **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate", "post_validation") if key in raw})
    return result
