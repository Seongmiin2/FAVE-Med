from __future__ import annotations

from ...core.schemas import BenchmarkItem


def select_evidence(item: BenchmarkItem, provider=None) -> tuple[list[str], list[str]]:
    if provider is None:
        return ([e.id for e in item.evidence if e.label == "valid"], [e.id for e in item.evidence if e.label == "invalid"])
    prompt = "\n".join(f"{e.id}: {e.text}" for e in item.evidence)
    result = provider.generate_json(
        "Classify evidence applicability. Return one JSON object containing "
        "accepted_evidence_ids and rejected_evidence_ids as arrays of evidence ID strings.",
        prompt,
    )
    return result.get("accepted_evidence_ids", []), result.get("rejected_evidence_ids", [])
