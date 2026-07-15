from ..domains.telecom.formula_executor import execute
from .common import SYSTEM, context, normalize


def run_demo_multi_executor(item, provider, config):
    raw = provider.generate_json(
        SYSTEM,
        f"Question: {item.question}\nContext:\n{context(item)}\n"
        "Extract variables and verify units and conditions. Do not perform arithmetic.",
    )
    try:
        value, unit = execute(item.formula.id, raw.get("extracted_variables", {}))
        raw["answer"] = {"final_value": value, "final_unit": unit}
        raw["execution"] = {"mode": "python", "success": True, "error": None}
    except Exception as exc:
        raw.update(
            answer={"final_value": None, "final_unit": None},
            abstain=True,
            abstain_reason="formula_execution_failed",
            execution={"mode": "python", "success": False, "error": str(exc)},
        )
    return normalize(item, "demo_multi_executor", raw)
