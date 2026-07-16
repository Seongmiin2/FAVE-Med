from __future__ import annotations

from .formula_retriever import retrieve_formula_candidates
from ...core.errors import StructuredOutputError
from ...core.schemas import FormulaSelectionRecord


def validate_formula_selection(raw: dict) -> dict:
    try:
        parsed = FormulaSelectionRecord.model_validate(raw)
    except Exception as exc:
        raise StructuredOutputError("formula_selector_parse_failure", f"Invalid formula selection schema: {exc}") from exc
    if not parsed.abstain and not parsed.predicted_formula_id:
        raise StructuredOutputError("formula_selector_parse_failure", "Non-abstaining selection requires predicted_formula_id")
    if parsed.predicted_formula_id and parsed.predicted_formula_id not in parsed.candidate_formula_ids:
        raise StructuredOutputError("formula_selector_parse_failure", "Predicted formula must occur in candidate list")
    return parsed.model_dump()


def select_formula(question: str, evidence_text: str, registry: list[dict], top_k: int = 3) -> dict:
    # Rank primarily from the question so a distractor formula in evidence cannot
    # hijack formula selection. Evidence is used downstream for extraction.
    candidates = retrieve_formula_candidates(question, registry, top_k)
    if not candidates or candidates[0]["score"] <= 0:
        return validate_formula_selection({"predicted_formula_id": None, "candidate_formula_ids": [row["formula_id"] for row in candidates], "confidence": 0.0, "reason": "No lexical formula match", "abstain": True, "abstain_reason": "formula_selection_failure"})
    top = candidates[0]
    return validate_formula_selection({"predicted_formula_id": top["formula_id"], "candidate_formula_ids": [row["formula_id"] for row in candidates], "confidence": top["score"], "reason": "Highest registry retrieval score", "abstain": False, "abstain_reason": None})
