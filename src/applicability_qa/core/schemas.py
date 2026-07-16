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


class FormulaVariableSpec(BaseModel):
    name: str
    quantity: str
    canonical_unit: str
    accepted_aliases: list[str] = Field(default_factory=list)


class FormulaOutputSpec(BaseModel):
    quantity: str
    canonical_unit: str


class TelecomFormulaSpec(BaseModel):
    formula_id: str
    name: str
    expression: str
    description: str
    required_variables: list[FormulaVariableSpec]
    output: FormulaOutputSpec
    applicability_conditions: list[str] = Field(default_factory=list)
    unsupported_conditions: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    executor_name: str


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


class MedicalRuntimeQuestion(BaseModel):
    id: str
    domain: Literal["medical"] = "medical"
    patient_note: str
    question: str
    requested_output: str | None = None
    evidence: list[RuntimeEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MedicalGoldAnnotation(BaseModel):
    answer: GoldAnswer
    calculator_id: str
    required_entities: dict[str, Any] = Field(default_factory=dict)
    required_units: dict[str, str] = Field(default_factory=dict)
    tolerance: dict[str, float | None] = Field(default_factory=dict)
    applicability_conditions: list[str] = Field(default_factory=list)
    evidence_annotations: list[EvidenceAnnotation] = Field(default_factory=list)


class MedicalBenchmarkRecord(BaseModel):
    schema_version: str = "0.3"
    source: dict[str, Any] = Field(default_factory=dict)
    runtime: MedicalRuntimeQuestion
    gold: MedicalGoldAnnotation


class CalculatorEntitySpec(BaseModel):
    name: str
    canonical_unit: str
    accepted_aliases: list[str] = Field(default_factory=list)


class MedicalCalculatorSpec(BaseModel):
    calculator_id: str
    name: str
    description: str
    expression: str
    required_entities: list[CalculatorEntitySpec]
    applicability_conditions: list[str] = Field(default_factory=list)
    unsupported_conditions: list[str] = Field(default_factory=list)
    output: FormulaOutputSpec
    aliases: list[str] = Field(default_factory=list)
    executor_name: str


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


class RetrievedEvidence(BaseModel):
    evidence_id: str
    text: str
    score: float
    rank: int
    source_id: str
    source_type: str


class RetrievalRecord(BaseModel):
    query: str
    top_k: int
    results: list[RetrievedEvidence] = Field(default_factory=list)


class FormulaSelectionRecord(BaseModel):
    predicted_formula_id: str | None = None
    candidate_formula_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""
    abstain: bool = False
    abstain_reason: str | None = None


class RunRecord(BaseModel):
    id: str
    experiment_id: str
    domain: Literal["telecom", "medical"]
    method: str
    model: str | None = None
    prompt_version: str
    schema_version: str = "0.3"
    evaluator_version: str = "v2"
    formula_mode: Literal["none", "oracle", "predicted"] = "none"
    is_primary_result: bool = True
    answer: dict[str, Any] = Field(default_factory=lambda: {"final_value": None, "final_unit": None})
    abstain: bool = False
    abstain_reason: str | None = None
    retrieval: RetrievalRecord | None = None
    evidence_decisions: list[EvidenceDecision] = Field(default_factory=list)
    formula_selection: FormulaSelectionRecord | None = None
    extracted_variables: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    raw_response: dict[str, Any] = Field(default_factory=dict)
    accepted_evidence_ids: list[str] = Field(default_factory=list)
    rejected_evidence_ids: list[str] = Field(default_factory=list)
