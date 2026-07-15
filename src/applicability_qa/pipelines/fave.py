from ..domains.telecom.validity_checker import select_evidence
from .common import SYSTEM, context, normalize


def run_fave(item, provider, config):
    accepted, rejected = select_evidence(item, provider)
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nApplicable evidence:\n{context(item, accepted)}")
    raw.update(accepted_evidence_ids=accepted, rejected_evidence_ids=rejected)
    return normalize(item, "fave", raw)
