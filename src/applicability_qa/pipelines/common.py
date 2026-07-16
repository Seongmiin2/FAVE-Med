from __future__ import annotations

from ..core.schemas import BenchmarkItem


SYSTEM = "Return one JSON object with answer.final_value and answer.final_unit. Never substitute an intermediate value for final_value."


def merge_usage(*records: dict) -> dict:
    keys = ("input_tokens", "output_tokens", "latency_seconds")
    merged = {key: sum(float(record.get(key, 0) or 0) for record in records) for key in keys}
    merged["input_tokens"] = int(merged["input_tokens"])
    merged["output_tokens"] = int(merged["output_tokens"])
    merged["total_calls"] = sum(int(record.get("total_calls", 1 if record else 0)) for record in records)
    return merged


def context(item: BenchmarkItem, ids: list[str] | None = None) -> str:
    chosen = item.evidence if ids is None else [e for e in item.evidence if e.id in ids]
    return "\n".join(f"- {e.id}: {e.text}" for e in chosen)


def normalize(item: BenchmarkItem, method: str, raw: dict) -> dict:
    answer = raw.get("answer", raw)
    if "answer.final_value" in raw:
        answer = {
            "final_value": raw.get("answer.final_value"),
            "final_unit": raw.get("answer.final_unit"),
        }
    if "final_value" not in answer and "value" in answer:
        answer = {"final_value": answer["value"], "final_unit": answer.get("unit")}
    model = raw.pop("_model", None)
    prompt_version = raw.pop("_prompt_version", "v1")
    return {"id": item.id, "domain": item.domain, "method": method, "model": model, "prompt_version": prompt_version, "answer": {"final_value": answer.get("final_value"), "final_unit": answer.get("final_unit")}, "abstain": bool(raw.get("abstain", False)), "abstain_reason": raw.get("abstain_reason"), "accepted_evidence_ids": raw.get("accepted_evidence_ids", []), "rejected_evidence_ids": raw.get("rejected_evidence_ids", []), "extracted_variables": raw.get("extracted_variables", {}), "verification": raw.get("verification", {}), "execution": raw.get("execution", {"mode": "llm", "success": True, "error": None}), "usage": {"input_tokens": 0, "output_tokens": 0, "latency_seconds": 0.0, **raw.get("usage", {})}, "raw_response": raw}
