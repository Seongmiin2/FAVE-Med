from __future__ import annotations

from .signatures import ExecutionGate, TypedApplicabilityDecision


def build_execution_gate(decisions: list[TypedApplicabilityDecision]) -> ExecutionGate:
    checks = [check for decision in decisions for check in decision.checks]
    blocking = sorted({check.code for check in checks if not check.passed and check.blocking})
    warnings = sorted({check.code for check in checks if not check.passed and not check.blocking})
    allowed = bool(decisions) and any(item.applicable for item in decisions) and not blocking
    return ExecutionGate(allowed=allowed, blocking_codes=blocking, warning_codes=warnings, reason="typed checks passed" if allowed else "execution blocked by typed applicability checks")
