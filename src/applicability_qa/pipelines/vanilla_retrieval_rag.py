from __future__ import annotations

from ..retrieval import BM25Retriever, load_corpus
from .common import SYSTEM, normalize


def run_vanilla_retrieval_rag(item, provider, config):
    corpus = load_corpus(config["retrieval"]["corpus_path"])
    top_k = config["retrieval"].get("top_k", 5)
    retrieved = BM25Retriever(corpus).retrieve(item.question, top_k)
    text = "\n".join(f"- {row.evidence_id}: {row.text}" for row in retrieved)
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nRetrieved evidence:\n{text}")
    result = normalize(item, "vanilla_retrieval_rag", raw)
    result.update(track="retrieval", retrieval={"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in retrieved]})
    return result
