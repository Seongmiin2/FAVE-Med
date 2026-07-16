from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class GoldAnswer(BaseModel):
    value: Any
    unit: str | None = None
    output_type: Literal["decimal", "integer", "date", "categorical", "telecom_quantity"]


class FormulaSpec(BaseModel):
    id: str
    expression: str | None = None


class EvidenceItem(BaseModel):
    id: str
    text: str
    label: Literal["valid", "invalid", "unknown"] = "unknown"
    invalidity_type: str | None = None


class BenchmarkItem(BaseModel):
    id: str
    domain: Literal["telecom", "medical"]
    task_type: str
    question: str
    gold_answer: GoldAnswer
    formula: FormulaSpec | None = None
    required_variables: dict[str, Any] = Field(default_factory=dict)
    required_conditions: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


ConflictType = Literal[
    "none", "unit_compatibility", "condition_mismatch", "variable_binding",
    "formula_convention", "approximation_misuse", "physical_constraint",
    "solution_step_corruption", "insufficient_context", "other",
]


class RuntimeEvidence(BaseModel):
    id: str
    text: str


class RuntimeQuestion(BaseModel):
    id: str
    domain: Literal["telecom", "medical"]
    question: str
    requested_output: str | None = None
    evidence: list[RuntimeEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceAnnotation(BaseModel):
    evidence_id: str
    label: Literal["valid", "contested", "rejected"]
    conflict_type: ConflictType = "none"
    rationale: str | None = None


class GoldAnnotation(BaseModel):
    answer: GoldAnswer
    formula_id: str
    formula_expression: str | None = None
    required_variables: dict[str, Any] = Field(default_factory=dict)
    required_units: dict[str, str] = Field(default_factory=dict)
    evidence_annotations: list[EvidenceAnnotation] = Field(default_factory=list)
    tolerance: dict[str, float | None] = Field(default_factory=dict)
    trap_answers: list[dict[str, Any]] = Field(default_factory=list)


class BenchmarkRecord(BaseModel):
    schema_version: str = "0.3"
    source: dict[str, Any] = Field(default_factory=dict)
    runtime: RuntimeQuestion
    gold: GoldAnnotation


class EvidenceDecision(BaseModel):
    evidence_id: str
    label: Literal["valid", "contested", "rejected"]
    conflict_type: ConflictType = "none"
    reason: str
    required_correction: str | None = None
    confidence: float = Field(ge=0, le=1)


class EvidenceClassificationResult(BaseModel):
    decisions: list[EvidenceDecision]
    usage: dict[str, Any] = Field(default_factory=dict)
