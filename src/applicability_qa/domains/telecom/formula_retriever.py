from __future__ import annotations

import re

TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(TOKEN.findall(text.lower()))


def retrieve_formula_candidates(query: str, registry: list, top_k: int = 3) -> list[dict]:
    query_tokens = _tokens(query)
    scored = []
    for row in registry:
        document = " ".join([row.name, row.description, row.expression, *row.aliases])
        score = len(query_tokens & _tokens(document)) / max(len(query_tokens), 1)
        scored.append({"formula_id": row.formula_id, "score": score, "formula": row})
    return sorted(scored, key=lambda row: (-row["score"], row["formula_id"]))[:top_k]
