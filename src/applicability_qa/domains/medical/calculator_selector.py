from __future__ import annotations

import re

TOKEN = re.compile(r"[a-z0-9]+")


def select_calculator(question: str, registry: list, top_k: int = 3) -> dict:
    query = set(TOKEN.findall(question.lower()))
    scored = []
    for row in registry:
        document = " ".join([row.name, row.description, row.expression, *row.aliases])
        overlap = len(query & set(TOKEN.findall(document.lower()))) / max(1, len(query))
        normalized_question = " ".join(TOKEN.findall(question.lower()))
        phrases = [row.name, *row.aliases]
        phrase_bonus = max((2.0 for phrase in phrases if " ".join(TOKEN.findall(phrase.lower())) in normalized_question), default=0.0)
        score = overlap + phrase_bonus
        scored.append((score, row.calculator_id))
    candidates = [item[1] for item in sorted(scored, key=lambda item: (-item[0], item[1]))[:top_k]]
    best = max(scored, default=(0, None))
    if best[0] <= 0:
        return {"predicted_formula_id": None, "candidate_formula_ids": candidates, "confidence": 0.0, "reason": "No calculator match", "abstain": True, "abstain_reason": "formula_selection_failure"}
    return {"predicted_formula_id": candidates[0], "candidate_formula_ids": candidates, "confidence": best[0], "reason": "Highest registry retrieval score", "abstain": False, "abstain_reason": None}
