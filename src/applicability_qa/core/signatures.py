from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class QuantityRequirement(BaseModel):
    name: str
    quantity: str
    canonical_unit: str
    required: bool = True
    aliases: list[str] = Field(default_factory=list)


class ConditionPredicate(BaseModel):
    field: str
    operator: Literal["eq", "ne", "lt", "le", "gt", "ge", "in", "not_in", "exists"]
    value: Any = None
    blocking: bool = True
    description: str = ""


class RequirementSignature(BaseModel):
    target_quantity: str
    target_unit: str
    required_inputs: list[QuantityRequirement] = Field(default_factory=list)
    conditions: list[ConditionPredicate] = Field(default_factory=list)
    convention: str | None = None
    approximation_policy: Literal["exact", "allowed", "required", "unspecified"] = "unspecified"
    physical_constraints: list[ConditionPredicate] = Field(default_factory=list)


class EvidenceSignature(BaseModel):
    evidence_id: str
    quantities: dict[str, str] = Field(default_factory=dict)
    variables: list[str] = Field(default_factory=list)
    facts: dict[str, Any] = Field(default_factory=dict)
    conditions: list[ConditionPredicate] = Field(default_factory=list)
    convention: str | None = None
    approximation: bool | None = None
    source_type: str = "unknown"


class CompatibilityCheck(BaseModel):
    check_type: Literal[
        "unit", "variable_binding", "condition", "convention",
        "approximation", "physical_constraint", "variable_coverage",
    ]
    passed: bool
    blocking: bool = True
    code: str
    message: str
    evidence_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class TypedApplicabilityDecision(BaseModel):
    evidence_id: str
    applicable: bool
    checks: list[CompatibilityCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SolutionPlan(BaseModel):
    executor_id: str
    ordered_inputs: list[str] = Field(default_factory=list)
    accepted_evidence_ids: list[str] = Field(default_factory=list)
    rejected_evidence_ids: list[str] = Field(default_factory=list)
    output_quantity: str
    output_unit: str


class ExecutionGate(BaseModel):
    allowed: bool
    blocking_codes: list[str] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)
    reason: str


class PostValidationResult(BaseModel):
    passed: bool
    checks: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
