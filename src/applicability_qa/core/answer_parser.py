from __future__ import annotations

from datetime import date
from typing import Any

from .unit_utils import close_to, convert_value


def evaluate_answer(prediction: dict, gold: dict, domain: str) -> dict:
    answer = prediction.get("answer") or {}
    value = answer.get("final_value")
    unit = answer.get("final_unit")
    output_type = gold["output_type"]
    result: dict[str, Any] = {"correct": False, "parsed": value is not None, "predicted_value": value, "gold_value": gold["value"], "unit_correct": None, "error_type": None}
    if value is None:
        result["error_type"] = "missing_final_value"
        return result
    try:
        if output_type in {"decimal", "integer", "telecom_quantity"}:
            converted, ambiguous = convert_value(float(value), unit, gold.get("unit"))
            result["unit_correct"] = converted is not None and not ambiguous
            result["correct"] = close_to(converted, float(gold["value"]))
        elif output_type == "date":
            result["correct"] = date.fromisoformat(str(value)) == date.fromisoformat(str(gold["value"]))
        elif output_type == "categorical":
            result["correct"] = str(value).strip().casefold() == str(gold["value"]).strip().casefold()
        else:
            raise ValueError(f"Unsupported output type: {output_type}")
    except (TypeError, ValueError):
        result["error_type"] = "parse_error"
        return result
    if not result["correct"]:
        result["error_type"] = "wrong_answer"
    return result
