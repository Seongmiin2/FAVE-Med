from ..domains.telecom.validity_checker import classify_evidence, runtime_from_item
from .common import SYSTEM, context, merge_usage, normalize


def run_fave(item, provider, config):
    runtime = runtime_from_item(item)
    classification = classify_evidence(runtime, runtime.evidence, provider, strict=config.get("runtime", {}).get("strict_structured_output", False))
    accepted = [row.evidence_id for row in classification.decisions if row.label == "valid"]
    rejected = [row.evidence_id for row in classification.decisions if row.label == "rejected"]
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nApplicable evidence:\n{context(item, accepted)}")
    raw["usage"] = merge_usage(classification.usage, raw.get("usage", {}))
    raw.update(accepted_evidence_ids=accepted, rejected_evidence_ids=rejected)
    result = normalize(item, "fave", raw)
    result["evidence_decisions"] = [row.model_dump() for row in classification.decisions]
    return result
