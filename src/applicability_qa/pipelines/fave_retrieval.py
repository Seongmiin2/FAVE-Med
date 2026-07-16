from __future__ import annotations

from ..core.schemas import RuntimeEvidence, RuntimeQuestion
from ..domains.telecom.validity_checker import classify_evidence
from ..retrieval import BM25Retriever, load_corpus
from .common import SYSTEM, merge_usage, normalize


def run_fave_retrieval(item, provider, config):
    corpus = load_corpus(config["retrieval"]["corpus_path"])
    top_k = config["retrieval"].get("top_k", 5)
    retrieved = BM25Retriever(corpus).retrieve(item.question, top_k)
    runtime_evidence = [RuntimeEvidence(id=row.evidence_id, text=row.text) for row in retrieved]
    runtime = RuntimeQuestion(id=item.id, domain=item.domain, question=item.question, requested_output=item.requested_output, evidence=runtime_evidence, metadata=item.metadata)
    classification = classify_evidence(runtime, runtime_evidence, provider)
    accepted = {row.evidence_id for row in classification.decisions if row.label == "valid"}
    text = "\n".join(f"- {row.evidence_id}: {row.text}" for row in retrieved if row.evidence_id in accepted)
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nApplicable retrieved evidence:\n{text}")
    raw["usage"] = merge_usage(classification.usage, raw.get("usage", {}))
    raw.update(accepted_evidence_ids=sorted(accepted), rejected_evidence_ids=[row.evidence_id for row in classification.decisions if row.label == "rejected"])
    result = normalize(item, "fave_retrieval", raw)
    result.update(track="retrieval", retrieval={"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in retrieved]}, evidence_decisions=[row.model_dump() for row in classification.decisions])
    return result
