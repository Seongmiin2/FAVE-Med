from __future__ import annotations

from ..core.schemas import RuntimeEvidence, RuntimeQuestion
from ..retrieval import BM25Retriever, load_corpus
from .fave_predicted_executor import run_fave_predicted_executor


def run_fave_retrieval_predicted_executor(item, provider, config):
    corpus = load_corpus(config["retrieval"]["corpus_path"])
    top_k = config["retrieval"].get("top_k", 5)
    retrieved = BM25Retriever(corpus).retrieve(item.question, top_k)
    runtime = RuntimeQuestion(
        id=item.id, domain=item.domain, question=item.question, requested_output=item.requested_output,
        evidence=[RuntimeEvidence(id=row.evidence_id, text=row.text) for row in retrieved], metadata=item.metadata,
    )
    result = run_fave_predicted_executor(runtime, provider, config)
    result.update(
        method="fave_retrieval_predicted_executor",
        track="retrieval",
        retrieval={"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in retrieved]},
    )
    return result
