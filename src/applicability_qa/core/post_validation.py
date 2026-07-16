from __future__ import annotations

import math
from typing import Any

from .signatures import PostValidationResult


def validate_execution(value: Any, unit: str | None, expected_unit: str, minimum: float | None = None, maximum: float | None = None) -> PostValidationResult:
    checks, errors = [], []
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        errors.append("non_finite_or_non_numeric_value")
    else:
        checks.append("finite_numeric_value")
        if minimum is not None and value < minimum:
            errors.append("below_minimum")
        if maximum is not None and value > maximum:
            errors.append("above_maximum")
    if unit != expected_unit:
        errors.append("output_unit_mismatch")
    else:
        checks.append("output_unit_match")
    return PostValidationResult(passed=not errors, checks=checks, errors=errors)
