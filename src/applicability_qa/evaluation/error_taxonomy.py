from __future__ import annotations

ERROR_TYPES = {
    "retrieval_failure", "evidence_classification_failure", "formula_retrieval_failure",
    "formula_selection_failure", "entity_extraction_failure", "variable_extraction_failure",
    "unit_normalization_failure", "condition_verification_failure", "executor_failure",
    "answer_format_failure", "classifier_parse_failure", "selector_parse_failure",
    "formula_selector_parse_failure", "variable_extractor_parse_failure", "unsupported_rule",
    "unsupported_formula", "wrong_abstention", "missing_abstention", "other",
    "requirement_signature_failure", "evidence_signature_failure",
    "typed_execution_gate", "post_validation_failure",
}


def primary_error(prediction: dict, *, correct: bool, parsed: bool, formula_correct: bool | None, retrieval_hit: bool | None) -> str | None:
    if correct:
        return None
    reason = prediction.get("abstain_reason")
    aliases = {
        "pipeline_error": "other", "formula_execution_failed": "executor_failure",
        "formula_selection_failure": "formula_selection_failure",
    }
    if reason in ERROR_TYPES:
        return reason
    if reason in aliases:
        return aliases[reason]
    if retrieval_hit is False:
        return "retrieval_failure"
    if formula_correct is False:
        return "formula_selection_failure"
    if prediction.get("execution", {}).get("success") is False:
        error = str(prediction.get("execution", {}).get("error", "")).lower()
        return "unsupported_formula" if "unsupported" in error else "executor_failure"
    if not parsed:
        return "answer_format_failure"
    if prediction.get("verification", {}).get("unit_check") == "fail":
        return "unit_normalization_failure"
    if prediction.get("verification", {}).get("condition_check") == "fail":
        return "condition_verification_failure"
    return "other"
