from __future__ import annotations

import json
from pathlib import Path

from ...core.schemas import (
    EvidenceClassificationResult, EvidenceDecision, RuntimeEvidence, RuntimeQuestion,
)

PROMPT_PATH = Path(__file__).resolve().parents[4] / "configs" / "prompts" / "telecom" / "applicability_v2.txt"


def classify_evidence(
    item: RuntimeQuestion,
    evidence: list[RuntimeEvidence],
    provider,
) -> EvidenceClassificationResult:
    system = PROMPT_PATH.read_text(encoding="utf-8")
    payload = {
        "question": item.question,
        "requested_output": item.requested_output,
        "explicit_information": item.metadata.get("explicit_information", []),
        "candidate_evidence": [row.model_dump() for row in evidence],
    }
    raw = provider.generate_json(system, json.dumps(payload, ensure_ascii=False))
    decisions = raw.get("decisions")
    if decisions is None:
        accepted = set(raw.get("accepted_evidence_ids", []))
        rejected = set(raw.get("rejected_evidence_ids", []))
        decisions = [
            {
                "evidence_id": row.id,
                "label": "rejected" if row.id in rejected else "valid" if row.id in accepted else "contested",
                "conflict_type": "other" if row.id in rejected else "none",
                "reason": "Legacy provider classification output",
                "required_correction": None,
                "confidence": 1.0,
            }
            for row in evidence
        ]
    by_id = {row.id for row in evidence}
    parsed = [EvidenceDecision.model_validate(row) for row in decisions]
    if {row.evidence_id for row in parsed} != by_id:
        raise ValueError("Classifier must return exactly one decision per evidence item")
    return EvidenceClassificationResult(decisions=parsed, usage=raw.get("usage", {}))


def select_evidence(item, provider=None) -> tuple[list[str], list[str]]:
    """Legacy pilot wrapper. New code should call classify_evidence()."""
    if isinstance(item, RuntimeQuestion):
        runtime = item
    else:
        runtime = RuntimeQuestion(
            id=item.id,
            domain=item.domain,
            question=item.question,
            requested_output=item.metadata.get("requested_output"),
            evidence=[RuntimeEvidence(id=row.id, text=row.text) for row in item.evidence],
            metadata={key: value for key, value in item.metadata.items() if key not in {"expected_arbitration", "invalid_evidence", "tolerance"}},
        )
    if provider is None:
        raise ValueError("A provider is required; gold evidence labels are never used for runtime selection")
    result = classify_evidence(runtime, runtime.evidence, provider)
    accepted = [row.evidence_id for row in result.decisions if row.label == "valid"]
    rejected = [row.evidence_id for row in result.decisions if row.label == "rejected"]
    return accepted, rejected
