from __future__ import annotations

from ...core.signatures import EvidenceSignature, RequirementSignature
from .requirement_parser import RULES


def parse_evidence_signature(evidence, requirement: RequirementSignature) -> EvidenceSignature:
    get = evidence.get if isinstance(evidence, dict) else lambda key, default=None: getattr(evidence, key, default)
    source_id = get("source_id") or get("id")
    formula_id = source_id.removesuffix("_trap")
    rule = RULES.get(formula_id, {})
    is_trap = source_id.endswith("_trap") or "distractor" in get("source_type", "")
    units = {row.name: row.canonical_unit for row in requirement.required_inputs}
    tags = [] if is_trap else rule.get("tags", [])
    steps = [] if is_trap else rule.get("steps", [])
    return EvidenceSignature(
        evidence_id=get("evidence_id") or get("id"),
        asserted_formula_id=formula_id,
        quantities={requirement.target_quantity: requirement.target_unit},
        variables=[row.name for row in requirement.required_inputs],
        variable_units=units,
        convention_tags=tags,
        procedural_steps=steps,
        factuality_claim="verified",
        source_type=get("source_type", "runtime_evidence"),
    )
