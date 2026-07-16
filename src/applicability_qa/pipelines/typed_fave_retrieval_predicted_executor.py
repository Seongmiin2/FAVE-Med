from __future__ import annotations

from ..core.compatibility import verify_applicability
from ..core.execution_gate import build_execution_gate
from ..core.planning import build_solution_plan
from ..core.post_validation import validate_execution
from ..core.signatures import EvidenceSignature
from ..domains.telecom.evidence_signature_parser import parse_evidence_signature
from ..domains.telecom.formula_executor import execute
from ..domains.telecom.formula_registry import formula_by_id, load_formula_registry
from ..domains.telecom.formula_selector import select_formula
from ..domains.telecom.requirement_parser import parse_requirement
from ..retrieval import BM25Retriever, load_corpus
from .common import normalize, validate_extraction
from .fave_demo import EXTRACTION_SYSTEM


def run_typed_fave_retrieval_predicted_executor(item, provider, config):
    top_k = config["retrieval"].get("top_k", 5)
    retrieved = BM25Retriever(load_corpus(config["retrieval"]["corpus_path"])).retrieve(item.question, top_k)
    registry = load_formula_registry(config.get("formula_registry_path", None) or load_formula_registry.__defaults__[0])
    selection = select_formula(item.question, "\n".join(row.text for row in retrieved), registry, config.get("formula_top_k", 3))
    if selection["abstain"]:
        return normalize(item, "typed_fave_retrieval_predicted_executor", {"answer": {"final_value": None, "final_unit": None}, "abstain": True, "abstain_reason": selection["abstain_reason"], "execution": {"mode": "python", "success": False, "error": selection["abstain_reason"]}}) | {"formula_mode": "predicted", "formula_selection": selection, "retrieval": {"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in retrieved]}}
    formula = formula_by_id(selection["predicted_formula_id"], registry)
    requirement = parse_requirement(item.question, formula)
    signatures = [parse_evidence_signature(row, requirement) for row in retrieved]
    passage_decisions = [verify_applicability(requirement, row) for row in signatures]
    accepted = [row.evidence_id for row in passage_decisions if row.applicable]
    context = "\n".join(row.text for row in retrieved if row.evidence_id in accepted)
    raw = provider.generate_json(EXTRACTION_SYSTEM, f"Formula: {formula.expression}\nQuestion: {item.question}\nApplicable evidence:\n{context}")
    validate_extraction(raw, config.get("runtime", {}).get("strict_structured_output", False))
    variables = raw.get("extracted_variables", {})
    normalized_facts = dict(variables)
    for field in requirement.required_inputs:
        if field.name not in normalized_facts:
            alias = next((name for name in field.aliases if name in variables), None)
            if alias is not None:
                normalized_facts[field.name] = variables[alias]
    execution_signature = EvidenceSignature(evidence_id="execution_inputs", quantities={requirement.target_quantity: requirement.target_unit}, variables=list(variables), facts=normalized_facts, asserted_formula_id=formula.formula_id, convention_tags=requirement.convention_tags, procedural_steps=requirement.required_procedural_steps, source_type="runtime_extraction")
    execution_decision = verify_applicability(requirement, execution_signature)
    gate = build_execution_gate([execution_decision])
    plan = build_solution_plan(formula.executor_name, requirement, passage_decisions)
    raw.update(requirement_signature=requirement.model_dump(), evidence_signatures=[row.model_dump() for row in signatures] + [execution_signature.model_dump()], typed_applicability_decisions=[row.model_dump() for row in passage_decisions] + [execution_decision.model_dump()], solution_plan=plan.model_dump(), execution_gate=gate.model_dump(), accepted_evidence_ids=accepted, rejected_evidence_ids=[row.evidence_id for row in passage_decisions if not row.applicable])
    if gate.allowed:
        try:
            value, unit = execute(formula.executor_name, variables)
            post = validate_execution(value, unit, requirement.target_unit, minimum=0)
            raw.update(answer={"final_value": value if post.passed else None, "final_unit": unit if post.passed else None}, abstain=not post.passed, abstain_reason=None if post.passed else "post_validation_failure", execution={"mode": "python", "success": post.passed, "error": None if post.passed else ";".join(post.errors)}, post_validation=post.model_dump())
        except Exception as exc:
            raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="executor_failure", execution={"mode": "python", "success": False, "error": str(exc)})
    else:
        raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason="typed_execution_gate", execution={"mode": "python", "success": False, "error": gate.reason})
    result = normalize(item, "typed_fave_retrieval_predicted_executor", raw)
    result.update(formula_mode="predicted", formula_selection=selection, retrieval={"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in retrieved]}, **{key: raw[key] for key in ("requirement_signature", "evidence_signatures", "typed_applicability_decisions", "solution_plan", "execution_gate", "post_validation") if key in raw})
    return result
