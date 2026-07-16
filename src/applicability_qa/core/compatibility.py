from __future__ import annotations

from .condition_predicates import evaluate_predicate
from .signatures import CompatibilityCheck, EvidenceSignature, RequirementSignature, TypedApplicabilityDecision


def _check(kind: str, passed: bool, code: str, message: str, evidence_id: str, blocking: bool = True, **details) -> CompatibilityCheck:
    return CompatibilityCheck(check_type=kind, passed=passed, blocking=blocking, code=code, message=message, evidence_id=evidence_id, details=details)


def check_unit(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    observed = evidence.quantities.get(requirement.target_quantity)
    passed = observed is None or observed == requirement.target_unit
    return _check("unit", passed, "unit_ok" if passed else "unit_mismatch", f"target unit requires {requirement.target_unit}; observed {observed or 'unspecified'}", evidence.evidence_id, required=requirement.target_unit, observed=observed)


def check_variable_coverage(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    available = set(evidence.variables) | set(evidence.facts)
    missing = [item.name for item in requirement.required_inputs if item.required and item.name not in available and not available.intersection(item.aliases)]
    passed = not missing
    return _check("variable_coverage", passed, "variables_covered" if passed else "missing_variables", f"missing required variables: {missing}" if missing else "all required variables are covered", evidence.evidence_id, missing=missing)


def check_conditions(requirement: RequirementSignature, evidence: EvidenceSignature) -> list[CompatibilityCheck]:
    checks = []
    for predicate in requirement.conditions:
        passed = evaluate_predicate(predicate, evidence.facts)
        checks.append(_check("condition", passed, "condition_ok" if passed else "condition_mismatch", predicate.description or f"{predicate.field} {predicate.operator} {predicate.value}", evidence.evidence_id, predicate=predicate.model_dump()))
    return checks


def check_convention(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    passed = requirement.convention is None or evidence.convention is None or requirement.convention == evidence.convention
    return _check("convention", passed, "convention_ok" if passed else "convention_mismatch", f"required {requirement.convention}; observed {evidence.convention}", evidence.evidence_id)


def check_approximation(requirement: RequirementSignature, evidence: EvidenceSignature) -> CompatibilityCheck:
    policy, observed = requirement.approximation_policy, evidence.approximation
    passed = not ((policy == "exact" and observed is True) or (policy == "required" and observed is False))
    return _check("approximation", passed, "approximation_ok" if passed else "approximation_mismatch", f"policy {policy}; approximation={observed}", evidence.evidence_id)


def check_physical_constraints(requirement: RequirementSignature, evidence: EvidenceSignature) -> list[CompatibilityCheck]:
    return [_check("physical_constraint", (passed := evaluate_predicate(p, evidence.facts)), "physical_ok" if passed else "physical_constraint_violation", p.description or f"{p.field} {p.operator} {p.value}", evidence.evidence_id, predicate=p.model_dump()) for p in requirement.physical_constraints]


def verify_applicability(requirement: RequirementSignature, evidence: EvidenceSignature) -> TypedApplicabilityDecision:
    checks = [check_unit(requirement, evidence), check_variable_coverage(requirement, evidence), *check_conditions(requirement, evidence), check_convention(requirement, evidence), check_approximation(requirement, evidence), *check_physical_constraints(requirement, evidence)]
    applicable = not any(not item.passed and item.blocking for item in checks)
    warnings = [item.code for item in checks if not item.passed and not item.blocking]
    return TypedApplicabilityDecision(evidence_id=evidence.evidence_id, applicable=applicable, checks=checks, warnings=warnings)
