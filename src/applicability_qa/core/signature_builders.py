from __future__ import annotations

from typing import Any

from .signatures import EvidenceSignature, QuantityRequirement, RequirementSignature


def requirement_from_formula(spec: Any) -> RequirementSignature:
    inputs = getattr(spec, "required_variables", None) or getattr(spec, "required_entities", [])
    return RequirementSignature(
        target_quantity=spec.output.quantity,
        target_unit=spec.output.canonical_unit,
        required_inputs=[QuantityRequirement(name=row.name, quantity=getattr(row, "quantity", row.name), canonical_unit=row.canonical_unit, aliases=row.accepted_aliases) for row in inputs],
        approximation_policy="unspecified",
        formula_family_candidates=[getattr(spec, "formula_id", None) or getattr(spec, "calculator_id")],
    )


def evidence_signatures_from_extraction(evidence_ids: list[str], variables: dict[str, Any]) -> list[EvidenceSignature]:
    # Extracted variables are a claim-level signature. Attribution to individual
    # passages remains explicit by duplicating the claim signature per accepted ID.
    ids = evidence_ids or ["runtime_question"]
    return [EvidenceSignature(evidence_id=evidence_id, variables=list(variables), facts=variables, source_type="independently_extracted_runtime_context") for evidence_id in ids]
