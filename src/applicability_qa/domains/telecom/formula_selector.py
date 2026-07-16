from __future__ import annotations

from .formula_retriever import retrieve_formula_candidates


def select_formula(question: str, evidence_text: str, registry: list[dict], top_k: int = 3) -> dict:
    # Rank primarily from the question so a distractor formula in evidence cannot
    # hijack formula selection. Evidence is used downstream for extraction.
    candidates = retrieve_formula_candidates(question, registry, top_k)
    if not candidates or candidates[0]["score"] <= 0:
        return {"predicted_formula_id": None, "candidate_formula_ids": [row["formula_id"] for row in candidates], "confidence": 0.0, "reason": "No lexical formula match", "abstain": True, "abstain_reason": "formula_selection_failure"}
    top = candidates[0]
    return {"predicted_formula_id": top["formula_id"], "candidate_formula_ids": [row["formula_id"] for row in candidates], "confidence": top["score"], "reason": "Highest registry retrieval score", "abstain": False, "abstain_reason": None}
