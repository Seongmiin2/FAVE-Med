from __future__ import annotations

from .signatures import EvidenceSignature


SCHEMA = {
    "type": "object",
    "properties": {
        "asserted_formula_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "variable_units": {"type": "object", "additionalProperties": {"type": "string"}},
        "convention_tags": {"type": "array", "items": {"type": "string"}},
        "procedural_steps": {"type": "array", "items": {"type": "string"}},
        "facts": {"type": "object", "additionalProperties": True},
    },
    "required": ["asserted_formula_id", "variable_units", "convention_tags", "procedural_steps", "facts"],
    "additionalProperties": False,
}


def parse_evidence_with_model(question: str, patient_context: str | None, evidence_id: str, evidence_text: str, provider) -> EvidenceSignature:
    system = "Extract a typed evidence signature from text only. Do not infer from IDs, provenance, labels, metadata, or expected answers. Return only the requested JSON."
    user = f"Question:\n{question}\n\nPatient context:\n{patient_context or ''}\n\nEvidence text:\n{evidence_text}"
    raw = provider.generate_json(system, user, schema=SCHEMA)
    return EvidenceSignature(
        evidence_id=evidence_id,
        asserted_formula_id=raw.get("asserted_formula_id"),
        variable_units=raw.get("variable_units", {}),
        variables=list(raw.get("variable_units", {})),
        convention_tags=raw.get("convention_tags", []),
        procedural_steps=raw.get("procedural_steps", []),
        facts=raw.get("facts", {}),
        factuality_claim="unverified",
        source_type="text_only_model_parser",
    )
