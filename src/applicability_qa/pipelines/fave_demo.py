from ..domains.telecom.formula_executor import execute
from ..domains.telecom.validity_checker import select_evidence
from .common import context, normalize


EXTRACTION_SYSTEM = (
    "Return one JSON object only with extracted_variables and verification. "
    "extracted_variables must contain normalized numeric values without unit text, using the "
    "variable names in the supplied formula. Do not calculate the final answer."
)


def run_fave_demo(item, provider, config):
    accepted, rejected = select_evidence(item, provider)
    raw = provider.generate_json(
        EXTRACTION_SYSTEM,
        f"Formula: {item.formula.expression}\nQuestion: {item.question}\n"
        f"Applicable evidence:\n{context(item, accepted)}",
    )
    raw.update(accepted_evidence_ids=accepted, rejected_evidence_ids=rejected)
    try:
        value, unit = execute(item.formula.id, raw.get("extracted_variables", {}))
        raw["answer"] = {"final_value": value, "final_unit": unit}
        raw["execution"] = {"mode": "python", "success": True, "error": None}
    except Exception as exc:
        raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason=str(exc), execution={"mode": "python", "success": False, "error": str(exc)})
    return normalize(item, "fave_demo", raw)
