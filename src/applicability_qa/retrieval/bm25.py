from __future__ import annotations

import math
import re
from collections import Counter

from ..core.schemas import RetrievedEvidence

TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class BM25Retriever:
    def __init__(self, corpus: list[dict], k1: float = 1.5, b: float = 0.75):
        self.corpus, self.k1, self.b = corpus, k1, b
        self.tokens = [tokenize(row["text"]) for row in corpus]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.avgdl = sum(self.lengths) / max(len(self.lengths), 1)
        self.df = Counter(token for tokens in self.tokens for token in set(tokens))

    def retrieve(self, query: str, k: int) -> list[RetrievedEvidence]:
        query_terms = tokenize(query)
        scored = []
        total = len(self.corpus)
        for index, tokens in enumerate(self.tokens):
            tf = Counter(tokens)
            score = 0.0
            for term in query_terms:
                frequency = tf[term]
                if not frequency:
                    continue
                idf = math.log(1 + (total - self.df[term] + 0.5) / (self.df[term] + 0.5))
                denominator = frequency + self.k1 * (1 - self.b + self.b * self.lengths[index] / max(self.avgdl, 1))
                score += idf * frequency * (self.k1 + 1) / denominator
            scored.append((score, index))
        results = []
        for rank, (score, index) in enumerate(sorted(scored, key=lambda pair: (-pair[0], pair[1]))[:k], 1):
            row = self.corpus[index]
            results.append(RetrievedEvidence(evidence_id=row["evidence_id"], text=row["text"], score=score, rank=rank, source_id=row["source_id"], source_type=row["source_type"]))
        return results
