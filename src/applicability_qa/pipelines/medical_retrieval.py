from __future__ import annotations

from ..core.schemas import MedicalRuntimeQuestion, RuntimeEvidence
from ..domains.telecom.validity_checker import classify_evidence
from ..retrieval import BM25Retriever, load_corpus
from .common import SYSTEM, merge_usage, normalize, question_prompt
from .medical_predicted_executor import run_medical_predicted_executor


def _retrieve(item, config):
    top_k = config["retrieval"].get("top_k", 5)
    rows = BM25Retriever(load_corpus(config["retrieval"]["corpus_path"])).retrieve(item.question, top_k)
    evidence = [RuntimeEvidence(id=row.evidence_id, text=row.text) for row in rows]
    runtime = MedicalRuntimeQuestion(id=item.id, patient_note=item.patient_note, question=item.question, requested_output=item.requested_output, evidence=evidence, metadata=item.metadata)
    retrieval = {"query": item.question, "top_k": top_k, "results": [row.model_dump() for row in rows]}
    return runtime, retrieval


def run_medical_vanilla_retrieval(item, provider, config):
    runtime, retrieval = _retrieve(item, config)
    evidence = "\n".join(f"- {row.id}: {row.text}" for row in runtime.evidence)
    raw = provider.generate_json(SYSTEM, f"{question_prompt(runtime)}\n\nRetrieved evidence:\n{evidence}")
    result = normalize(runtime, "medical_vanilla_retrieval", raw)
    result.update(track="retrieval", retrieval=retrieval)
    return result


def run_medical_fave_retrieval(item, provider, config):
    runtime, retrieval = _retrieve(item, config)
    classification = classify_evidence(runtime, runtime.evidence, provider, strict=config.get("runtime", {}).get("strict_structured_output", False))
    accepted = {row.evidence_id for row in classification.decisions if row.label == "valid"}
    evidence = "\n".join(f"- {row.id}: {row.text}" for row in runtime.evidence if row.id in accepted)
    raw = provider.generate_json(SYSTEM, f"{question_prompt(runtime)}\n\nApplicable evidence:\n{evidence}")
    raw["usage"] = merge_usage(classification.usage, raw.get("usage", {}))
    result = normalize(runtime, "medical_fave_retrieval", raw)
    result.update(track="retrieval", retrieval=retrieval, evidence_decisions=[row.model_dump() for row in classification.decisions], accepted_evidence_ids=sorted(accepted))
    return result


def run_medical_retrieval_predicted_executor(item, provider, config):
    runtime, retrieval = _retrieve(item, config)
    result = run_medical_predicted_executor(runtime, provider, config)
    result.update(method="medical_retrieval_predicted_executor", track="retrieval", retrieval=retrieval)
    return result


def run_medical_fave_retrieval_predicted_executor(item, provider, config):
    runtime, retrieval = _retrieve(item, config)
    classification = classify_evidence(runtime, runtime.evidence, provider, strict=config.get("runtime", {}).get("strict_structured_output", False))
    accepted = {row.evidence_id for row in classification.decisions if row.label == "valid"}
    filtered = MedicalRuntimeQuestion(id=runtime.id, patient_note=runtime.patient_note, question=runtime.question, requested_output=runtime.requested_output, evidence=[row for row in runtime.evidence if row.id in accepted], metadata=runtime.metadata)
    result = run_medical_predicted_executor(filtered, provider, config)
    result.update(method="medical_fave_retrieval_predicted_executor", track="retrieval", retrieval=retrieval, evidence_decisions=[row.model_dump() for row in classification.decisions], accepted_evidence_ids=sorted(accepted))
    return result
