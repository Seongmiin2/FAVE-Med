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
