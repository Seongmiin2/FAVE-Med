from __future__ import annotations

from .condition_predicates import evaluate_predicate
from .signatures import CompatibilityCheck, EvidenceSignature, RequirementSignature, TypedApplicabilityDecision


def _check(kind: str, passed: bool, code: str, message: str, evidence_id: str, blocking: bool = True, **details) -> CompatibilityCheck:
    return CompatibilityCheck(check_type=kind, passed=passed, blocking=blocking, code=code, message=message, evidence_id=evidence_id, details=details)


def check_unit(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    observed = evidence.quantities.get(requirement.target_quantity)
    mismatches = {item.name: {"required": item.canonical_unit, "observed": evidence.variable_units[item.name]} for item in requirement.required_inputs if item.name in evidence.variable_units and evidence.variable_units[item.name] != item.canonical_unit}
    omitted = [name for name, value in evidence.observed_variables.items() if value.observed_unit and value.normalized_unit and value.observed_unit != value.normalized_unit and not value.conversion_operation]
    passed = (observed is None or observed == requirement.target_unit) and not mismatches and not omitted
    code = "unit_ok" if passed else "conversion_omitted" if omitted else "unit_mismatch"
    return _check("unit", passed, code, f"target unit requires {requirement.target_unit}; observed {observed or 'unspecified'}; variable mismatches={mismatches}; omitted conversions={omitted}", evidence.evidence_id, required=requirement.target_unit, observed=observed, variable_mismatches=mismatches, omitted_conversions=omitted)


BINDING_TERMS = {
    "B": ("bandwidth",), "C": ("capacity", "throughput"), "snr_linear": ("snr",),
    "S": ("signal",), "I": ("interference",), "N": ("noise",),
    "sodium": ("sodium",), "chloride": ("chloride",), "bicarbonate": ("bicarbonate",),
    "urine_sodium": ("urine sodium",), "plasma_sodium": ("plasma sodium",),
    "urine_creatinine": ("urine creatinine",), "plasma_creatinine": ("plasma creatinine",),
    "systolic_bp": ("systolic",), "diastolic_bp": ("diastolic",),
}


def check_variable_binding(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    conflicts = []
    for name, value in evidence.observed_variables.items():
        span = value.source_span.lower().replace("_", " ")
        own = BINDING_TERMS.get(name, (name.lower().replace("_", " "),))
        other = [other_name for other_name, terms in BINDING_TERMS.items() if other_name != name and any(term in span for term in terms)]
        if other and not any(term in span for term in own):
            conflicts.append({"variable": name, "span": value.source_span, "looks_like": other})
    passed = not conflicts
    return _check("variable_binding", passed, "binding_ok" if passed else "variable_binding_mismatch", "runtime source spans match variable bindings" if passed else f"binding conflicts: {conflicts}", evidence.evidence_id, conflicts=conflicts)


def check_variable_coverage(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    available = set(evidence.variables) | set(evidence.facts)
    missing = [item.name for item in requirement.required_inputs if item.required and item.name not in available and not available.intersection(item.aliases)]
    passed = not missing
    return _check("variable_coverage", passed, "variables_covered" if passed else "missing_variables", f"missing required variables: {missing}" if missing else "all required variables are covered", evidence.evidence_id, missing=missing)


def check_conditions(requirement: RequirementSignature, evidence: EvidenceSignature) -> list[CompatibilityCheck]:
    checks = []
    for predicate in requirement.conditions:
        if predicate.field not in evidence.facts:
            checks.append(_check("condition", True, "condition_deferred", f"{predicate.field} will be checked against runtime inputs", evidence.evidence_id, predicate=predicate.model_dump()))
            continue
        passed = evaluate_predicate(predicate, evidence.facts)
        checks.append(_check("condition", passed, "condition_ok" if passed else "condition_mismatch", predicate.description or f"{predicate.field} {predicate.operator} {predicate.value}", evidence.evidence_id, predicate=predicate.model_dump()))
    return checks


def check_convention(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    formula_ok = not requirement.formula_family_candidates or evidence.asserted_formula_id is None or evidence.asserted_formula_id in requirement.formula_family_candidates
    tags_ok = not requirement.convention_tags or not evidence.convention_tags or bool(set(requirement.convention_tags) & set(evidence.convention_tags))
    passed = formula_ok and tags_ok and (requirement.convention is None or evidence.convention is None or requirement.convention == evidence.convention)
    return _check("convention", passed, "convention_ok" if passed else "convention_mismatch", f"required {requirement.convention}; observed {evidence.convention}", evidence.evidence_id)


def check_approximation(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    policy, observed = requirement.approximation_policy, evidence.approximation
    passed = not ((policy == "exact" and observed is True) or (policy == "required" and observed is False))
    return _check("approximation", passed, "approximation_ok" if passed else "approximation_mismatch", f"policy {policy}; approximation={observed}", evidence.evidence_id)


def check_physical_constraints(requirement: RequirementSignature, evidence: EvidenceSignature) -> list[CompatibilityCheck]:
    checks = []
    for predicate in requirement.physical_constraints:
        if predicate.field not in evidence.facts:
            checks.append(_check("physical_constraint", True, "physical_deferred", f"{predicate.field} will be checked against runtime inputs", evidence.evidence_id, predicate=predicate.model_dump()))
            continue
        passed = evaluate_predicate(predicate, evidence.facts)
        checks.append(_check("physical_constraint", passed, "physical_ok" if passed else "physical_constraint_violation", predicate.description or f"{predicate.field} {predicate.operator} {predicate.value}", evidence.evidence_id, predicate=predicate.model_dump()))
    return checks


def check_procedural_steps(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    missing = sorted(set(requirement.required_procedural_steps) - set(evidence.procedural_steps))
    passed = not missing
    return _check("procedural_step", passed, "procedure_ok" if passed else "procedural_step_mismatch", f"missing procedural steps: {missing}" if missing else "required procedural steps present", evidence.evidence_id, missing=missing)


def verify_applicability(requirement: RequirementSignature, evidence: EvidenceSignature) -> TypedApplicabilityDecision:
    checks = [check_unit(requirement, evidence), check_variable_coverage(requirement, evidence), check_variable_binding(requirement, evidence), *check_conditions(requirement, evidence), check_convention(requirement, evidence), check_approximation(requirement, evidence), *check_physical_constraints(requirement, evidence), check_procedural_steps(requirement, evidence)]
    applicable = not any(not item.passed and item.blocking for item in checks)
    warnings = [item.code for item in checks if not item.passed and not item.blocking]
    blocking = [item.code for item in checks if not item.passed and item.blocking]
    return TypedApplicabilityDecision(evidence_id=evidence.evidence_id, applicable=applicable, decision="applicable" if applicable and not warnings else "conditionally_applicable" if applicable else "inapplicable", checks=checks, warnings=warnings, blocking_failures=blocking)
