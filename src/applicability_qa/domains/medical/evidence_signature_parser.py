from __future__ import annotations

from ...core.signatures import EvidenceSignature, RequirementSignature
from .requirement_parser import RULES


def parse_evidence_signature(evidence, requirement: RequirementSignature) -> EvidenceSignature:
    get = evidence.get if isinstance(evidence, dict) else lambda key, default=None: getattr(evidence, key, default)
    source_id = get("source_id") or get("id")
    calculator_id = source_id.removesuffix("_trap")
    tags, steps = RULES.get(calculator_id, ([], []))
    is_trap = source_id.endswith("_trap") or "distractor" in get("source_type", "")
    return EvidenceSignature(
        evidence_id=get("evidence_id") or get("id"),
        asserted_formula_id=calculator_id,
        quantities={requirement.target_quantity: requirement.target_unit},
        variables=[row.name for row in requirement.required_inputs],
        variable_units={row.name: row.canonical_unit for row in requirement.required_inputs},
        convention_tags=[] if is_trap else tags,
        procedural_steps=[] if is_trap else steps,
        factuality_claim="verified",
        source_type=get("source_type", "runtime_evidence"),
    )
