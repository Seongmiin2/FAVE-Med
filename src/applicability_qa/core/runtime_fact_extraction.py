from __future__ import annotations

from typing import Any

from .signatures import EvidenceSignature, ObservedVariable, RuntimeFactExtraction


def validate_runtime_extraction(raw: dict[str, Any]) -> RuntimeFactExtraction:
    payload = raw.get("runtime_facts", raw)
    return RuntimeFactExtraction.model_validate(payload)


def build_execution_signature(extraction: RuntimeFactExtraction) -> EvidenceSignature:
    facts = {name: value.normalized_value for name, value in extraction.variables.items()}
    units = {name: value.normalized_unit for name, value in extraction.variables.items() if value.normalized_unit}
    return EvidenceSignature(
        evidence_id="execution_inputs",
        variables=list(extraction.variables),
        facts={**facts, **extraction.conditions},
        variable_units=units,
        asserted_formula_id=extraction.asserted_formula_id,
        convention_tags=extraction.convention_tags,
        procedural_steps=extraction.procedural_steps,
        observed_variables=extraction.variables,
        factuality_claim="unverified",
        source_type="independent_runtime_fact_extraction",
    )
