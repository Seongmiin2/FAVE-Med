from ..domains.telecom.formula_executor import execute
from ..domains.telecom.validity_checker import select_evidence
from .common import SYSTEM, context, normalize


def run_fave_demo(item, provider, config):
    accepted, rejected = select_evidence(item, provider)
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nApplicable evidence:\n{context(item, accepted)}\nReturn extracted_variables and verification.")
    raw.update(accepted_evidence_ids=accepted, rejected_evidence_ids=rejected)
    try:
        value, unit = execute(item.formula.id, raw.get("extracted_variables", {}))
        raw["answer"] = {"final_value": value, "final_unit": unit}
        raw["execution"] = {"mode": "python", "success": True, "error": None}
    except Exception as exc:
        raw.update(answer={"final_value": None, "final_unit": None}, abstain=True, abstain_reason=str(exc), execution={"mode": "python", "success": False, "error": str(exc)})
    return normalize(item, "fave_demo", raw)
