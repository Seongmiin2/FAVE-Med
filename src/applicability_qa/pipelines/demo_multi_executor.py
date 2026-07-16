from ..domains.telecom.formula_executor import execute
from .common import context, normalize


EXTRACTION_SYSTEM = (
    "Return one JSON object only. It must contain extracted_variables and verification. "
    "extracted_variables must use normalized numeric values without unit text. "
    "Use the variable names shown in the formula: B and C in base SI units, d in km and f in MHz "
    "when the formula explicitly uses d_km and f_MHz, plus rho, Nt, H, S, I, N, gamma_th, "
    "gamma_bar, eb_n0_db, Pt, Gt, Gr, lambda, and snr_db where applicable. "
    "Every numeric input explicitly provided by the question must appear at the top level of "
    "extracted_variables, including snr_db even when it must later be converted to snr_linear. "
    "Do not calculate or return the final answer."
)


def run_demo_multi_executor(item, provider, config):
    raw = provider.generate_json(
        EXTRACTION_SYSTEM,
        f"Formula: {item.formula.expression}\nQuestion: {item.question}\nContext:\n{context(item)}\n"
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
