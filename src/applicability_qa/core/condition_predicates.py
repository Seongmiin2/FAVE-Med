from __future__ import annotations

from typing import Any

from .signatures import ConditionPredicate


def evaluate_predicate(predicate: ConditionPredicate, facts: dict[str, Any]) -> bool:
    exists = predicate.field in facts and facts[predicate.field] is not None
    if predicate.operator == "exists":
        return exists == (True if predicate.value is None else bool(predicate.value))
    if not exists:
        return False
    actual, expected = facts[predicate.field], predicate.value
    operations = {
        "eq": lambda: actual == expected,
        "ne": lambda: actual != expected,
        "lt": lambda: actual < expected,
        "le": lambda: actual <= expected,
        "gt": lambda: actual > expected,
        "ge": lambda: actual >= expected,
        "in": lambda: actual in expected,
        "not_in": lambda: actual not in expected,
    }
    try:
        return bool(operations[predicate.operator]())
    except (TypeError, ValueError):
        return False
